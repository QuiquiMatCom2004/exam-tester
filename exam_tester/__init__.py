"""
ExamTester - Framework para evaluación automática de código de estudiantes.

Este paquete proporciona un framework orientado a objetos para:
- Definir ejercicios y casos de prueba
- Generar casos con respuestas pre-calculadas
- Evaluar código de estudiantes automáticamente
- Generar reportes detallados

Example:
    Uso básico:

    >>> from exam_tester import ExamTester, Exercise
    >>> from exam_tester.generators import IntegerPairGenerator
    >>>
    >>> # Definir ejercicio
    >>> class SumaExercise(Exercise):
    ...     def __init__(self):
    ...         super().__init__(name="suma", function_name="suma", file_suffix=1)
    ...
    ...     def get_solution(self):
    ...         return lambda a, b: a + b
    ...
    ...     def get_test_generator(self):
    ...         return IntegerPairGenerator(min_val=-1000, max_val=1000)
    >>>
    >>> # Configurar y ejecutar
    >>> tester = (ExamTester("Mi Examen")
    ...     .add_exercise(SumaExercise())
    ...     .set_students_path("./StudentsCode")
    ...     .generate_test_cases(num_random=100, seed=42)
    ...     .evaluate_all()
    ...     .generate_reports())

Módulos principales:
- exercise: Clase base Exercise para definir ejercicios
- generators: Generadores de casos de prueba (IntegerPairGenerator, etc.)
- core: Clase principal ExamTester
- exceptions: Excepciones personalizadas
"""

# Exportar clases principales
from .exercise import Exercise
from .generators import (
    TestCaseGenerator,
    IntegerPairGenerator,
    SingleIntegerGenerator,
    IntegerListGenerator,
    StringGenerator,
    CustomGenerator
)
from .exceptions import (
    ExamTesterError,
    ConfigurationError,
    ValidationError,
    EvaluationError,
    GeneratorError
)

# La clase ExamTester se importará después de crearla
# from .core import ExamTester

# Versión del paquete
__version__ = "2.0.0"

# Definir qué se exporta con "from exam_tester import *"
__all__ = [
    # Clases base
    'Exercise',
    'TestCaseGenerator',
    # 'ExamTester',  # Se agregará después

    # Generadores predefinidos
    'IntegerPairGenerator',
    'SingleIntegerGenerator',
    'IntegerListGenerator',
    'StringGenerator',
    'CustomGenerator',

    # Excepciones
    'ExamTesterError',
    'ConfigurationError',
    'ValidationError',
    'EvaluationError',
    'GeneratorError',

    # Versión
    '__version__',
]
