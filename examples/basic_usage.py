"""
Ejemplo básico de uso del framework ExamTester.

Este ejemplo muestra cómo:
1. Crear ejercicios simples usando generadores predefinidos
2. Configurar el tester con builder pattern
3. Generar casos de prueba con semilla para reproducibilidad
4. Evaluar estudiantes y generar reportes

Para ejecutar este ejemplo:
    python examples/basic_usage.py
"""

import sys
from pathlib import Path

# Agregar el paquete al path (solo para desarrollo)
sys.path.insert(0, str(Path(__file__).parent.parent))

from exam_tester import Exercise
from exam_tester.generators import IntegerPairGenerator, SingleIntegerGenerator


# ===================================================================
# PASO 1: Definir ejercicios
# ===================================================================

class SumaExercise(Exercise):
    """
    Ejercicio simple: suma de dos números enteros.

    Los estudiantes deben implementar:
        def suma(a, b):
            return a + b
    """

    def __init__(self):
        super().__init__(
            name="suma",
            function_name="suma",
            file_suffix=1,
            comparator="default"
        )

    def get_solution(self):
        """Solución correcta: suma simple"""
        return lambda a, b: a + b

    def get_test_generator(self):
        """
        Generador de casos para suma.

        Casos fijos:
        - (0, 0): Ambos ceros
        - (1, 1): Positivos pequeños
        - (-1, 1): Negativo y positivo
        - (100, -100): Valores medios
        - (1000, -1000): Valores extremos

        Casos aleatorios: Pares de enteros entre -1000 y 1000
        """
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
    """
    Ejercicio: cálculo de factorial.

    Los estudiantes deben implementar:
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
    """

    def __init__(self):
        super().__init__(
            name="factorial",
            function_name="factorial",
            file_suffix=2,
            comparator="default"
        )

    def get_solution(self):
        """Solución correcta: factorial recursivo"""
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        return factorial

    def get_test_generator(self):
        """
        Generador de casos para factorial.

        Casos fijos:
        - 0: Caso base
        - 1: Caso base
        - 5: Caso pequeño
        - 10: Caso medio
        - 20: Caso grande

        Casos aleatorios: Enteros entre 0 y 20
        """
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
# PASO 2: Configurar y ejecutar el tester
# ===================================================================

def main():
    """
    Función principal que configura y ejecuta el tester.

    NOTA: Esta función está comentada porque necesita que la clase
    ExamTester esté implementada. Una vez implementada, descomenta
    el código para probar el ejemplo.
    """

    print("=" * 60)
    print("Ejemplo Básico - ExamTester v2.0")
    print("=" * 60)

    # TODO: Descomentar cuando ExamTester esté implementado
    """
    from exam_tester import ExamTester

    # Crear tester con builder pattern
    tester = (ExamTester("Primer Parcial")
        # Agregar ejercicios
        .add_exercise(SumaExercise())
        .add_exercise(FactorialExercise())

        # Configurar rutas
        .set_students_path("./StudentsCode")
        .set_results_path("./Results")

        # Generar casos de prueba (100 casos aleatorios por ejercicio)
        # Usando semilla 42 para reproducibilidad
        .generate_test_cases(num_random=100, seed=42)

        # Evaluar todos los estudiantes
        .evaluate_all()

        # Generar reportes en JSON y Markdown
        .generate_reports(formats=['json', 'markdown'])
    )

    print("\n✓ Evaluación completada")
    print("✓ Reportes generados en ./Results")
    """

    # Por ahora, solo mostramos los ejercicios creados
    print("\nEjercicios definidos:")
    print()

    suma = SumaExercise()
    print(f"1. {suma}")
    print(f"   Generador: {suma.get_test_generator().__class__.__name__}")
    print(f"   Casos fijos: {suma.get_test_generator().get_num_fixed_cases()}")
    print()

    factorial = FactorialExercise()
    print(f"2. {factorial}")
    print(f"   Generador: {factorial.get_test_generator().__class__.__name__}")
    print(f"   Casos fijos: {factorial.get_test_generator().get_num_fixed_cases()}")
    print()

    print("=" * 60)
    print("Estructura de carpetas esperada:")
    print("=" * 60)
    print("""
StudentsCode/
├── Juan Perez/
│   ├── Juan_Perez_1.py    # def suma(a, b): ...
│   └── Juan_Perez_2.py    # def factorial(n): ...
├── Maria Lopez/
│   ├── Maria_Lopez_1.py
│   └── Maria_Lopez_2.py
└── Adriana Amador/
    ├── Adriana_Amador_1.py
    └── Adriana_Amador_2.py
    """)


if __name__ == '__main__':
    main()
