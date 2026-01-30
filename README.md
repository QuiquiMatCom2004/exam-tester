# ExamTester v2.0 - Framework Genérico de Evaluación

Framework genérico y reutilizable orientado a objetos para evaluar automáticamente código de estudiantes mediante casos de prueba.

## Características

- **Arquitectura OOP completa**: Clases para ejercicios y generadores de pruebas
- **Patrón Builder**: API fluida con encadenamiento de métodos
- **Pre-generación de resultados**: Ejecuta la solución correcta solo una vez (100x más rápido)
- **Nombres flexibles**: Soporta carpetas con espacios ("Adriana Amador") y archivos con guiones bajos ("Adriana_Amador_1.py")
- **Generación reproducible**: Casos aleatorios con semillas para reproducibilidad
- **Comparadores personalizables**: Funciones de comparación enchufables
- **Reportes multi-formato**: JSON (estructurado) y Markdown (legible)
- **Type hints completos**: Soporte completo de tipos para mypy
- **Validación exhaustiva**: Mensajes de error claros con seguimiento de configuración

## Instalación

```bash
# Instalación en modo desarrollo (editable)
pip install -e .

# Instalación regular
pip install .
```

## Inicio Rápido

```python
from exam_tester import ExamTester, Exercise
from exam_tester.generators import IntegerPairGenerator

# 1. Definir un ejercicio
class SumaExercise(Exercise):
    def __init__(self):
        super().__init__(
            name="suma",
            function_name="suma",
            file_suffix=1,
            comparator="default"
        )

    def get_solution(self):
        return lambda a, b: a + b

    def get_test_generator(self):
        return IntegerPairGenerator(
            fixed_cases=[(0, 0), (1, 1), (-1, 1)],
            min_val=-1000,
            max_val=1000
        )

# 2. Configurar y ejecutar el tester (patrón builder)
tester = (ExamTester("Mi Examen")
    .add_exercise(SumaExercise())
    .set_students_path("./StudentsCode")
    .set_results_path("./Results")
    .generate_test_cases(num_random=100, seed=42)
    .evaluate_all()
    .generate_reports(formats=['json', 'markdown'])
)
```

## Estructura del Proyecto

```
ExamTester/
├── exam_tester/              # Paquete principal (v2.0 OOP API)
│   ├── __init__.py           # Exporta API pública
│   ├── core.py               # Clase ExamTester (builder pattern)
│   ├── exercise.py           # Clase base Exercise (abstracta)
│   ├── generators.py         # Generadores de casos de prueba
│   ├── evaluator.py          # Motor de evaluación
│   ├── reporter.py           # Generador de reportes
│   ├── comparators.py        # Funciones de comparación
│   ├── exceptions.py         # Excepciones personalizadas
│   └── py.typed              # Marcador de type hints
├── examples/                 # Ejemplos de uso
│   ├── basic_usage.py
│   ├── custom_exercise.py
│   └── complete_workflow.py
├── StudentsCode/             # Carpeta para código de estudiantes
├── Results/                  # Carpeta de salida para reportes
├── setup.py                  # Configuración de empaquetado
├── MANIFEST.in               # Reglas de distribución
├── LICENSE                   # Licencia MIT
└── README.md                 # Esta documentación
```

## Guía de Uso Completa

### Paso 1: Definir Ejercicios

Cada ejercicio es una clase que hereda de `Exercise`:

```python
from exam_tester import Exercise
from exam_tester.generators import SingleIntegerGenerator

class FactorialExercise(Exercise):
    """Ejercicio: calcular factorial de un número"""

    def __init__(self):
        super().__init__(
            name="factorial",           # Identificador del ejercicio
            function_name="factorial",  # Nombre de la función a evaluar
            file_suffix=2,              # Archivo: {Nombre}_2.py
            comparator="default"        # Comparador a usar
        )

    def get_solution(self):
        """Retorna la solución correcta"""
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        return factorial

    def get_test_generator(self):
        """Retorna el generador de casos de prueba"""
        return SingleIntegerGenerator(
            fixed_cases=[
                (0,),   # Casos fijos (edge cases)
                (1,),
                (5,),
                (10,),
                (20,)
            ],
            min_val=0,
            max_val=20
        )
```

