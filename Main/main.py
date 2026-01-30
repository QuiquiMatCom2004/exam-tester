"""
Script principal que coordina la evaluacion de todos los estudiantes.
Inyecta el tester en cada carpeta de estudiante, lo ejecuta y recopila resultados.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Agregar directorio raiz al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class EvaluadorEstudiantes:
    def __init__(self, ruta_base, ruta_tester):
        """
        Inicializa el evaluador.

        Args:
            ruta_base: ruta base del proyecto
            ruta_tester: ruta a la carpeta con el tester
        """
        self.ruta_base = Path(ruta_base)
        self.ruta_tester = Path(ruta_tester)
        self.ruta_exam_content = self.ruta_base / "ExamContent"
        self.ruta_estudiantes = self.ruta_base / "StudentsCode"
        self.ruta_resultados = self.ruta_base / "Results"

        # Crear carpeta de resultados si no existe
        self.ruta_resultados.mkdir(exist_ok=True)

    def inyectar_tester(self, carpeta_estudiante):
        """
        Copia los archivos del tester a la carpeta del estudiante.

        Args:
            carpeta_estudiante: ruta a la carpeta del estudiante
        Returns:
            True si se inyecto correctamente, False en caso contrario
        """
        try:
            # Archivos del framework (Tester/)
            archivos_tester = ['tester.py', 'case_loader.py', 'comparators.py']
            for archivo in archivos_tester:
                origen = self.ruta_tester / archivo
                if not origen.exists():
                    print(f"  Archivo {archivo} no encontrado en {self.ruta_tester}")
                    return False
                shutil.copy2(origen, carpeta_estudiante / archivo)

            # Archivos del examen (ExamContent/)
            archivos_exam = ['correctSolution.py', 'test_cases.json']
            for archivo in archivos_exam:
                origen = self.ruta_exam_content / archivo
                if not origen.exists():
                    print(f"  Archivo {archivo} no encontrado en {self.ruta_exam_content}")
                    return False
                shutil.copy2(origen, carpeta_estudiante / archivo)

            # Config desde la raiz
            config_origen = self.ruta_base / "config.py"
            if not config_origen.exists():
                print(f"  Archivo config.py no encontrado en {self.ruta_base}")
                return False
            shutil.copy2(config_origen, carpeta_estudiante / "config.py")

            return True
        except Exception as e:
            print(f"   Error al inyectar tester: {e}")
            return False

    def ejecutar_tester(self, nombre_estudiante, carpeta_estudiante):
        """
        Ejecuta el tester para un estudiante especifico.

        Args:
            nombre_estudiante: nombre del estudiante
            carpeta_estudiante: ruta a la carpeta del estudiante
        Returns:
            diccionario con resultados o None si hay error
        """
        try:
            resultado = subprocess.run(
                ['python', 'tester.py', nombre_estudiante, str(carpeta_estudiante)],
                cwd=carpeta_estudiante,
                capture_output=True,
                text=True,
                timeout=60
            )

            archivo_json = carpeta_estudiante / f"{nombre_estudiante}_resultados.json"

            if archivo_json.exists():
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    'nombre_estudiante': nombre_estudiante,
                    'error': 'No se genero el archivo de resultados',
                    'stdout': resultado.stdout,
                    'stderr': resultado.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                'nombre_estudiante': nombre_estudiante,
                'error': 'Timeout al ejecutar el tester (>60s)'
            }
        except Exception as e:
            return {
                'nombre_estudiante': nombre_estudiante,
                'error': f'Error al ejecutar tester: {e}'
            }

    def limpiar_archivos_tester(self, carpeta_estudiante):
        """
        Elimina los archivos del tester de la carpeta del estudiante.

        Args:
            carpeta_estudiante: ruta a la carpeta del estudiante
        """
        try:
            archivos_limpiar = [
                'tester.py', 'correctSolution.py', 'case_loader.py',
                'test_cases.json', 'config.py', 'comparators.py'
            ]

            for archivo in archivos_limpiar:
                ruta_archivo = carpeta_estudiante / archivo
                if ruta_archivo.exists():
                    ruta_archivo.unlink()

        except Exception as e:
            print(f"  Error al limpiar archivos: {e}")

    def evaluar_estudiante(self, nombre_estudiante):
        """
        Evalua un estudiante completo.

        Args:
            nombre_estudiante: nombre del estudiante
        Returns:
            diccionario con resultados
        """
        print(f"\nEvaluando: {nombre_estudiante}")
        carpeta_estudiante = self.ruta_estudiantes / nombre_estudiante

        if not carpeta_estudiante.exists():
            print(f"   Carpeta no encontrada")
            return {
                'nombre_estudiante': nombre_estudiante,
                'error': 'Carpeta no encontrada'
            }

        # Inyectar tester
        print(f"  Inyectando tester...")
        if not self.inyectar_tester(carpeta_estudiante):
            return {
                'nombre_estudiante': nombre_estudiante,
                'error': 'No se pudo inyectar el tester'
            }

        # Ejecutar tester
        print(f"  Ejecutando pruebas...")
        resultados = self.ejecutar_tester(nombre_estudiante, carpeta_estudiante)

        # Limpiar archivos
        print(f"  Limpiando archivos temporales...")
        self.limpiar_archivos_tester(carpeta_estudiante)

        # Verificar si hubo errores
        if 'error' in resultados:
            print(f"   Error: {resultados['error']}")
        else:
            print(f"   Evaluacion completada")

        return resultados

    def evaluar_todos(self):
        """
        Evalua todos los estudiantes en la carpeta StudentsCode.

        Returns:
            lista con resultados de todos los estudiantes
        """
        if not self.ruta_estudiantes.exists():
            print(f"Error: Carpeta {self.ruta_estudiantes} no existe")
            return []

        # Obtener lista de estudiantes
        estudiantes = [
            carpeta.name for carpeta in self.ruta_estudiantes.iterdir()
            if carpeta.is_dir()
        ]

        estudiantes.sort()

        print(f"{'='*60}")
        print(f"Evaluando {len(estudiantes)} estudiantes")
        print(f"{'='*60}")

        resultados_todos = []

        for i, nombre_estudiante in enumerate(estudiantes, 1):
            print(f"\n[{i}/{len(estudiantes)}]", end=" ")
            resultado = self.evaluar_estudiante(nombre_estudiante)
            resultados_todos.append(resultado)

        return resultados_todos

    def guardar_resultados(self, resultados):
        """
        Guarda los resultados en un archivo JSON.

        Args:
            resultados: lista de resultados de estudiantes
        Returns:
            ruta al archivo guardado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_json = self.ruta_resultados / f"resultados_{timestamp}.json"

        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*60}")
        print(f"Resultados guardados en: {archivo_json}")
        print(f"{'='*60}")

        return archivo_json

    def generar_reporte_markdown(self, resultados):
        """
        Genera un reporte en formato markdown con los resultados.

        Args:
            resultados: lista de resultados de estudiantes
        Returns:
            ruta al archivo markdown generado
        """
        exam = config.EXAM_CONFIG
        exercises = exam['exercises']

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_md = self.ruta_resultados / f"reporte_{timestamp}.md"

        with open(archivo_md, 'w', encoding='utf-8') as f:
            # Encabezado
            f.write(f"# Reporte de Evaluacion - {exam['exam_name']}\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total de estudiantes evaluados:** {len(resultados)}\n\n")

            # Resumen general
            f.write("## Resumen General\n\n")

            exercise_names = [ex['function_name'] for ex in exercises]
            perfect_counts = {name: 0 for name in exercise_names}
            error_count = 0

            for resultado in resultados:
                if 'error' in resultado:
                    error_count += 1
                    continue

                if 'ejercicios' in resultado:
                    for ejercicio in resultado['ejercicios']:
                        fname = ejercicio.get('nombre_funcion')
                        if fname in perfect_counts and 'error' not in ejercicio:
                            if ejercicio.get('casos_pasados', 0) == ejercicio.get('total_casos', 0):
                                perfect_counts[fname] += 1

            for i, ex in enumerate(exercises, 1):
                fname = ex['function_name']
                f.write(f"- **Ejercicio {i} ({fname}):** {perfect_counts[fname]}/{len(resultados)} estudiantes con solucion correcta\n")

            f.write(f"- **Estudiantes con errores de evaluacion:** {error_count}\n\n")

            # Resultados por estudiante
            f.write("## Resultados por Estudiante\n\n")

            for resultado in resultados:
                nombre = resultado.get('nombre_estudiante', 'Desconocido')
                f.write(f"### {nombre}\n\n")

                if 'error' in resultado:
                    f.write(f"**Error:** {resultado['error']}\n\n")
                    continue

                if 'ejercicios' not in resultado:
                    f.write("**Error:** No se encontraron ejercicios evaluados\n\n")
                    continue

                # Tabla de resultados
                f.write("| Ejercicio | Casos Pasados | Casos Fallidos | Casos con Error | Total | Casos Fijados Pasados |\n")
                f.write("|-----------|---------------|----------------|-----------------|-------|----------------------|\n")

                for ejercicio in resultado['ejercicios']:
                    if 'error' in ejercicio:
                        nombre_ej = ejercicio.get('nombre_funcion', 'Desconocido')
                        f.write(f"| {nombre_ej} | - | - | - | - | Error: {ejercicio['error']} |\n")
                    else:
                        nombre_ej = ejercicio.get('nombre_funcion', 'Desconocido')
                        pasados = ejercicio.get('casos_pasados', 0)
                        fallidos = ejercicio.get('casos_fallidos', 0)
                        errores = ejercicio.get('casos_error', 0)
                        total = ejercicio.get('total_casos', 0)

                        casos_fijados_total = ejercicio.get('casos_fijados_total', 0)
                        casos_fijados_pasados = ejercicio.get('casos_fijados_pasados', 0)
                        porcentaje_fijados = 0
                        if casos_fijados_total > 0:
                            porcentaje_fijados = (casos_fijados_pasados / casos_fijados_total) * 100

                        casos_fijados_str = f"{casos_fijados_pasados}/{casos_fijados_total} ({porcentaje_fijados:.1f}%)"

                        estado = "OK" if pasados == total else "FAIL"
                        f.write(f"| {nombre_ej} [{estado}] | {pasados} | {fallidos} | {errores} | {total} | {casos_fijados_str} |\n")

                f.write("\n---\n\n")

        print(f"Reporte markdown generado en: {archivo_md}")
        return archivo_md


def main():
    """
    Funcion principal.
    """
    # Rutas del proyecto
    ruta_base = Path(__file__).parent.parent
    ruta_tester = ruta_base / "Tester"

    # Verificar que hay ejercicios configurados
    exercises = config.EXAM_CONFIG.get('exercises', [])
    if not exercises:
        print("Error: No hay ejercicios configurados en config.py")
        return

    # Verificar que test_cases.json existe
    test_cases_path = ruta_base / "ExamContent" / "test_cases.json"
    if not test_cases_path.exists():
        print("Error: No se encontro ExamContent/test_cases.json")
        print("Ejecuta primero: python Tester/generate_test_cases.py")
        return

    # Crear evaluador
    evaluador = EvaluadorEstudiantes(ruta_base, ruta_tester)

    # Evaluar todos los estudiantes
    resultados = evaluador.evaluar_todos()

    if not resultados:
        print("No se encontraron estudiantes para evaluar.")
        return

    # Guardar resultados
    evaluador.guardar_resultados(resultados)

    # Generar reporte markdown
    evaluador.generar_reporte_markdown(resultados)

    print("\nProceso completado")


if __name__ == '__main__':
    main()
