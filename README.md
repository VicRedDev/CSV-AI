# CSV-AI

Procesa un archivo CSV y crea nuevas columnas usando LLMs a partir de otras columnas del mismo CSV.

## ¿Qué hace?

- Toma un CSV desde `csvs/`.
- Toma un formatter JSON desde `formatters/`.
- Para cada columna definida en el formatter, consulta al LLM con un prompt y campos del CSV.
- Guarda un nuevo CSV en `results/` con las columnas originales + las nuevas columnas AI.

## Requisitos

- Python 3.10+
- Dependencias:

```bash
pip install openai python-dotenv
```

## Estructura del proyecto

```txt
csv-ai/
├── main.py
├── ai.py
├── app.py
├── csvs/           # aquí van los CSV a procesar
├── formatters/     # aquí van los formatter .json
└── results/        # aquí se guardan los CSV de salida
```

## Configuración (`.env`)

1. Copia el ejemplo:

```bash
cp .env.example .env
```

2. Edita `.env` según tu proveedor/modelo.

Variables principales:

- `LANGUAGE`: `es` o `en`.
- `REASONING_EFFORT`: `high`, `medium` o `low`.
- `USE_RESPONSE_FORMAT`: mejora consistencia de salida estructurada (`true/false`).
  - Recomendado en modelos potentes.
  - No siempre funciona bien en modelos open source pequeños.
- `PROCESSING_LIMIT`: limita cuántas filas se procesan.
  - Ejemplo: `PROCESSING_LIMIT=100` procesa solo 100 filas.
  - Si está vacío, en `0` o en un valor inválido, procesa todo el CSV.
- `MULTIPLE_LINE_PROCESSING_LIMIT`: cuántas filas se procesan en paralelo simultáneamente.
  - Ejemplo: `MULTIPLE_LINE_PROCESSING_LIMIT=5` procesa 5 filas a la vez.
  - Si está vacío, en `0` o en un valor inválido, se usa `1` (secuencial).

Variables de conexión del LLM:

- `BASE_URL`
- `API_KEY`
- `AI_MODEL`

### Ejemplo de `.env` (autocontenido)

Puedes copiar este bloque y luego completar tus credenciales/modelo:

```env
LANGUAGE=en

REASONING_EFFORT=high
USE_RESPONSE_FORMAT=false
PROCESSING_LIMIT=
MULTIPLE_LINE_PROCESSING_LIMIT=

# --- Elige SOLO un proveedor ---

# OPENAI
# BASE_URL=
# API_KEY=tu_api_key
# AI_MODEL=gpt-5-nano

# LM STUDIO (local)
# BASE_URL=http://localhost:7341/v1
# API_KEY=lm-studio
# AI_MODEL=tu-modelo-local

# GROK
# BASE_URL=https://api.x.ai/v1
# API_KEY=tu_api_key
# AI_MODEL=grok-4-1-fast-non-reasoning

# DEEPSEEK
# BASE_URL=https://api.deepseek.com
# API_KEY=tu_api_key
# AI_MODEL=deepseek-chat
```

## Uso rápido

1. Coloca uno o más CSV en `csvs/`.
2. Coloca uno o más formatter `.json` en `formatters/`.
3. Ejecuta:

```bash
python main.py
```

4. El sistema mostrará menús para elegir:
   - idioma,
   - CSV,
   - formatter.
5. El resultado se guarda en `results/` con nombre timestamp.

## ¿Cómo crear un formatter?

Cada key del JSON es el nombre de la columna nueva que quieres generar.

Cada valor es un objeto con esta estructura:

- `prompt` (string, requerido): instrucción para el LLM.
- `show_fields` (array de strings, requerido): columnas del CSV que se envían al modelo (deben coincidir exactamente con el encabezado del CSV).
- `type` (requerido): `string`, `date` o `enum`.
- `enum` (opcional, requerido si `type = enum`): opciones válidas.
- `get_original` (boolean): **definido para uso futuro**. Actualmente no se aplica en el flujo.
- `can_leave_empty` (boolean): permite devolver vacío cuando corresponde y ayuda a reducir alucinaciones.

### Ejemplo de formatter (autocontenido)

Ejemplo mínimo:

```json
{
  "NUEVA_COLUMNA_AI": {
    "prompt": "Extrae X del texto.",
    "show_fields": ["TEXTO"],
    "type": "string",
    "get_original": true,
    "can_leave_empty": true
  },
  "ESTADO_AI": {
    "prompt": "Clasifica el estado.",
    "show_fields": ["DESCRIPCION"],
    "type": "enum",
    "enum": ["ABIERTO", "CERRADO"],
    "can_leave_empty": true
  }
}
```

Ejemplo realista (tickets de soporte):

```json
{
  "CATEGORIA_AI": {
    "prompt": "Clasifica la categoría principal del ticket según el problema descrito.",
    "show_fields": ["ASUNTO", "MENSAJE"],
    "type": "enum",
    "enum": ["FACTURACION", "TECNICO", "ENVIO", "CUENTA"],
    "can_leave_empty": true
  },
  "PRIORIDAD_AI": {
    "prompt": "Según el impacto reportado, clasifica la prioridad del ticket.",
    "show_fields": ["ASUNTO", "MENSAJE"],
    "type": "enum",
    "enum": ["BAJA", "MEDIA", "ALTA", "CRITICA"],
    "can_leave_empty": true
  },
  "RESUMEN_AI": {
    "prompt": "Resume el problema en una sola oración clara.",
    "show_fields": ["MENSAJE"],
    "type": "string",
    "get_original": true,
    "can_leave_empty": true
  },
  "FECHA_REPORTE_AI": {
    "prompt": "Extrae la fecha del reporte si está presente en el texto.",
    "show_fields": ["MENSAJE"],
    "type": "date",
    "can_leave_empty": true
  }
}
```

## Tipos soportados

- `string`: texto libre.
- `enum`: una opción entre las definidas en `enum`.
- `date`: el modelo devuelve estructura de fecha (`day`, `month`, `year`).

## Notas importantes

- Los nombres en `show_fields` deben existir en el CSV exactamente igual.
- Si faltan `BASE_URL`/`API_KEY`/`AI_MODEL` correctos, el proceso fallará o devolverá `ERROR`.
- `PROCESSING_LIMIT` solo afecta la cantidad de filas procesadas; no modifica el CSV original.
- Si `PROCESSING_LIMIT` está vacío, en `0` o es inválido, se procesan todas las filas.

## Flujo recomendado

1. Prueba primero con un CSV pequeño.
2. Ajusta prompts y `show_fields` en el formatter.
3. Activa/desactiva `USE_RESPONSE_FORMAT` según calidad del modelo.
4. Cuando el resultado sea bueno, procesa archivos más grandes.