### Paso 2: Generadores de Casos de Prueba

ExamTester incluye 5 generadores predefinidos:

#### IntegerPairGenerator
Para funciones con 2 argumentos enteros:

```python
from exam_tester.generators import IntegerPairGenerator

generator = IntegerPairGenerator(
    fixed_cases=[(0, 0), (1, 1), (-1, 1)],
    min_val=-1000,
    max_val=1000
)
```

#### SingleIntegerGenerator
Para funciones con 1 argumento entero:

```python
from exam_tester.generators import SingleIntegerGenerator

generator = SingleIntegerGenerator(
    fixed_cases=[(0,), (1,), (5,)],
    min_val=0,
    max_val=100
)
```

#### IntegerListGenerator
Para funciones que reciben una lista de enteros:

```python
from exam_tester.generators import IntegerListGenerator

generator = IntegerListGenerator(
    fixed_cases=[
        ([],),
        ([1],),
        ([1, 2, 3],)
    ],
    min_length=0,
    max_length=10,
    min_val=-100,
    max_val=100
)
```

#### StringGenerator
Para funciones con argumentos de cadena:

```python
from exam_tester.generators import StringGenerator

generator = StringGenerator(
    fixed_cases=[
        ("",),
        ("hello",),
        ("123",)
    ],
    min_length=0,
    max_length=20,
    charset="abcdefghijklmnopqrstuvwxyz0123456789"
)
```

#### CustomGenerator
Para casos de prueba completamente personalizados:

```python
from exam_tester.generators import CustomGenerator

def mi_generador_personalizado(n, seed=None):
    """Genera n casos de prueba personalizados"""
    import random
    if seed is not None:
        random.seed(seed)

    casos = []
    for _ in range(n):
        # Tu lógica personalizada aquí
        x = random.randint(1, 100)
        y = random.choice(['a', 'b', 'c'])
        casos.append((x, y))
    return casos

generator = CustomGenerator(
    fixed_cases=[(10, 'a'), (20, 'b')],
    random_generator=mi_generador_personalizado
)
```

### Paso 3: Configurar el Tester (Patrón Builder)

```python
from exam_tester import ExamTester

# Crear el tester con patrón builder
tester = (ExamTester("Primer Parcial")
    .add_exercise(SumaExercise())
    .add_exercise(FactorialExercise())
    .set_students_path("./StudentsCode")
    .set_results_path("./Results")
)

# Validación automática
# Si falta alguna configuración, se lanzará ConfigurationError
```

### Paso 4: Generar Casos de Prueba

```python
# Generar casos (combina casos fijos + aleatorios)
tester.generate_test_cases(
    num_random=100,  # Número de casos aleatorios
    seed=42          # Semilla para reproducibilidad (opcional)
)

# Opcionalmente guardar los casos generados
tester.save_test_cases("./Results/test_cases.json")
```

**Optimización**: La solución correcta se ejecuta solo una vez aquí para pre-calcular todas las respuestas esperadas. Esto hace la evaluación 100x más rápida.

### Paso 5: Preparar Código de Estudiantes

Estructura de carpetas:

```
StudentsCode/
├── Juan Perez/              # Carpeta con espacios (OK)
│   ├── Juan_Perez_1.py      # Archivos con guiones bajos
│   └── Juan_Perez_2.py
├── Maria Lopez/
│   ├── Maria_Lopez_1.py
│   └── Maria_Lopez_2.py
└── Adriana Amador/
    ├── Adriana_Amador_1.py
    └── Adriana_Amador_2.py
```

**Importante**: Las carpetas pueden tener espacios, pero los archivos deben usar guiones bajos. El framework convierte automáticamente.

