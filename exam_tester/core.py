"""
Clase principal ExamTester para orquestar todo el framework.

Este módulo contiene la clase ExamTester que coordina:
- Configuración de ejercicios
- Generación de casos de prueba con respuestas pre-calculadas
- Evaluación de estudiantes
- Generación de reportes

Example:
    Uso básico con builder pattern:

    >>> from exam_tester import ExamTester
    >>> from examples.basic_usage import SumaExercise, FactorialExercise
    >>>
    >>> tester = (ExamTester("Primer Parcial")
    ...     .add_exercise(SumaExercise())
    ...     .add_exercise(FactorialExercise())
    ...     .set_students_path("./StudentsCode")
    ...     .set_results_path("./Results")
    ...     .generate_test_cases(num_random=100, seed=42)
    ...     .evaluate_all()
    ...     .generate_reports(formats=['json', 'markdown'])
    ... )
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .exercise import Exercise
from .exceptions import ConfigurationError, ValidationError
from .evaluator import StudentEvaluator
from .reporter import ReportGenerator


class ExamTester:
    """
    Clase principal para configurar y ejecutar evaluaciones automáticas.

    Esta clase implementa el patrón Builder, permitiendo encadenar métodos
    para configurar el examen:

    ```python
    tester = (ExamTester("Mi Examen")
        .add_exercise(ejercicio1)
        .add_exercise(ejercicio2)
        .set_students_path("./StudentsCode")
        .generate_test_cases(num_random=100, seed=42)
        .evaluate_all()
        .generate_reports()
    )
    ```

    Args:
        exam_name: Nombre del examen (aparecerá en reportes)

    Attributes:
        exam_name: Nombre del examen
        exercises: Lista de ejercicios agregados
        students_path: Ruta a carpetas de estudiantes
        results_path: Ruta donde guardar resultados
        test_cases: Casos de prueba generados con respuestas esperadas
        results: Resultados de evaluaciones

    Raises:
        ConfigurationError: Si se intenta ejecutar sin configuración completa
        ValidationError: Si los parámetros proporcionados son inválidos
    """

    def __init__(self, exam_name: str):
        """
        Inicializa el tester.

        Args:
            exam_name: Nombre del examen

        Raises:
            ValidationError: Si exam_name está vacío
        """
        if not exam_name or not exam_name.strip():
            raise ValidationError("exam_name no puede estar vacío")

        self.exam_name = exam_name.strip()
        self._exercises: List[Exercise] = []
        self._students_path: Optional[Path] = None
        self._results_path: Optional[Path] = None
        self._test_cases: Dict[str, List[Dict[str, Any]]] = {}
        self._results: List[Dict[str, Any]] = []

        # Estado de configuración
        self._configured = {
            'exam_name': True,
            'exercises': False,
            'students_path': False,
            'results_path': False,
            'test_cases_generated': False,
            'students_evaluated': False
        }

    # ================================================================
    # MÉTODOS DE CONFIGURACIÓN (Builder Pattern)
    # ================================================================

    def add_exercise(self, exercise: Exercise) -> 'ExamTester':
        """
        Agrega un ejercicio al examen.

        Args:
            exercise: Instancia de Exercise a agregar

        Returns:
            self (para builder pattern)

        Raises:
            TypeError: Si exercise no es instancia de Exercise
            ValidationError: Si ya existe un ejercicio con el mismo nombre

        Example:
            >>> tester = ExamTester("Mi Examen")
            >>> tester.add_exercise(SumaExercise())
            >>> tester.add_exercise(FactorialExercise())
        """
        # Validar tipo
        if not isinstance(exercise, Exercise):
            raise TypeError(
                f"exercise debe ser instancia de Exercise, "
                f"got {type(exercise).__name__}"
            )

        # Verificar que no haya duplicados
        if any(ex.name == exercise.name for ex in self._exercises):
            raise ValidationError(
                f"Ya existe un ejercicio con nombre '{exercise.name}'"
            )

        # Verificar que file_suffix no esté duplicado
        if any(ex.file_suffix == exercise.file_suffix for ex in self._exercises):
            raise ValidationError(
                f"Ya existe un ejercicio con file_suffix {exercise.file_suffix}"
            )

        self._exercises.append(exercise)
        self._configured['exercises'] = True

        return self

    def set_students_path(self, path: str) -> 'ExamTester':
        """
        Configura la ruta a las carpetas de estudiantes.

        Args:
            path: Ruta a la carpeta que contiene subcarpetas de estudiantes

        Returns:
            self (para builder pattern)

        Raises:
            ValidationError: Si la ruta no existe

        Example:
            >>> tester.set_students_path("./StudentsCode")
        """
        students_path = Path(path)

        if not students_path.exists():
            raise ValidationError(
                f"La ruta de estudiantes no existe: {students_path}"
            )

        if not students_path.is_dir():
            raise ValidationError(
                f"La ruta debe ser un directorio: {students_path}"
            )

        self._students_path = students_path
        self._configured['students_path'] = True

        return self

    def set_results_path(self, path: str) -> 'ExamTester':
        """
        Configura la ruta donde guardar resultados.

        Si la carpeta no existe, se creará automáticamente.

        Args:
            path: Ruta donde guardar resultados

        Returns:
            self (para builder pattern)

        Example:
            >>> tester.set_results_path("./Results")
        """
        results_path = Path(path)
        results_path.mkdir(parents=True, exist_ok=True)

        self._results_path = results_path
        self._configured['results_path'] = True

        return self

    # ================================================================
    # GENERACIÓN DE CASOS DE PRUEBA
    # ================================================================

    def generate_test_cases(self, num_random: int = 100,
                           seed: Optional[int] = None) -> 'ExamTester':
        """
        Genera casos de prueba con respuestas pre-calculadas.

        Este método:
        1. Genera casos de prueba (fijos + aleatorios) para cada ejercicio
        2. Ejecuta la solución correcta para obtener respuestas esperadas
        3. Guarda todo en memoria (self._test_cases)
        4. Opcionalmente guarda en archivo JSON

        Args:
            num_random: Número de casos aleatorios por ejercicio
            seed: Semilla para reproducibilidad (opcional)

        Returns:
            self (para builder pattern)

        Raises:
            ConfigurationError: Si no hay ejercicios configurados

        Example:
            >>> tester.generate_test_cases(num_random=100, seed=42)
        """
        self._validate_for_generation()

        print(f"\nGenerando casos de prueba para {len(self._exercises)} ejercicio(s)...")
        print(f"  Casos aleatorios por ejercicio: {num_random}")
        if seed is not None:
            print(f"  Semilla: {seed}")

        self._test_cases = {}

        for exercise in self._exercises:
            print(f"\n  Procesando ejercicio '{exercise.name}'...")

            # Obtener generador y solución
            generator = exercise.get_test_generator()
            solution_func = exercise.get_solution()

            # Generar casos (fijos + aleatorios)
            input_cases = generator.generate_all_cases(num_random, seed)
            print(f"    - Casos fijos: {generator.get_num_fixed_cases()}")
            print(f"    - Casos aleatorios: {num_random}")
            print(f"    - Total: {len(input_cases)}")

            # Ejecutar solución correcta para cada caso
            cases_with_outputs = []
            for caso in input_cases:
                output, error = self._execute_solution(solution_func, caso)
                cases_with_outputs.append({
                    "inputs": list(caso),
                    "expected_output": output,
                    "expected_error": error
                })

            self._test_cases[exercise.name] = cases_with_outputs
            print(f"    ✓ Respuestas esperadas generadas")

        self._configured['test_cases_generated'] = True
        print(f"\n✓ Casos de prueba generados exitosamente")

        return self

    def save_test_cases(self, filepath: Optional[str] = None) -> 'ExamTester':
        """
        Guarda los casos de prueba generados en un archivo JSON.

        Args:
            filepath: Ruta del archivo (opcional). Si no se proporciona,
                     se guarda en results_path/test_cases.json

        Returns:
            self (para builder pattern)

        Raises:
            ConfigurationError: Si no se han generado casos de prueba

        Example:
            >>> tester.save_test_cases("./ExamContent/test_cases.json")
        """
        if not self._configured['test_cases_generated']:
            raise ConfigurationError(
                "No se han generado casos de prueba. "
                "Ejecuta generate_test_cases() primero"
            )

        if filepath is None:
            if self._results_path is None:
                raise ConfigurationError(
                    "Debes configurar results_path o proporcionar filepath"
                )
            filepath = str(self._results_path / "test_cases.json")

        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self._test_cases, f, indent=2, ensure_ascii=False)

        print(f"✓ Casos guardados en: {output_path}")

        return self

    # ================================================================
    # EVALUACIÓN DE ESTUDIANTES
    # ================================================================

    def evaluate_all(self) -> 'ExamTester':
        """
        Evalúa todos los estudiantes en students_path.

        Este método:
        1. Encuentra todas las carpetas de estudiantes
        2. Evalúa cada estudiante contra los casos de prueba
        3. Almacena resultados en self._results

        Returns:
            self (para builder pattern)

        Raises:
            ConfigurationError: Si falta configuración necesaria

        Example:
            >>> tester.evaluate_all()
        """
        self._validate_for_evaluation()

        print("\n" + "=" * 70)
        print(f"Evaluando estudiantes en: {self._students_path}")
        print("=" * 70)

        # Obtener lista de estudiantes
        student_folders = [
            folder for folder in self._students_path.iterdir()
            if folder.is_dir()
        ]

        if not student_folders:
            print("\n⚠ No se encontraron carpetas de estudiantes")
            self._results = []
            return self

        student_folders.sort(key=lambda f: f.name)
        print(f"\nEncontrados {len(student_folders)} estudiantes")

        # Crear evaluador
        evaluator = StudentEvaluator(self._exercises, self._test_cases)

        # Evaluar cada estudiante
        self._results = []
        for i, folder in enumerate(student_folders, 1):
            student_name = folder.name
            print(f"\n[{i}/{len(student_folders)}] Evaluando: {student_name}")

            try:
                resultado = evaluator.evaluate_student(student_name, folder)
                self._results.append(resultado)

                # Mostrar resumen rápido
                if 'error' in resultado:
                    print(f"  ✗ Error: {resultado['error']}")
                else:
                    total_pasados = sum(
                        ej.get('casos_pasados', 0)
                        for ej in resultado.get('ejercicios', [])
                        if 'error' not in ej
                    )
                    total_casos = sum(
                        ej.get('total_casos', 0)
                        for ej in resultado.get('ejercicios', [])
                        if 'error' not in ej
                    )
                    print(f"  ✓ Casos pasados: {total_pasados}/{total_casos}")

            except Exception as e:
                print(f"  ✗ Error inesperado: {e}")
                self._results.append({
                    'nombre_estudiante': student_name,
                    'error': f'Error inesperado durante evaluación: {str(e)}'
                })

        self._configured['students_evaluated'] = True

        print("\n" + "=" * 70)
        print(f"✓ Evaluación completada: {len(self._results)} estudiantes")
        print("=" * 70)

        return self

    # ================================================================
    # GENERACIÓN DE REPORTES
    # ================================================================

    def generate_reports(self, formats: List[str] = ['json', 'markdown']) -> 'ExamTester':
        """
        Genera reportes de evaluación.

        Args:
            formats: Lista de formatos ('json', 'markdown', o ambos)

        Returns:
            self (para builder pattern)

        Raises:
            ConfigurationError: Si no se han evaluado estudiantes o
                               si no se ha configurado results_path

        Example:
            >>> tester.generate_reports(formats=['json', 'markdown'])
        """
        if not self._configured['students_evaluated']:
            raise ConfigurationError(
                "No hay resultados para reportar. "
                "Ejecuta evaluate_all() primero"
            )

        if self._results_path is None:
            raise ConfigurationError(
                "Debes configurar results_path antes de generar reportes"
            )

        print("\n" + "=" * 70)
        print("Generando reportes...")
        print("=" * 70)

        # Crear generador de reportes
        reporter = ReportGenerator(
            self.exam_name,
            self._exercises,
            self._results
        )

        # Timestamp para nombres de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generar reportes según formatos solicitados
        for formato in formats:
            if formato.lower() == 'json':
                filepath = self._results_path / f"resultados_{timestamp}.json"
                reporter.generate_json(filepath)
                print(f"✓ JSON:     {filepath}")

            elif formato.lower() == 'markdown':
                filepath = self._results_path / f"reporte_{timestamp}.md"
                reporter.generate_markdown(filepath)
                print(f"✓ Markdown: {filepath}")

            else:
                print(f"⚠ Formato desconocido: {formato}")

        print("=" * 70)

        return self

    # ================================================================
    # MÉTODOS DE VALIDACIÓN
    # ================================================================

    def _validate_for_generation(self):
        """
        Valida que la configuración sea suficiente para generar casos.

        Raises:
            ConfigurationError: Si falta configuración
        """
        required = ['exam_name', 'exercises']
        missing = [k for k in required if not self._configured[k]]

        if missing:
            raise ConfigurationError(
                f"No se pueden generar casos de prueba. "
                f"Falta configurar: {', '.join(missing)}"
            )

    def _validate_for_evaluation(self):
        """
        Valida que la configuración sea suficiente para evaluar.

        Raises:
            ConfigurationError: Si falta configuración
        """
        required = ['exam_name', 'exercises', 'students_path', 'test_cases_generated']
        missing = [k for k in required if not self._configured[k]]

        if missing:
            raise ConfigurationError(
                f"No se puede evaluar estudiantes. "
                f"Falta: {', '.join(missing)}"
            )

    # ================================================================
    # MÉTODOS AUXILIARES
    # ================================================================

    @staticmethod
    def _execute_solution(func, args):
        """
        Ejecuta la solución correcta y captura resultado o error.

        Args:
            func: Función de solución
            args: Tupla de argumentos

        Returns:
            Tupla (resultado, error_msg)
        """
        try:
            resultado = func(*args)
            return resultado, None
        except Exception as e:
            return None, f"{type(e).__name__}: {str(e)}"

    # ================================================================
    # PROPIEDADES
    # ================================================================

    @property
    def exercises(self) -> List[Exercise]:
        """Lista de ejercicios configurados"""
        return self._exercises.copy()

    @property
    def num_exercises(self) -> int:
        """Número de ejercicios configurados"""
        return len(self._exercises)

    @property
    def is_configured(self) -> bool:
        """Indica si el tester está completamente configurado"""
        return all(self._configured.values())

    # ================================================================
    # REPRESENTACIÓN
    # ================================================================

    def __repr__(self):
        """Representación técnica del tester"""
        return (f"<ExamTester(exam='{self.exam_name}', "
                f"exercises={self.num_exercises}, "
                f"configured={self.is_configured})>")

    def __str__(self):
        """Representación amigable del tester"""
        status = []
        if self._configured['exercises']:
            status.append(f"{self.num_exercises} ejercicio(s)")
        if self._configured['test_cases_generated']:
            status.append("casos generados")
        if self._configured['students_evaluated']:
            status.append("evaluación completa")

        status_str = ", ".join(status) if status else "sin configurar"
        return f"ExamTester '{self.exam_name}' [{status_str}]"
