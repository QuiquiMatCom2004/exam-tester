# ExamTester - Framework Generico de Evaluacion

Framework generico y reutilizable para evaluar automaticamente codigo de estudiantes mediante casos de prueba.

## Estructura del Proyecto

```
ExamTester/
├── config.py                    # Configuracion central del examen
├── Main/
│   └── main.py                  # Orquestador - evalua todos los estudiantes
├── Tester/
│   ├── tester.py                # Motor de pruebas
│   ├── case_loader.py           # Cargador de casos desde JSON
│   ├── generate_test_cases.py  # Generador de casos de prueba
│   └── comparators.py           # Registro de funciones de comparacion
├── ExamContent/                 # Contenido especifico del examen (reemplazable)
│   ├── correctSolution.py       # Soluciones oficiales
│   ├── input.py                 # Generadores de casos de prueba
│   └── test_cases.json          # Casos pre-generados (auto-generado)
├── StudentsCode/                # Carpeta para submissions de estudiantes
└── Results/                     # Carpeta de salida para reportes
```

## Flujo de Uso para un Nuevo Examen

### Paso 1: Configurar el examen

Editar `config.py` con la informacion del examen:

```python
EXAM_CONFIG = {
    "exam_name": "Primer Parcial",
    "num_random_cases": 100,
    "exercises": [
        {
            "name": "suma",              # Identificador del ejercicio
            "function_name": "suma",     # Nombre de la funcion a implementar
            "file_suffix": 1,            # Archivo: {nombre_estudiante}_1.py
            "num_fixed_cases": 5,        # Casos edge importantes
            "comparator": "default",     # Comparador a usar
        },
        {
            "name": "factorial",
            "function_name": "factorial",
            "file_suffix": 2,
            "num_fixed_cases": 7,
            "comparator": "default",
        },
    ]
}
```

### Paso 2: Escribir soluciones oficiales

Editar `ExamContent/correctSolution.py`:

```python
def suma(a, b):
    """Solucion oficial para el ejercicio suma."""
    return a + b

def factorial(n):
    """Solucion oficial para el ejercicio factorial."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

### Paso 3: Escribir generadores de casos

Editar `ExamContent/input.py` siguiendo la convencion `generar_casos_{name}(num_casos)`:

```python
import random

def generar_casos_suma(num_casos):
    casos = []
    # Casos fijos (edge cases) van primero
    casos.append((0, 0))
    casos.append((1, 1))
    casos.append((-1, 1))
    casos.append((100, -100))
    casos.append((999, 1))

    # Casos aleatorios
    for _ in range(num_casos - 5):
        a = random.randint(-1000, 1000)
        b = random.randint(-1000, 1000)
        casos.append((a, b))

    return casos

def generar_casos_factorial(num_casos):
    casos = []
    # Casos fijos
    casos.append((0,))
    casos.append((1,))
    casos.append((5,))
    casos.append((10,))
    casos.append((15,))
    casos.append((20,))
    casos.append((1,))

    # Casos aleatorios
    for _ in range(num_casos - 7):
        n = random.randint(0, 20)
        casos.append((n,))

    return casos
```

**Importante**:
- Los nombres de las funciones deben seguir el patron `generar_casos_{name}` donde `{name}` es el campo "name" del ejercicio en config.py
- Cada caso es una tupla con los argumentos de la funcion
- Los casos fijos (edge cases) van al inicio de la lista

### Paso 4: Preparar carpetas de estudiantes

Colocar las carpetas de estudiantes en `StudentsCode/`. Cada carpeta debe:
- Tener como nombre el identificador del estudiante (puede contener espacios, ej: `Adriana Amador`)
- Contener archivos con patron: `{Nombre_Con_Guiones_Bajos}_{file_suffix}.py`

**Importante**: Las carpetas pueden tener espacios, pero los archivos deben usar guiones bajos (`_`).

Ejemplo:
```
StudentsCode/
├── Juan Perez/
│   ├── Juan_Perez_1.py    # Contiene: def suma(a, b): ...
│   └── Juan_Perez_2.py    # Contiene: def factorial(n): ...
├── Maria Lopez/
│   ├── Maria_Lopez_1.py
│   └── Maria_Lopez_2.py
└── Adriana Amador/
    ├── Adriana_Amador_1.py
    └── Adriana_Amador_2.py
```

### Paso 5: Generar casos de prueba

Ejecutar el generador de casos (solo una vez):

```bash
python Tester/generate_test_cases.py
```

Esto creara `ExamContent/test_cases.json` con:
- Todos los casos de entrada pre-generados
- Las respuestas esperadas de la solución correcta para cada caso

**Optimización**: Al pre-generar las respuestas, la solución correcta se ejecuta solo una vez (en este paso), en lugar de ejecutarse por cada estudiante. Esto hace la evaluación mucho más rápida.

### Paso 6: Evaluar estudiantes

Ejecutar el evaluador principal:

```bash
python Main/main.py
```

Esto:
1. Inyecta el tester en cada carpeta de estudiante (sin la solución correcta)
2. Ejecuta las pruebas comparando contra respuestas pre-generadas
3. Recopila resultados
4. Genera reportes en `Results/`:
   - `resultados_TIMESTAMP.json` (datos estructurados)
   - `reporte_TIMESTAMP.md` (reporte legible)
5. Limpia archivos temporales

**Nota**: La solución correcta NO se ejecuta durante este paso, solo se comparan las respuestas del estudiante contra las respuestas pre-generadas en `test_cases.json`.

## Comparadores Disponibles

Los comparadores se usan para validar resultados. Disponibles en `Tester/comparators.py`:

- **`default`**: Igualdad directa (`==`)
- **`list_equal`**: Compara listas elemento a elemento
- **`tuple_result`**: Para funciones que retornan `(bool, valor)`. Si ambos tienen primer elemento falsy, son iguales.

### Agregar un comparador personalizado

Editar `Tester/comparators.py`:

```python
def mi_comparador(esperado, obtenido):
    """Tu logica de comparacion personalizada."""
    # Retornar True si son equivalentes, False si no
    return esperado == obtenido