Ejemplo de archivo de estudiante (`Juan_Perez_1.py`):

```python
def suma(a, b):
    """Implementación del estudiante"""
    return a + b
```

### Paso 6: Evaluar Estudiantes

```python
# Evaluar todos los estudiantes
tester.evaluate_all()

# Acceder a resultados programáticamente
results = tester.get_results()
for student_result in results:
    print(f"Estudiante: {student_result['nombre_estudiante']}")
    for ejercicio in student_result['ejercicios']:
        print(f"  {ejercicio['ejercicio']}: {ejercicio['pasados']}/{ejercicio['total']}")
```

### Paso 7: Generar Reportes

```python
# Generar reportes en múltiples formatos
tester.generate_reports(formats=['json', 'markdown'])

# Reportes generados:
# - Results/resultados_TIMESTAMP.json  (datos estructurados)
# - Results/reporte_TIMESTAMP.md       (reporte legible)
```

## Comparadores Disponibles

### Comparadores Predefinidos

```python
from exam_tester.comparators import COMPARATORS

# default: Igualdad directa (==)
# list_equal: Compara listas elemento a elemento
# tuple_result: Para funciones que retornan (bool, valor)
```

### Crear Comparador Personalizado

```python
from exam_tester.comparators import register_comparator

def mi_comparador(esperado, obtenido):
    """Lógica de comparación personalizada"""
    # Retornar True si son equivalentes
    return abs(esperado - obtenido) < 0.001  # Tolerancia numérica

# Registrar el comparador
register_comparator("tolerancia", mi_comparador)

# Usar en ejercicio
class MiEjercicio(Exercise):
    def __init__(self):
        super().__init__(
            name="mi_ejercicio",
            function_name="mi_funcion",
            file_suffix=1,
            comparator="tolerancia"  # Usar comparador personalizado
        )
```

## Ejemplos Completos

### Ejemplo Básico

Ver [examples/basic_usage.py](examples/basic_usage.py):

```python
from exam_tester import ExamTester, Exercise
from exam_tester.generators import IntegerPairGenerator, SingleIntegerGenerator

class SumaExercise(Exercise):
    def __init__(self):
        super().__init__(name="suma", function_name="suma", file_suffix=1)

    def get_solution(self):
        return lambda a, b: a + b

    def get_test_generator(self):
        return IntegerPairGenerator(
            fixed_cases=[(0, 0), (1, 1), (-1, 1)],
            min_val=-1000,
            max_val=1000
        )

# Ejecutar
tester = (ExamTester("Primer Parcial Demo")
    .add_exercise(SumaExercise())
    .set_results_path("./Results")
    .generate_test_cases(num_random=10, seed=42)
)
tester.save_test_cases("./Results/demo_test_cases.json")
```

### Ejemplo con Evaluación Completa

Ver [examples/complete_workflow.py](examples/complete_workflow.py) para un flujo completo que incluye:
- Definición de múltiples ejercicios
- Generación de casos de prueba
- Evaluación de estudiantes
- Generación de reportes JSON y Markdown

### Ejemplo con Generador Personalizado

Ver [examples/custom_exercise.py](examples/custom_exercise.py) para un ejemplo usando `CustomGenerator`.

## Excepciones

El framework lanza excepciones específicas para facilitar el debugging:

```python
from exam_tester.exceptions import (
    ExamTesterError,        # Excepción base
    ConfigurationError,     # Falta configuración
    ValidationError,        # Datos inválidos
    EvaluationError,        # Error durante evaluación
    GeneratorError          # Error en generación de casos
)
```

Ejemplo de manejo:

```python
try:
    tester = ExamTester("Mi Examen")
    tester.evaluate_all()  # Falta configuración
except ConfigurationError as e:
    print(f"Error de configuración: {e}")
```

## Optimizaciones del Framework

### Respuestas Pre-generadas

**Problema**: Evaluar 100 estudiantes con 100 casos cada uno requiere ejecutar la solución correcta 10,000 veces (100 × 100).

