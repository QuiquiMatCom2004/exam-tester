"""
Ejemplo completo del flujo de trabajo con ExamTester v2.0.

Este ejemplo demuestra el flujo completo:
1. Definir ejercicios
2. Configurar tester
3. Generar casos de prueba
4. Evaluar estudiantes
5. Generar reportes

Para ejecutar:
    python examples/complete_workflow.py
"""

import sys
from pathlib import Path

# Agregar paquete al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from exam_tester import ExamTester, Exercise
from exam_tester.generators import IntegerPairGenerator, SingleIntegerGenerator


# ===================================================================
# Definir Ejercicios
# ===================================================================

class SumaExercise(Exercise):
    """Ejercicio: suma de dos números"""

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
            fixed_cases=[
                (0, 0),
                (1, 1),
                (-1, 1),
                (100, -100),
                (1000, -1000)
            ],
            min_val=-1000,
            max_val=1000
        )


class FactorialExercise(Exercise):
    """Ejercicio: factorial"""

    def __init__(self):
        super().__init__(
            name="factorial",
            function_name="factorial",
            file_suffix=2,
            comparator="default"
        )

    def get_solution(self):
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        return factorial

    def get_test_generator(self):
        return SingleIntegerGenerator(
            fixed_cases=[
                (0,),
                (1,),
                (5,),
                (10,),
                (15,),
                (20,)
            ],
            min_val=0,
            max_val=20
        )


# ===================================================================
# Flujo Completo
# ===================================================================

def main():
    print("=" * 70)
    print("ExamTester v2.0 - Flujo Completo de Evaluación")
    print("=" * 70)

    # ---------------------------------------------------------------
    # PASO 1: Configurar tester con builder pattern
    # ---------------------------------------------------------------
    print("\n📋 PASO 1: Configurando examen...")

    tester = (ExamTester("Primer Parcial - Demo Completo")
        .add_exercise(SumaExercise())
        .add_exercise(FactorialExercise())
        .set_students_path("./StudentsCode")
        .set_results_path("./Results")
    )

    print(f"✓ Tester configurado: {tester}")

    # ---------------------------------------------------------------
    # PASO 2: Generar casos de prueba
    # ---------------------------------------------------------------
    print("\n🔧 PASO 2: Generando casos de prueba...")

    tester.generate_test_cases(
        num_random=20,  # 20 casos aleatorios para demo rápida
        seed=42          # Semilla para reproducibilidad
    )

    # Opcionalmente guardar casos
    tester.save_test_cases("./Results/test_cases_demo.json")

    # ---------------------------------------------------------------
    # PASO 3: Evaluar estudiantes
    # ---------------------------------------------------------------
    print("\n🎓 PASO 3: Evaluando estudiantes...")

    tester.evaluate_all()

    # ---------------------------------------------------------------
    # PASO 4: Generar reportes
    # ---------------------------------------------------------------
    print("\n📊 PASO 4: Generando reportes...")

    tester.generate_reports(formats=['json', 'markdown'])

    # ---------------------------------------------------------------
    # Resumen Final
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("✅ FLUJO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print("\nArchivos generados:")
    print("  📁 ./Results/")
    print("     ├── test_cases_demo.json    (casos de prueba)")
    print("     ├── resultados_XXXXXX.json  (resultados JSON)")
    print("     └── reporte_XXXXXX.md       (reporte Markdown)")
    print("\nAbre el reporte Markdown para ver resultados detallados.")
    print("=" * 70)


if __name__ == '__main__':
    main()
