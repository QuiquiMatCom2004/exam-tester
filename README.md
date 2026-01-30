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
- Tener como nombre el identificador del estudiante (ej: `juan_perez`)
- Contener archivos con patron: `{nombre_estudiante}_{file_suffix}.py`

Ejemplo:
```
StudentsCode/
├── juan_perez/
│   ├── juan_perez_1.py    # Contiene: def suma(a, b): ...
│   └── juan_perez_2.py    # Contiene: def factorial(n): ...
└── maria_lopez/
    ├── maria_lopez_1.py
    └── maria_lopez_2.py
```

### Paso 5: Generar casos de prueba

Ejecutar el generador de casos (solo una vez):

```bash
python Tester/generate_test_cases.py
```

Esto creara `ExamContent/test_cases.json` con todos los casos pre-generados.

### Paso 6: Evaluar estudiantes

Ejecutar el evaluador principal:

```bash
python Main/main.py
```

Esto:
1. Inyecta el tester en cada carpeta de estudiante
2. Ejecuta las pruebas
3. Recopila resultados
4. Genera reportes en `Results/`:
   - `resultados_TIMESTAMP.json` (datos estructurados)
   - `reporte_TIMESTAMP.md` (reporte legible)
5. Limpia archivos temporales

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

## Estructura de Archivos de Estudiante

Cada archivo debe:
- Tener nombre: `{nombre_estudiante}_{file_suffix}.py`
- Definir la funcion especificada en `function_name` del config
- La funcion debe tener la misma firma que la solucion oficial

Ejemplo (`juan_perez_1.py`):
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

3. **Timeout**: Las evaluaciones tienen timeout de 60 segundos por estudiante. Codigo con loops infinitos sera detectado.

4. **Limpieza automatica**: El tester inyecta archivos temporales pero los limpia al terminar. Las carpetas de estudiantes quedan intactas.

5. **Reutilizacion**: Para un nuevo examen, solo cambia `config.py`, `ExamContent/correctSolution.py` y `ExamContent/input.py`. El framework en `Tester/` y `Main/` nunca se modifica.

## Solucion de Problemas

**Error: "No se encontro generar_casos_{nombre}"**
- Verifica que `ExamContent/input.py` tenga una funcion con ese nombre exacto

**Error: "Solucion correcta no tiene la funcion {nombre}"**
- Verifica que `ExamContent/correctSolution.py` defina la funcion especificada

**Error: "No se encontro ExamContent/test_cases.json"**
- Ejecuta primero: `python Tester/generate_test_cases.py`

**Estudiante con todos los casos fallidos**
- Verifica que el nombre de la funcion en su archivo coincida exactamente con `function_name` en config.py
- Verifica que la firma de la funcion (numero de parametros) coincida con la solucion oficial

## Licencia

Framework desarrollado para evaluacion educativa.
