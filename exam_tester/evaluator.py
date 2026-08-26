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

import copy
import importlib.util
import multiprocessing
import sys
from pathlib import Path
from typing import Dict, List, Any, Callable, Tuple, Optional

from .exercise import Exercise
from .comparators import get_comparator
from .exceptions import EvaluationError


def _student_worker(file_path_str: str, function_name: str,
                     args: Tuple, queue: "multiprocessing.Queue") -> None:
    """
    Carga el archivo del estudiante desde cero y llama a la función indicada.

    Se ejecuta dentro de un proceso hijo aislado (ver _execute_function),
    para que cualquier estado global que el estudiante modifique (límite de
    recursión, semilla de random, monkeypatching, variables de módulo,
    argumentos por defecto mutables) muera junto con el proceso y nunca
    contamine al intérprete padre, a otros casos, otros ejercicios u otros
    estudiantes.
    """
    file_path = Path(file_path_str)
    module_name = f"student_{file_path.stem}_{id(file_path)}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            queue.put(("error", "No se pudo cargar el módulo"))
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, function_name):
            queue.put(("error", f"Función {function_name} no encontrada"))
            return

        resultado = getattr(module, function_name)(*args)
        try:
            queue.put(("ok", resultado))
        except Exception:
            queue.put(("error", "El resultado no se pudo serializar entre procesos"))
    except Exception as e:
        queue.put(("error", f"{type(e).__name__}: {str(e)}"))


def _student_check_worker(file_path_str: str, function_name: str,
                           queue: "multiprocessing.Queue") -> None:
    """
    Verifica en un proceso aislado si el módulo del estudiante carga y si
    contiene la función esperada, SIN llamarla. Existe para poder dar
    mensajes de error tempranos y amigables (archivo/función faltante) sin
    ejecutar el código de importación del estudiante en el proceso padre.
    """
    file_path = Path(file_path_str)
    module_name = f"student_check_{file_path.stem}_{id(file_path)}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            queue.put(("load_error", "No se pudo cargar el módulo"))
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, function_name):
            queue.put(("missing_function", None))
            return

        queue.put(("ok", None))
    except Exception as e:
        queue.put(("load_error", f"{type(e).__name__}: {str(e)}"))


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

        # Verificar que el módulo carga y tiene la función, en un proceso
        # aislado (evita ejecutar el import del estudiante en el padre)
        ok, error_msg = self._check_module(file_path, exercise.function_name)
        if not ok:
            return {
                'nombre_funcion': exercise.function_name,
                'error': error_msg
            }

        # Obtener casos de prueba
        casos = self.test_cases.get(exercise.name, [])
        if not casos:
            return {
                'nombre_funcion': exercise.function_name,
                'error': f'No hay casos de prueba para {exercise.name}'
            }

        # Obtener comparador
        comparator = get_comparator(exercise.comparator)

        # Ejecutar pruebas (cada caso corre en un proceso aislado, ver _execute_function)
        num_fixed = exercise.get_test_generator().get_num_fixed_cases()
        return self._run_tests(
            file_path,
            exercise.function_name,
            casos,
            num_fixed,
            comparator
        )

    def _run_tests(self, file_path: Path,
                   func_name: str,
                   test_cases: List[Dict[str, Any]],
                   num_fixed_cases: int,
                   comparator: Callable[[Any, Any], bool]) -> Dict[str, Any]:
        """
        Ejecuta todos los casos de prueba para una función.

        Cada caso se ejecuta en un proceso hijo aislado y desechable (ver
        _execute_function), recargando el archivo del estudiante desde cero
        en cada llamada. Esto evita que el estado de un caso (o de un
        ejercicio, o de un estudiante) se filtre al siguiente.

        Args:
            file_path: Ruta al archivo .py del estudiante
            func_name: Nombre de la función
            test_cases: Casos de prueba con respuestas esperadas
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
            # Obtener datos del caso (deep copy para que cada estudiante use el tablero original)
            inputs = copy.deepcopy(tuple(caso['inputs']))
            expected_output = caso['expected_output']
            expected_error = caso.get('expected_error')

            # Ejecutar función del estudiante en un proceso aislado
            student_output, student_error = self._execute_function(
                file_path, func_name, inputs
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
    def _check_module(file_path: Path, function_name: str,
                       timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """
        Verifica, en un proceso hijo aislado, si el archivo del estudiante
        carga correctamente y si contiene la función esperada.

        No ejecuta la función, solo el import. Correrlo en un proceso
        aparte (en vez de importar directamente en el padre) evita que
        efectos secundarios del import (globals, monkeypatching, límites de
        recursión, bucles infinitos a nivel de módulo) afecten al proceso
        principal del framework.

        Args:
            file_path: Ruta al archivo .py del estudiante
            function_name: Nombre de la función esperada
            timeout: Tiempo máximo en segundos (default: 5)

        Returns:
            Tupla (ok, mensaje_error). mensaje_error es None si ok es True.
        """
        ctx = multiprocessing.get_context("fork")
        queue = ctx.Queue()
        process = ctx.Process(
            target=_student_check_worker,
            args=(str(file_path), function_name, queue),
            daemon=True,
        )
        process.start()
        process.join(timeout)

        if process.is_alive():
            process.terminate()
            process.join(1)
            if process.is_alive():
                process.kill()
                process.join()
            return False, f"TimeoutError: La carga del módulo excedió el tiempo límite ({timeout}s)"

        if queue.empty():
            return False, "No se pudo cargar el módulo"

        status, _ = queue.get()
        if status == "ok":
            return True, None
        if status == "missing_function":
            return False, f"Función {function_name} no encontrada"
        return False, "No se pudo cargar el módulo"

    @staticmethod
    def _execute_function(file_path: Path, function_name: str, args: Tuple,
                         timeout: int = 5) -> Tuple[Any, Optional[str]]:
        """
        Ejecuta la función del estudiante en un proceso hijo aislado.

        A diferencia de un hilo, un proceso puede matarse de verdad
        (terminate/kill) si excede el tiempo límite: si el estudiante tiene
        un bucle infinito o una recursión que nunca termina, el proceso se
        destruye y la evaluación continúa en vez de quedarse colgada. Además,
        el proceso hijo importa el archivo del estudiante desde cero, así que
        cualquier efecto secundario global (límite de recursión, semillas,
        monkeypatching, variables de módulo, argumentos por defecto mutables)
        desaparece junto con el proceso y no puede filtrarse a otros casos,
        ejercicios o estudiantes.

        Args:
            file_path: Ruta al archivo .py del estudiante
            function_name: Nombre de la función a llamar
            args: Argumentos
            timeout: Tiempo máximo en segundos (default: 5)

        Returns:
            Tupla (resultado, error_msg)
        """
        ctx = multiprocessing.get_context("fork")
        queue = ctx.Queue()
        process = ctx.Process(
            target=_student_worker,
            args=(str(file_path), function_name, args, queue),
            daemon=True,
        )
        process.start()
        process.join(timeout)

        if process.is_alive():
            process.terminate()
            process.join(1)
            if process.is_alive():
                process.kill()
                process.join()
            return None, f"TimeoutError: La función excedió el tiempo límite ({timeout}s)"

        if queue.empty():
            if process.exitcode not in (0, None):
                return None, f"CrashError: el proceso terminó abruptamente (código {process.exitcode})"
            return None, "EvaluationError: no se recibió resultado del proceso hijo"

        status, payload = queue.get()
        return (payload, None) if status == "ok" else (None, payload)

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