# Agregar al registro
COMPARATORS["mi_comparador"] = mi_comparador
```

Luego usar `"comparator": "mi_comparador"` en config.py.

## Optimizaciones del Framework

### Respuestas Pre-generadas

El framework utiliza un enfoque optimizado que genera las respuestas esperadas una sola vez:

**Ventajas**:

- **Eficiencia**: La solución correcta se ejecuta solo una vez (al generar `test_cases.json`), no por cada estudiante
- **Consistencia**: Todos los estudiantes son evaluados contra exactamente las mismas respuestas esperadas
- **Velocidad**: La evaluación es mucho más rápida, especialmente con muchos estudiantes
- **Portabilidad**: El archivo `test_cases.json` contiene todo lo necesario para evaluar

**Formato del JSON**:

```json
{
  "ejercicio1": [
    {
      "inputs": [arg1, arg2, ...],
      "expected_output": resultado,
      "expected_error": null
    },
    ...
  ]
}
```

### Manejo Flexible de Nombres

El framework soporta dos formatos de nombres comunes en entornos educativos:

- **Carpetas**: Pueden tener espacios (ej: `Adriana Amador`, `Juan Perez`)
- **Archivos**: Deben usar guiones bajos (ej: `Adriana_Amador_1.py`, `Juan_Perez_1.py`)

El framework convierte automáticamente los espacios a guiones bajos al buscar archivos, eliminando errores comunes de formato.

## Estructura de Archivos de Estudiante

Cada archivo debe:
- Tener nombre: `{Nombre_Con_Guiones_Bajos}_{file_suffix}.py`
- Definir la funcion especificada en `function_name` del config
- La funcion debe tener la misma firma que la solucion oficial

**Formato de nombres**: Las carpetas pueden tener espacios (ej: `Adriana Amador`), pero los archivos deben usar guiones bajos (ej: `Adriana_Amador_1.py`). El framework convierte automáticamente los espacios a guiones bajos al buscar archivos.

Ejemplo (`Juan_Perez_1.py`):
```python
def suma(a, b):
    return a + b
```

## Reportes Generados

### JSON (`resultados_TIMESTAMP.json`)
Datos estructurados con:
- Resultados por estudiante
- Casos pasados/fallidos/error
- Detalles de cada fallo (entrada, esperado, obtenido)

### Markdown (`reporte_TIMESTAMP.md`)
Reporte legible con:
- Resumen general de aprobacion por ejercicio
- Tabla detallada por estudiante
- Estadisticas de casos fijos pasados

## Consejos

1. **Casos fijos**: Son casos criticos que deben ir al inicio de la lista en los generadores. Permiten verificar edge cases importantes.

2. **Nombres de ejercicios**: Deben ser identificadores Python validos (sin espacios, caracteres especiales).

3. **Formato de nombres**: Las carpetas de estudiantes pueden tener espacios, pero los archivos deben usar guiones bajos. El framework maneja esto automáticamente.

4. **Regenerar casos**: Si modificas la solución correcta o los generadores, debes ejecutar nuevamente `python Tester/generate_test_cases.py` para regenerar las respuestas esperadas.

5. **Timeout**: Las evaluaciones tienen timeout de 60 segundos por estudiante. Codigo con loops infinitos sera detectado.

6. **Limpieza automatica**: El tester inyecta archivos temporales pero los limpia al terminar. Las carpetas de estudiantes quedan intactas.

7. **Reutilizacion**: Para un nuevo examen, solo cambia `config.py`, `ExamContent/correctSolution.py` y `ExamContent/input.py`. El framework en `Tester/` y `Main/` nunca se modifica.

8. **Eficiencia**: Con respuestas pre-generadas, evaluar 100 estudiantes con 100 casos cada uno solo requiere ejecutar la solución correcta 100 veces (una vez por caso), en lugar de 10,000 veces (100 casos × 100 estudiantes).

## Solucion de Problemas

### Error: "No se encontro generar_casos_{nombre}"

- Verifica que `ExamContent/input.py` tenga una funcion con ese nombre exacto

### Error: "No se encontro funcion '{nombre}' en ExamContent/correctSolution.py"

- Verifica que `ExamContent/correctSolution.py` defina la funcion especificada
- Ejecuta nuevamente `python Tester/generate_test_cases.py` para regenerar el JSON

### Error: "No se encontro ExamContent/test_cases.json"

- Ejecuta primero: `python Tester/generate_test_cases.py`

### Error: "Archivo {nombre}_{suffix}.py no encontrado"

- Verifica que los archivos de estudiante usen guiones bajos (`_`), no espacios
- Ejemplo correcto: `Adriana_Amador_1.py` (no `Adriana Amador 1.py`)
- La carpeta puede llamarse `Adriana Amador` (con espacio), pero el archivo debe usar guiones bajos

### Estudiante con todos los casos fallidos

- Verifica que el nombre de la funcion en su archivo coincida exactamente con `function_name` en config.py
- Verifica que la firma de la funcion (numero de parametros) coincida con la solucion oficial

### Resultados diferentes después de modificar la solución correcta

- Recuerda regenerar los casos: `python Tester/generate_test_cases.py`
- Las respuestas esperadas están pre-generadas en `test_cases.json`, no se actualizan automáticamente

## Licencia

Framework desarrollado para evaluacion educativa.