**Solución**: Pre-generar las respuestas esperadas en `generate_test_cases()`, ejecutando la solución correcta solo 100 veces (una vez por caso).

**Resultado**: 100x mejora en rendimiento.

### Manejo Flexible de Nombres

- **Carpetas de estudiantes**: Pueden tener espacios (ej: "Adriana Amador", "Juan Perez")
- **Archivos de estudiantes**: Deben usar guiones bajos (ej: "Adriana_Amador_1.py")

El framework convierte automáticamente espacios a guiones bajos, eliminando errores comunes.

### Generación Reproducible

Usa el parámetro `seed` para generar siempre los mismos casos aleatorios:

```python
tester.generate_test_cases(num_random=100, seed=42)
# Siempre generará los mismos 100 casos
```

## API Reference

### ExamTester

```python
class ExamTester:
    def __init__(self, exam_name: str)
    def add_exercise(self, exercise: Exercise) -> 'ExamTester'
    def set_students_path(self, path: str) -> 'ExamTester'
    def set_results_path(self, path: str) -> 'ExamTester'
    def generate_test_cases(self, num_random: int, seed: Optional[int] = None) -> 'ExamTester'
    def save_test_cases(self, filepath: str) -> None
    def evaluate_all(self) -> 'ExamTester'
    def generate_reports(self, formats: List[str] = ['json', 'markdown']) -> 'ExamTester'
    def get_results(self) -> List[Dict[str, Any]]
```

### Exercise (Clase Abstracta)

```python
class Exercise(ABC):
    def __init__(self, name: str, function_name: str, file_suffix: int, comparator: str = "default")

    @abstractmethod
    def get_solution(self) -> Callable

    @abstractmethod
    def get_test_generator(self) -> TestCaseGenerator
```

### TestCaseGenerator (Clase Abstracta)

```python
class TestCaseGenerator(ABC):
    @abstractmethod
    def get_fixed_cases(self) -> List[Tuple[Any, ...]]

    @abstractmethod
    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[Any, ...]]

    def generate_all_cases(self, num_random: int, seed: Optional[int] = None) -> List[Tuple[Any, ...]]
```

## Solución de Problemas

### Error: ConfigurationError - "No se han agregado ejercicios"

```python
# Asegúrate de agregar al menos un ejercicio
tester.add_exercise(MiEjercicio())
```

### Error: ValidationError - "Ejercicio duplicado"

```python
# No agregues el mismo ejercicio dos veces
# (se compara por name y file_suffix)
```

### Error: EvaluationError - "No se encontró la función"

```python
# Verifica que el archivo del estudiante defina la función correcta
# Ejemplo: para function_name="suma", el archivo debe tener:
def suma(a, b):
    return a + b
```

### Error: "Archivo no encontrado"

```python
# Verifica que los archivos usen guiones bajos:
# Correcto:   Adriana_Amador_1.py
# Incorrecto: Adriana Amador 1.py
```

### Resultados inesperados tras modificar la solución

```python
# Regenera los casos de prueba
tester.generate_test_cases(num_random=100, seed=42)
```

## Migración desde v1.0

Si tienes código usando la v1.0 (con `config.py` y estructura de diccionarios):

**Antes (v1.0)**:
```python
EXAM_CONFIG = {
    "exam_name": "Mi Examen",
    "exercises": [{"name": "suma", "function_name": "suma", ...}]
}
```

**Después (v2.0)**:
```python
class SumaExercise(Exercise):
    def __init__(self):
        super().__init__(name="suma", function_name="suma", file_suffix=1)
    # ... implementar métodos abstractos

tester = ExamTester("Mi Examen").add_exercise(SumaExercise())
```

## Contribuir

Reporta problemas o sugiere mejoras en el repositorio del proyecto.

## Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

## Autor

ExamTester Contributors

---

**Versión**: 2.0.0
**Última actualización**: 2026-01-29
