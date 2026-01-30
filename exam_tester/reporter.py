"""
Generador de reportes de evaluación.

Este módulo proporciona la clase ReportGenerator que genera reportes
en diferentes formatos (JSON, Markdown) con los resultados de evaluación.

Example:
    Uso interno desde ExamTester:

    >>> reporter = ReportGenerator(exam_name, exercises, results)
    >>> reporter.generate_json("./Results/resultados.json")
    >>> reporter.generate_markdown("./Results/reporte.md")
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .exercise import Exercise


class ReportGenerator:
    """
    Generador de reportes de evaluación.

    Genera reportes en formato JSON y Markdown con:
    - Resumen general por ejercicio
    - Resultados detallados por estudiante
    - Estadísticas de casos fijos
    - Detalles de fallos (opcional)

    Args:
        exam_name: Nombre del examen
        exercises: Lista de ejercicios evaluados
        results: Lista de resultados de estudiantes

    Example:
        >>> reporter = ReportGenerator("Primer Parcial", exercises, results)
        >>> reporter.generate_json("resultados.json")
        >>> reporter.generate_markdown("reporte.md")
    """

    def __init__(self, exam_name: str, exercises: List[Exercise],
                 results: List[Dict[str, Any]]):
        """
        Inicializa el generador de reportes.

        Args:
            exam_name: Nombre del examen
            exercises: Lista de ejercicios
            results: Lista de resultados de evaluación
        """
        self.exam_name = exam_name
        self.exercises = exercises
        self.results = results
        self.timestamp = datetime.now()

    def generate_json(self, filepath: Path,
                     include_details: bool = True) -> Path:
        """
        Genera reporte en formato JSON.

        Args:
            filepath: Ruta donde guardar el archivo
            include_details: Si incluir detalles de fallos

        Returns:
            Ruta al archivo generado

        Example:
            >>> reporter.generate_json(Path("./Results/resultados.json"))
            Path('./Results/resultados.json')
        """
        output = {
            'examen': self.exam_name,
            'fecha': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'total_estudiantes': len(self.results),
            'ejercicios': [ex.name for ex in self.exercises],
            'resultados': self.results if include_details else self._strip_details(self.results)
        }

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return filepath

    def generate_markdown(self, filepath: Path) -> Path:
        """
        Genera reporte en formato Markdown.

        Args:
            filepath: Ruta donde guardar el archivo

        Returns:
            Ruta al archivo generado

        Example:
            >>> reporter.generate_markdown(Path("./Results/reporte.md"))
            Path('./Results/reporte.md')
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Encabezado
            f.write(f"# Reporte de Evaluación - {self.exam_name}\n\n")
            f.write(f"**Fecha:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total de estudiantes evaluados:** {len(self.results)}\n\n")

            # Resumen general
            f.write("## Resumen General\n\n")
            self._write_summary(f)

            # Resultados por estudiante
            f.write("\n## Resultados por Estudiante\n\n")
            self._write_student_results(f)

        return filepath

    def _write_summary(self, f):
        """
        Escribe resumen general al archivo.

        Args:
            f: Archivo abierto para escritura
        """
        # Calcular estudiantes perfectos por ejercicio
        perfect_counts = {ex.name: 0 for ex in self.exercises}
        error_count = 0

        for resultado in self.results:
            if 'error' in resultado:
                error_count += 1
                continue

            if 'ejercicios' in resultado:
                for ejercicio in resultado['ejercicios']:
                    if 'error' in ejercicio:
                        continue

                    ex_name = self._find_exercise_name_by_function(
                        ejercicio.get('nombre_funcion')
                    )

                    if ex_name and ex_name in perfect_counts:
                        pasados = ejercicio.get('casos_pasados', 0)
                        total = ejercicio.get('total_casos', 0)
                        if pasados == total and total > 0:
                            perfect_counts[ex_name] += 1

        # Escribir resumen
        for i, ex in enumerate(self.exercises, 1):
            f.write(
                f"- **Ejercicio {i} ({ex.function_name}):** "
                f"{perfect_counts[ex.name]}/{len(self.results)} "
                f"estudiantes con solución perfecta\n"
            )

        f.write(
            f"- **Estudiantes con errores de evaluación:** {error_count}\n"
        )

    def _write_student_results(self, f):
        """
        Escribe resultados por estudiante al archivo.

        Args:
            f: Archivo abierto para escritura
        """
        for resultado in self.results:
            nombre = resultado.get('nombre_estudiante', 'Desconocido')
            f.write(f"### {nombre}\n\n")

            # Manejar errores generales
            if 'error' in resultado:
                f.write(f"**Error:** {resultado['error']}\n\n")
                continue

            if 'ejercicios' not in resultado:
                f.write("**Error:** No se encontraron ejercicios evaluados\n\n")
                continue

            # Tabla de resultados
            f.write(
                "| Ejercicio | Casos Pasados | Casos Fallidos | "
                "Casos con Error | Total | Casos Fijos Pasados |\n"
            )
            f.write(
                "|-----------|---------------|----------------|"
                "-----------------|-------|--------------------|\n"
            )

            for ejercicio in resultado['ejercicios']:
                if 'error' in ejercicio:
                    nombre_ej = ejercicio.get('nombre_funcion', 'Desconocido')
                    f.write(
                        f"| {nombre_ej} | - | - | - | - | "
                        f"Error: {ejercicio['error']} |\n"
                    )
                else:
                    self._write_exercise_row(f, ejercicio)

            f.write("\n---\n\n")

    def _write_exercise_row(self, f, ejercicio: Dict[str, Any]):
        """
        Escribe una fila de la tabla de resultados.

        Args:
            f: Archivo abierto
            ejercicio: Datos del ejercicio
        """
        nombre_ej = ejercicio.get('nombre_funcion', 'Desconocido')
        pasados = ejercicio.get('casos_pasados', 0)
        fallidos = ejercicio.get('casos_fallidos', 0)
        errores = ejercicio.get('casos_error', 0)
        total = ejercicio.get('total_casos', 0)

        # Casos fijos
        fijos_total = ejercicio.get('casos_fijados_total', 0)
        fijos_pasados = ejercicio.get('casos_fijados_pasados', 0)

        if fijos_total > 0:
            porcentaje = (fijos_pasados / fijos_total) * 100
            fijos_str = f"{fijos_pasados}/{fijos_total} ({porcentaje:.1f}%)"
        else:
            fijos_str = "N/A"

        # Estado
        estado = "✓" if pasados == total else "✗"

        f.write(
            f"| {nombre_ej} [{estado}] | {pasados} | {fallidos} | "
            f"{errores} | {total} | {fijos_str} |\n"
        )

    def _find_exercise_name_by_function(self, func_name: str) -> str:
        """
        Encuentra el nombre del ejercicio por nombre de función.

        Args:
            func_name: Nombre de la función

        Returns:
            Nombre del ejercicio o cadena vacía
        """
        for ex in self.exercises:
            if ex.function_name == func_name:
                return ex.name
        return ""

    @staticmethod
    def _strip_details(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remueve detalles de fallos para reportes compactos.

        Args:
            results: Resultados completos

        Returns:
            Resultados sin detalles de fallos
        """
        clean_results = []
        for result in results:
            clean_result = result.copy()
            if 'ejercicios' in clean_result:
                clean_ejercicios = []
                for ej in clean_result['ejercicios']:
                    clean_ej = ej.copy()
                    clean_ej.pop('detalles_fallos', None)
                    clean_ejercicios.append(clean_ej)
                clean_result['ejercicios'] = clean_ejercicios
            clean_results.append(clean_result)
        return clean_results
