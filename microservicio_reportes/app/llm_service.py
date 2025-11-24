# microservicio_reportes/app/llm_service.py
import cohere
import json
import re
from .core.config import COHERE_API_KEY
from datetime import date
from .utils.date_utils import obtener_rango_fechas

# Configura la API de Google
#genai.configure(api_key=GEMINI_API_KEY)
co = cohere.Client(COHERE_API_KEY)

def construir_preambulo_sistema(fecha_actual: str) -> str:
    """
    Preambulo detallado para interpretar prompts relacionados con reportes de E-commerce de boutique.
    """
    return f"""
    Eres un analista experto en datos de un E-commerce de moda (boutique).
    Tu tarea es transformar solicitudes en un JSON estructurado y **nada más**.
    Nunca agregues texto fuera del JSON.

    --- 🧾 ESTRUCTURA JSON ---
    {{
      "metric": "tipo_de_reporte",
      "filters": {{
         "campo": "valor"
      }},
      "period": "rango_relativo",
      "date_range": {{
         "start_date": "AAAA-MM-DD",
         "end_date": "AAAA-MM-DD"
      }},
      "granularity": "day|week|month",
      "limit": 10,
      "threshold": 10,
      "group_by": "opcional",
      "format": "json|pdf|excel"
    }}

    --- 🧭 REGLAS GENERALES ---
    - Si el usuario no especifica formato, usa "json" por defecto.
    - NO calcules fechas exactas para términos relativos. Usa el campo "period".
      - "hoy" -> "today"
      - "ayer" -> "yesterday"
      - "esta semana" -> "this_week"
      - "semana pasada" -> "last_week"
      - "este mes" -> "this_month"
      - "mes pasado" -> "last_month"
      - "este año" -> "this_year"
      - "año pasado" -> "last_year"
    - Si el usuario da fechas específicas (ej: "del 1 al 15 de octubre"), usa "period": "custom" y llena "date_range".
    - Si pide "ventas diarias", "por día" -> "granularity": "day"
    - Si pide "ventas semanales" -> "granularity": "week"
    - Si pide "ventas mensuales" -> "granularity": "month"
    - Si pide "top X productos" -> "limit": X
    - Si pide "stock menor a X" -> "threshold": X
    - El resultado debe ser SIEMPRE un JSON válido sin texto adicional.

    --- 📊 MÉTRICAS DISPONIBLES ---
    🔸 **Ventas** (requieren date_range)
    - ventas_totales, cantidad_pedidos, ticket_promedio
    - ventas_por_categoria, productos_mas_vendidos

    🔸 **Finanzas** (requieren date_range)
    - ingresos_brutos, ingresos_netos, devoluciones

    🔸 **Inventario** (NO requieren date_range - son snapshots actuales)
    - stock_actual, inventario_por_categoria, inventario_bajo

    🔸 **Clientes**
    - todos_clientes, lista_clientes, clientes_sistema (NO requieren date_range - lista todos)
    - clientes_nuevos, clientes_frecuentes (requieren date_range)

    🔸 **Logística** (requieren date_range)
    - pedidos_pendientes, pedidos_enviados, pedidos_entregados

    --- ⚠️ IMPORTANTE: DATE_RANGE ---
    - Métricas de inventario (stock_actual, inventario_bajo, inventario_por_categoria): NO requieren date_range
    - Métricas de lista de clientes (todos_clientes, lista_clientes, clientes_sistema): NO requieren date_range
    - Para estas métricas, omite el campo "date_range" o déjalo vacío
    - Todas las demás métricas SÍ requieren date_range

    --- ⚙️ FORMATO DE SALIDA ---
    - Si el usuario no indica formato → usa "json".
    - No devuelvas explicaciones ni texto adicional, solo el JSON.

    --- 📚 EJEMPLOS ---
    Usuario: "ventas totales del mes pasado en excel"
    {{
      "metric": "ventas_totales",
      "period": "last_month",
      "format": "excel"
    }}

    Usuario: "clientes frecuentes de este mes por sucursal"
    {{
      "metric": "clientes_frecuentes",
      "group_by": "sucursal",
      "period": "this_month",
      "format": "json"
    }}

    Usuario: "productos con stock bajo (menos de 5)"
    {{
      "metric": "inventario_bajo",
      "threshold": 5,
      "format": "json"
    }}
    """

    Usuario: "dame los clientes que tiene el sistema en pdf"
    {{
      "metric": "todos_clientes",
      "format": "pdf"
    }}

    Usuario: "inventario por categoría en excel"
    {{
      "metric": "inventario_por_categoria",
      "format": "excel"
    }}
    """


def limpiar_json(texto: str) -> str:
    """Extrae el bloque JSON del texto (incluso si hay texto adicional o código markdown)."""
    match = re.search(r"\{[\s\S]*\}", texto)
    return match.group(0) if match else "{}"


def analizar_prompt_usuario(user_prompt: str) -> dict:
    """
    Envía el prompt del usuario a Cohere y devuelve un JSON estructurado.
    Incluye manejo de errores, validación y logs.
    """
    hoy = date.today().isoformat()
    preambulo = construir_preambulo_sistema(hoy)
    print(f"\n🧠 Prompt del usuario: {user_prompt}\n")

    try:
        response = co.chat(
            message=user_prompt,
            preamble=preambulo,
            temperature=0.2,
            model="command-a-03-2025"
        )

        raw_text = response.text.strip()
        print(f"🪶 Respuesta cruda del modelo:\n{raw_text}\n")

        json_text = limpiar_json(raw_text)

        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError:
            raise ValueError("El modelo no devolvió un JSON válido.")
        
        # Validación básica - solo metric es obligatorio
        if "metric" not in parsed:
            raise ValueError("El JSON devuelto no tiene la clave requerida 'metric'.")

        # Métricas que no requieren date_range
        metrics_sin_fecha = ['stock_actual', 'inventario_bajo', 'todos_clientes', 
                            'lista_clientes', 'clientes_sistema', 'inventario_por_categoria']

        # Procesamos el rango de fechas relativo
        period = parsed.get("period")
        if period and period != "custom":
            parsed["date_range"] = obtener_rango_fechas(period)
        
        # Fallback: si no hay period pero hay date_range (legacy o custom)
        elif isinstance(parsed.get("date_range"), dict):
            start = parsed["date_range"].get("start_date", "")
            end = parsed["date_range"].get("end_date", "")
            # Si detectamos palabras clave en las fechas (alucinación del LLM), recalculamos
            if any(x in (start + end).lower() for x in ["hoy", "mes", "semana", "trimestre", "últimos", "año", "ayer"]):
                parsed["date_range"] = obtener_rango_fechas(start or end)

        print(f"✅ JSON final con fechas reales: {parsed}")
        return parsed

    except Exception as e:
        print(f"❌ Error al analizar el prompt: {e}")
        return {"error": "No pude entender la petición. Asegúrate de formular una solicitud clara de reporte."}