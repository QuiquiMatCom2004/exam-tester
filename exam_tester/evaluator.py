"""
Módulo para evaluar código de estudiantes.

Este módulo proporciona la clase StudentEvaluator que:
- Carga código Python de estudiantes
- Ejecuta casos de prueba
- Compara resultados con respuestas esperadas
- Genera reportes detallados de errores

Example:
    Uso interno desde ExamTester:

    >>> evaluator = StudentEvaluator(exercises, test_cases)
    >>> result = evaluator.evaluate_student("Juan Perez", Path("./StudentsCode/Juan Perez"))
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any, Callable, Tuple, Optional

from .exercise import Exercise
from .comparators import get_comparator
from .exceptions import EvaluationError


class StudentEvaluator:
    """
    Evaluador de código de estudiantes.

    Esta clase se encarga de:
    1. Cargar módulos Python de estudiantes
    2. Ejecutar funciones con casos de prueba
    3. Comparar resultados
    4. Generar reportes detallados

    Args:
        exercises: Lista de ejercicios configurados
        test_cases: Casos de prueba con respuestas esperadas

    Example:
        >>> evaluator = StudentEvaluator(exercises, test_cases)
        >>> resultado = evaluator.evaluate_student(
        ...     "Juan Perez",
        ...     Path("./StudentsCode/Juan Perez")
        ... )
    """

    def __init__(self, exercises: List[Exercise],
                 test_cases: Dict[str, List[Dict[str, Any]]]):
        """
        Inicializa el evaluador.

        Args:
            exercises: Lista de ejercicios
            test_cases: Diccionario {nombre_ejercicio: casos}
        """
        self.exercises = exercises
        self.test_cases = test_cases

    def evaluate_student(self, student_name: str,
                        student_folder: Path) -> Dict[str, Any]:
        """
        Evalúa todos los ejercicios de un estudiante.

        Args:
            student_name: Nombre del estudiante (puede tener espacios)
            student_folder: Ruta a la carpeta del estudiante

        Returns:
            Diccionario con resultados de la evaluación

        Example:
            >>> result = evaluator.evaluate_student(
            ...     "Adriana Amador",
            ...     Path("./StudentsCode/Adriana Amador")
            ... )
            >>> print(result['nombre_estudiante'])
            'Adriana Amador'
            >>> print(result['ejercicios'][0]['casos_pasados'])
            95
        """
        # Convertir nombre con espacios a nombre de archivo con guiones bajos
        # "Adriana Amador" -> "Adriana_Amador"
        file_name = student_name.replace(' ', '_')

        resultados = {
            'nombre_estudiante': student_name,
            'ejercicios': []
        }

        # Evaluar cada ejercicio
        for exercise in self.exercises:
            ejercicio_result = self._evaluate_exercise(
                exercise,
                student_folder,
                file_name
            )
            resultados['ejercicios'].append(ejercicio_result)

        return resultados

    def _evaluate_exercise(self, exercise: Exercise,
                          student_folder: Path,
                          file_name: str) -> Dict[str, Any]:
        """
        Evalúa un ejercicio específico para un estudiante.

        Args:
            exercise: Ejercicio a evaluar
            student_folder: Carpeta del estudiante
            file_name: Nombre base del archivo (con guiones bajos)

        Returns:
            Diccionario con resultados del ejercicio
        """
        # Construir ruta al archivo del estudiante
        file_path = student_folder / f"{file_name}_{exercise.file_suffix}.py"

        # Verificar que existe
        if not file_path.exists():
            return {
                'nombre_funcion': exercise.function_name,
                'error': f'Archivo {file_path.name} no encontrado'
            }

        # Cargar módulo
        module = self._load_module(file_path)
        if module is None:
            return {
                'nombre_funcion': exercise.function_name,
                'error': 'No se pudo cargar el módulo'
            }

        # Verificar que tiene la función
        if not hasattr(module, exercise.function_name):
            return {
                'nombre_funcion': exercise.function_name,
                'error': f'Función {exercise.function_name} no encontrada'
            }

        # Obtener función del estudiante
        student_func = getattr(module, exercise.function_name)

        # Obtener casos de prueba
        casos = self.test_cases.get(exercise.name, [])
        if not casos:
            return {
                'nombre_funcion': exercise.function_name,
                'error': f'No hay casos de prueba para {exercise.name}'
            }

        # Obtener comparador
        comparator = get_comparator(exercise.comparator)

        # Ejecutar pruebas
        num_fixed = exercise.get_test_generator().get_num_fixed_cases()
        return self._run_tests(
            student_func,
            casos,
            exercise.function_name,
            num_fixed,
            comparator
        )

    def _run_tests(self, student_func: Callable,
                   test_cases: List[Dict[str, Any]],
                   func_name: str,
                   num_fixed_cases: int,
                   comparator: Callable[[Any, Any], bool]) -> Dict[str, Any]:
        """
        Ejecuta todos los casos de prueba para una función.

        Args:
            student_func: Función del estudiante
            test_cases: Casos de prueba con respuestas esperadas
            func_name: Nombre de la función
            num_fixed_cases: Número de casos fijos
            comparator: Función comparadora

        Returns:
            Diccionario con resultados detallados
        """
        resultados = {
            'nombre_funcion': func_name,
            'total_casos': len(test_cases),
            'casos_pasados': 0,
            'casos_fallidos': 0,
            'casos_error': 0,
            'casos_fijados_total': num_fixed_cases,
            'casos_fijados_pasados': 0,
            'detalles_fallos': []
        }

        for i, caso in enumerate(test_cases, 1):
            # Obtener datos del caso
            inputs = tuple(caso['inputs'])
            expected_output = caso['expected_output']
            expected_error = caso.get('expected_error')

            # Ejecutar función del estudiante
            student_output, student_error = self._execute_function(
                student_func, inputs
            )

            # Determinar si es caso fijo
            is_fixed = (i <= num_fixed_cases)

            # Evaluar resultado
            self._evaluate_case(
                i, inputs,
                expected_output, expected_error,
                student_output, student_error,
                is_fixed, comparator,
                resultados
            )

        return resultados

    def _evaluate_case(self, case_num: int, inputs: Tuple,
                      expected_output: Any, expected_error: Optional[str],
                      student_output: Any, student_error: Optional[str],
                      is_fixed: bool, comparator: Callable,
                      resultados: Dict[str, Any]):
        """
        Evalúa un caso de prueba individual.

        Args:
            case_num: Número del caso
            inputs: Entrada del caso
            expected_output: Salida esperada
            expected_error: Error esperado (si aplica)
            student_output: Salida del estudiante
            student_error: Error del estudiante (si hubo)
            is_fixed: Si es un caso fijo
            comparator: Función comparadora
            resultados: Diccionario donde agregar resultados (se modifica)
        """
        # Caso 1: Se esperaba un error
        if expected_error:
            if student_error:
                # Ambos generan error - correcto
                resultados['casos_pasados'] += 1
                if is_fixed:
                    resultados['casos_fijados_pasados'] += 1
            else:
                # Estudiante no generó error cuando debería
                resultados['casos_fallidos'] += 1
                resultados['detalles_fallos'].append({
                    'caso_numero': case_num,
                    'entrada': list(inputs),
                    'esperado': f"ERROR: {expected_error}",
                    'obtenido': self._format_value(student_output),
                    'tipo_error': 'deberia_generar_error'
                })

        # Caso 2: Estudiante generó error inesperado
        elif student_error:
            resultados['casos_error'] += 1
            resultados['detalles_fallos'].append({
                'caso_numero': case_num,
                'entrada': list(inputs),
                'esperado': self._format_value(expected_output),
                'obtenido': f"ERROR: {student_error}",
                'tipo_error': 'excepcion'
            })

        # Caso 3: Comparar resultados
        elif not comparator(expected_output, student_output):
            resultados['casos_fallidos'] += 1
            resultados['detalles_fallos'].append({
                'caso_numero': case_num,
                'entrada': list(inputs),
                'esperado': self._format_value(expected_output),
                'obtenido': self._format_value(student_output),
                'tipo_error': 'resultado_incorrecto'
            })

        # Caso 4: Correcto
        else:
            resultados['casos_pasados'] += 1
            if is_fixed:
                resultados['casos_fijados_pasados'] += 1

    @staticmethod
    def _load_module(file_path: Path):
        """
        Carga un módulo Python desde un archivo.

        Args:
            file_path: Ruta al archivo .py

        Returns:
            Módulo cargado o None si hay error
        """
        try:
            spec = importlib.util.spec_from_file_location(
                "student_module",
                file_path
            )
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules['student_module'] = module
            spec.loader.exec_module(module)
            return module
        except Exception:
            return None

    @staticmethod
    def _execute_function(func: Callable, args: Tuple,
                         timeout: int = 5) -> Tuple[Any, Optional[str]]:
        """
        Ejecuta una función con manejo de excepciones.

        Args:
            func: Función a ejecutar
            args: Argumentos
            timeout: Tiempo máximo (reservado para futura implementación)

        Returns:
            Tupla (resultado, error_msg)
        """
        try:
            resultado = func(*args)
            return resultado, None
        except Exception as e:
            return None, f"{type(e).__name__}: {str(e)}"

    @staticmethod
    def _format_value(value: Any) -> Any:
        """
        Formatea un valor para mostrar en reportes.

        Args:
            value: Valor a formatear

        Returns:
            Valor formateado (None se convierte a 'None')
        """
        return value if value is not None else 'None'
