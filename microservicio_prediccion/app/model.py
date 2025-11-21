# microservicio_prediccion/app/model.py
import joblib
import pandas as pd
from datetime import timedelta
import os
from sqlalchemy import text
from .config import engine

# --- Carga de Activos (se ejecuta UNA VEZ al iniciar el servidor) ---
print("Cargando activos de predicción...")
modelo = None
df_historico = None

def cargar_datos_historicos_desde_db():
    """
    Carga los datos históricos de ventas desde la base de datos.
    Consulta la tabla ecommerce_detallepedido y agrupa por fecha.
    """
    try:
        if engine is None:
            raise Exception("Motor de base de datos no disponible")
        
        # Consulta SQL para obtener datos históricos de ventas
        query = text("""
            SELECT 
                DATE(p.fecha_creacion) as fecha_pedido,
                SUM(dp.cantidad * dp.precio_unitario) as total_ventas
            FROM pedidos_detallepedido AS dp
            JOIN pedidos_pedido AS p ON dp.pedido_id = p.id
            WHERE p.estado IN ('pagado', 'enviado', 'entregado')
            GROUP BY DATE(p.fecha_creacion)
            ORDER BY fecha_pedido
        """)
        
        # Ejecutar consulta y convertir a DataFrame
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("⚠️  ADVERTENCIA: No hay datos históricos en la base de datos. Usando datos de Excel como respaldo.")
            return None
        
        # Convertir a formato de serie temporal
        df['fecha_pedido'] = pd.to_datetime(df['fecha_pedido'])
        df = df.set_index('fecha_pedido')
        
        # Rellenar fechas faltantes con 0
        df = df.resample('D').sum().fillna(0)
        df = df.rename(columns={'total_ventas': 'total_ventas'})
        
        print(f"✅ Datos históricos cargados desde BD: {len(df)} días, desde {df.index.min()} hasta {df.index.max()}")
        return df
        
    except Exception as e:
        print(f"❌ Error al cargar datos desde BD: {e}")
        return None

try:
    # 1. Cargar el modelo
    MODEL_PATH = 'modelo/modelo_random_forest.pkl'
    modelo = joblib.load(MODEL_PATH)
    print(f"✅ Modelo cargado exitosamente desde {MODEL_PATH}")
    
    # 2. Intentar cargar datos históricos desde la base de datos
    df_historico = cargar_datos_historicos_desde_db()
    
    # 3. Si falla, usar Excel como respaldo
    if df_historico is None or df_historico.empty:
        print("📁 Intentando cargar datos desde archivo Excel de respaldo...")
        DATA_PATH = 'notebooks/dataset_ventas.xlsx'
        
        df_trans = pd.read_excel(DATA_PATH)
        df_trans['InvoiceDate'] = pd.to_datetime(df_trans['InvoiceDate'])
        df_trans['TotalVenta'] = df_trans['Quantity'] * df_trans['Price']
        df_historico = df_trans.set_index('InvoiceDate')['TotalVenta'].resample('D').sum().fillna(0)
        df_historico = df_historico.to_frame(name='total_ventas')
        
        print(f"✅ Datos históricos cargados desde Excel ({len(df_historico)} días)")

except FileNotFoundError as e:
    print(f"❌ ERROR CRÍTICO: No se encontró el archivo {e.filename}")
    print("Asegúrate de que 'modelo/modelo_random_forest.pkl' exista.")
except Exception as e:
    print(f"❌ ERROR CRÍTICO AL CARGAR ACTIVOS: {e}")


# --- Función de Features (IDÉNTICA al notebook) ---
def crear_features(df):
    """Crea características de series de tiempo a partir de un índice de fecha."""
    df_copy = df.copy()
    df_copy['dia_del_mes'] = df_copy.index.day
    df_copy['dia_de_la_semana'] = df_copy.index.dayofweek
    df_copy['mes'] = df_copy.index.month
    df_copy['anio'] = df_copy.index.year
    df_copy['trimestre'] = df_copy.index.quarter
    
    # Se calculan los lags/rolling basados en los datos pasados
    df_copy['ventas_dia_anterior'] = df_copy['total_ventas'].shift(1)
    df_copy['media_ventas_7_dias'] = df_copy['total_ventas'].shift(1).rolling(window=7).mean()
    
    return df_copy


# --- Función de Predicción (El "cerebro" en vivo) ---
def generar_predicciones(dias_a_predecir: int) -> list:
    """
    Genera predicciones futuras día por día (auto-regresivo).
    """
    if modelo is None or df_historico is None:
        raise Exception("Los activos (modelo o datos históricos) no están cargados.")
    
    # Tomamos el historial más reciente (necesitamos al menos 7 días para el 'rolling')
    historial_reciente = df_historico.iloc[-7:].copy()
    
    predicciones_lista = []
    
    for i in range(1, dias_a_predecir + 1):
        # 1. Crear la nueva fecha a predecir
        # (Usamos el índice del último elemento del 'historial_reciente')
        ultima_fecha_conocida = historial_reciente.index.max()
        nueva_fecha = ultima_fecha_conocida + timedelta(days=1)
        
        # 2. Crear una fila temporal para esta fecha
        fila_nueva = pd.DataFrame(index=[nueva_fecha], data={'total_ventas': [0]})
        
        # 3. Juntar el historial reciente + la fila nueva
        datos_loop = pd.concat([historial_reciente, fila_nueva])
        
        # 4. Crear features para este conjunto de datos
        df_con_features = crear_features(datos_loop)
        
        # 5. Tomar solo la última fila (la que queremos predecir)
        features_dia_nuevo = df_con_features.iloc[-1:]
        
        # 6. Llenar NaNs (crucial)
        # Los 'lags' y 'rolling' del primer día de predicción
        # se llenan con los últimos datos reales.
        features_dia_nuevo = features_dia_nuevo.fillna(method='ffill')
        
        # 7. Preparar X (las features)
        FEATURES = [col for col in features_dia_nuevo.columns if col != 'total_ventas']
        X_pred = features_dia_nuevo[FEATURES]
        
        # 8. ¡Predecir!
        prediccion_dia = modelo.predict(X_pred)[0]
        prediccion_dia = max(0, prediccion_dia) # No predecir ventas negativas
        
        # 9. Guardar el resultado
        predicciones_lista.append({
            "fecha": nueva_fecha.strftime('%Y-%m-%d'),
            "prediccion_venta": round(prediccion_dia, 2)
        })
        
        # 10. ¡Actualizar el historial!
        # Añadimos la predicción al 'historial_reciente' para que
        # el próximo loop la use para calcular el 'lag' y 'rolling'.
        fila_predicha = pd.DataFrame(index=[nueva_fecha], data={'total_ventas': [prediccion_dia]})
        historial_reciente = pd.concat([historial_reciente, fila_predicha])
        
        # Mantenemos solo los últimos 7 días para eficiencia
        historial_reciente = historial_reciente.iloc[-7:]

    return predicciones_lista