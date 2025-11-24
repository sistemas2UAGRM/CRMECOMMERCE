from fastapi import FastAPI, HTTPException
from .schemas import PredictionRequest
from . import model

app = FastAPI(
    title="Microservicio de PREDICCIÓN de Ventas",
    version="0.1.0",
)

@app.on_event("startup")
def verificar_modelo():
    # Verificación al inicio para fallar rápido si algo salió mal
    if model.modelo is None:
        print("ADVERTENCIA: El modelo de ML no está cargado. El endpoint /predecir fallará.")
    else:
        print("✅ Microservicio de predicción listo para recibir peticiones multi-tenant")

@app.get("/")
def leer_raiz():
    """
    Endpoint raíz para verificar que el servicio está en línea.
    """
    return {"mensaje": "¡Microservicio de PREDICCIÓN está en línea!"}

@app.post("/predecir")
def predecir_ventas(request: PredictionRequest):
    """
    Recibe un número de días y el schema del tenant, devuelve la predicción de ventas.
    """
    # Si el modelo no se cargó al inicio, devolvemos un error
    if model.modelo is None:
        raise HTTPException(
            status_code=503,
            detail="El servicio no está listo. El modelo no se pudo cargar."
        )
    
    try:
        tenant_schema = request.tenant_schema or "public"
        print(f"Recibida petición para predecir {request.dias_a_predecir} días para tenant '{tenant_schema}'.")
        
        # 1. Llamar a nuestra función de lógica con el tenant_schema
        predicciones = model.generar_predicciones(
            dias_a_predecir=request.dias_a_predecir,
            tenant_schema=tenant_schema
        )
        
        # 2. Devolver los resultados en formato JSON
        return {
            "tenant_schema": tenant_schema,
            "dias_solicitados": request.dias_a_predecir,
            "predicciones": predicciones
        }
        
    except Exception as e:
        print(f"Error durante la predicción para tenant '{request.tenant_schema}': {e}")
        # Captura cualquier error de la función 'generar_predicciones'
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al generar la predicción: {str(e)}"
        )
    
