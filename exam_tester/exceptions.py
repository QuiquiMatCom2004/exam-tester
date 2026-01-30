"""
Excepciones personalizadas para el framework ExamTester.

Este módulo define todas las excepciones que puede lanzar el framework,
proporcionando mensajes de error claros y específicos.
"""


class ExamTesterError(Exception):
    """
    Excepción base para todos los errores del framework.

    Todas las excepciones personalizadas heredan de esta clase,
    permitiendo capturar cualquier error del framework con:

    try:
        tester.evaluate_all()
    except ExamTesterError as e:
        print(f"Error del framework: {e}")
    """
    pass


class ConfigurationError(ExamTesterError):
    """
    Se lanza cuando falta configuración necesaria o es inválida.

    Ejemplos:
        - Intentar generar casos sin agregar ejercicios
        - Intentar evaluar sin haber generado casos de prueba
        - Rutas no configuradas

    Example:
        >>> tester = ExamTester("Mi Examen")
        >>> tester.evaluate_all()  # Sin configurar ejercicios
        ConfigurationError: No se puede evaluar. Falta: exercises, students_path, test_cases_generated
    """
    pass


class ValidationError(ExamTesterError):
    """
    Se lanza cuando los datos proporcionados no son válidos.

    Ejemplos:
        - Nombre de ejercicio inválido (no es identificador Python)
        - file_suffix menor que 1
        - Función de solución no es callable

    Example:
        >>> class BadExercise(Exercise):
        ...     def __init__(self):
        ...         super().__init__(name="mi ejercicio", ...)  # Espacio inválido
        ValidationError: name debe ser un identificador Python válido: mi ejercicio
    """
    pass


class EvaluationError(ExamTesterError):
    """
    Se lanza cuando ocurre un error durante la evaluación de estudiantes.

    Ejemplos:
        - No se puede cargar el módulo del estudiante
        - Error al ejecutar casos de prueba
        - Timeout en evaluación
    """
    pass


class GeneratorError(ExamTesterError):
    """
    Se lanza cuando hay un error en la generación de casos de prueba.

    Ejemplos:
        - Generador no implementa métodos requeridos
        - Error al generar casos aleatorios
        - Casos fijos tienen formato incorrecto
    """
    pass
