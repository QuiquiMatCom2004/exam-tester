"""
Ejemplo avanzado: Ejercicio personalizado con generador custom.

Este ejemplo muestra cómo crear un ejercicio más complejo con:
1. Generador de casos personalizado con lógica específica
2. Validación de resultados compleja
3. Casos de prueba con múltiples argumentos

Ejercicio: Búsqueda binaria en lista ordenada
"""

import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from exam_tester import Exercise
from exam_tester.generators import TestCaseGenerator


# ===================================================================
# Generador personalizado para búsqueda binaria
# ===================================================================

class BinarySearchGenerator(TestCaseGenerator):
    """
    Generador personalizado para búsqueda binaria.

    Genera casos que incluyen:
    - Listas vacías
    - Listas con un elemento
    - Búsquedas exitosas (elemento existe)
    - Búsquedas fallidas (elemento no existe)
    - Elementos al inicio, medio y final
    """

    def get_fixed_cases(self):
        """
        Casos fijos que cubren edge cases importantes.
        """
        return [
            # (lista, elemento_buscar) -> índice o -1
            ([], 5),                        # Lista vacía
            ([1], 1),                       # Un elemento (encontrado)
            ([1], 2),                       # Un elemento (no encontrado)
            ([1, 2, 3, 4, 5], 1),          # Encontrar al inicio
            ([1, 2, 3, 4, 5], 3),          # Encontrar en el medio
            ([1, 2, 3, 4, 5], 5),          # Encontrar al final
            ([1, 2, 3, 4, 5], 6),          # No existe (mayor)
            ([1, 2, 3, 4, 5], 0),          # No existe (menor)
            ([1, 3, 5, 7, 9], 4),          # No existe (en medio)
            ([1, 1, 1, 1, 1], 1),          # Todos iguales
            (list(range(100)), 50),        # Lista grande (existe)
            (list(range(100)), 150),       # Lista grande (no existe)
        ]

    def generate_random_cases(self, n, seed=None):
        """
        Genera casos aleatorios con lógica específica.

        Estrategia:
        - 70% de las veces: buscar un elemento que existe
        - 30% de las veces: buscar un elemento que no existe
        - Longitudes variadas de listas
        """
        if seed is not None:
            random.seed(seed)

        cases = []
        for _ in range(n):
            # Generar lista ordenada aleatoria
            length = random.randint(0, 30)
            arr = sorted([random.randint(-100, 100) for _ in range(length)])

            # 70% buscar elemento existente, 30% elemento inexistente
            if arr and random.random() < 0.7:
                # Buscar elemento que existe
                target = random.choice(arr)
            else:
                # Buscar elemento que probablemente no existe
                target = random.randint(-100, 100)

            cases.append((arr, target))

        return cases


# ===================================================================
# Ejercicio de búsqueda binaria
# ===================================================================

class BinarySearchExercise(Exercise):
    """
    Ejercicio: Implementar búsqueda binaria.

    Los estudiantes deben implementar:
        def buscar(arr, target):
            '''
            Busca target en arr (lista ordenada) usando búsqueda binaria.

            Args:
                arr: Lista de enteros ordenada ascendentemente
                target: Entero a buscar

            Returns:
                Índice donde se encuentra target, o -1 si no está
            '''
            # Implementación del estudiante...
    """

    def __init__(self):
        super().__init__(
            name="busqueda_binaria",
            function_name="buscar",
            file_suffix=3,
            comparator="default"
        )

    def get_solution(self):
        """Implementación correcta de búsqueda binaria"""
        def buscar(arr, target):
            left, right = 0, len(arr) - 1

            while left <= right:
                mid = (left + right) // 2

                if arr[mid] == target:
                    return mid
                elif arr[mid] < target:
                    left = mid + 1
                else:
                    right = mid - 1

            return -1

        return buscar

    def get_test_generator(self):
        """Retorna el generador personalizado"""
        return BinarySearchGenerator()


# ===================================================================
# Otro ejemplo: Ordenamiento con generador inline
# ===================================================================

class OrdernarListaExercise(Exercise):
    """
    Ejercicio: Ordenar una lista de enteros.

    Usa CustomGenerator para no crear una clase completa.
    """

    def __init__(self):
        from exam_tester.generators import CustomGenerator

        # Definir generador inline con lambda
        def generar_listas_aleatorias(n, seed=None):
            if seed:
                random.seed(seed)

            cases = []
            for _ in range(n):
                length = random.randint(0, 20)
                lst = [random.randint(-100, 100) for _ in range(length)]
                cases.append((lst,))
            return cases

        self._generator = CustomGenerator(
            fixed_cases=[
                ([],),                          # Lista vacía
                ([1],),                         # Un elemento
                ([3, 1, 2],),                   # Desordenada
                ([1, 2, 3],),                   # Ya ordenada
                ([3, 2, 1],),                   # Orden inverso
                ([1, 1, 1],),                   # Todos iguales
                ([5, 2, 8, 1, 9],),            # Varios elementos
            ],
            random_func=generar_listas_aleatorias
        )

        super().__init__(
            name="ordenar",
            function_name="ordenar",
            file_suffix=4,
            comparator="list_equal"  # Usar comparador de listas
        )

    def get_solution(self):
        """Solución: usar sorted()"""
        return lambda lst: sorted(lst)

    def get_test_generator(self):
        return self._generator


# ===================================================================
# Demo
# ===================================================================

def main():
    print("=" * 70)
    print("Ejemplo Avanzado - Ejercicios Personalizados")
    print("=" * 70)

    # Ejercicio 1: Búsqueda binaria con generador personalizado
    print("\n1. Búsqueda Binaria")
    print("-" * 70)
    busqueda = BinarySearchExercise()
    print(f"   Ejercicio: {busqueda}")
    print(f"   Generador: {busqueda.get_test_generator().__class__.__name__}")
    print(f"   Casos fijos: {busqueda.get_test_generator().get_num_fixed_cases()}")

    # Mostrar algunos casos fijos
    gen = busqueda.get_test_generator()
    print("\n   Ejemplos de casos fijos:")
    for i, caso in enumerate(gen.get_fixed_cases()[:5], 1):
        arr, target = caso
        resultado = busqueda.get_solution()(arr, target)
        print(f"      {i}. buscar({arr[:5]}{'...' if len(arr) > 5 else ''}, {target}) → {resultado}")

    # Ejercicio 2: Ordenamiento con CustomGenerator
    print("\n2. Ordenar Lista")
    print("-" * 70)
    ordenar = OrdernarListaExercise()
    print(f"   Ejercicio: {ordenar}")
    print(f"   Generador: CustomGenerator (inline)")
    print(f"   Casos fijos: {ordenar.get_test_generator().get_num_fixed_cases()}")

    print("\n   Ejemplos de casos fijos:")
    for i, caso in enumerate(ordenar.get_test_generator().get_fixed_cases()[:5], 1):
        lst = caso[0]
        resultado = ordenar.get_solution()(lst.copy())
        print(f"      {i}. ordenar({lst}) → {resultado}")

    print("\n" + "=" * 70)
    print("Ventajas de generadores personalizados:")
    print("=" * 70)
    print("""
✓ Control total sobre la lógica de generación
✓ Puedes implementar estrategias específicas (70% existente, 30% inexistente)
✓ Validación de casos complejos
✓ Reutilizable para ejercicios similares
✓ Casos fijos cubren edge cases críticos
    """)


if __name__ == '__main__':
    main()
