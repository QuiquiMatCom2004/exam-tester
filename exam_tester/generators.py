"""
Generadores de casos de prueba para ejercicios.

Este módulo proporciona:
1. TestCaseGenerator: Clase base abstracta para todos los generadores
2. Generadores predefinidos para tipos de datos comunes
3. Generadores personalizables

Example:
    Uso básico con generador predefinido:

    >>> from exam_tester.generators import IntegerPairGenerator
    >>> gen = IntegerPairGenerator(
    ...     fixed_cases=[(0, 0), (1, 1)],
    ...     min_val=-100,
    ...     max_val=100
    ... )
    >>> cases = gen.generate_all_cases(num_random=10, seed=42)
    >>> print(len(cases))  # 2 fijos + 10 aleatorios
    12
"""

import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional, Callable

from .exceptions import GeneratorError


class TestCaseGenerator(ABC):
    """
    Clase base abstracta para generadores de casos de prueba.

    Todos los generadores deben heredar de esta clase e implementar
    los métodos abstractos get_fixed_cases() y generate_random_cases().

    La clase base proporciona:
    - generate_all_cases(): Combina casos fijos + aleatorios
    - get_num_fixed_cases(): Cuenta casos fijos
    - Validación básica

    Example:
        Crear un generador personalizado:

        >>> class MiGenerador(TestCaseGenerator):
        ...     def get_fixed_cases(self):
        ...         return [(0,), (1,), (5,)]
        ...
        ...     def generate_random_cases(self, n, seed=None):
        ...         if seed:
        ...             random.seed(seed)
        ...         return [(random.randint(0, 100),) for _ in range(n)]
    """

    @abstractmethod
    def get_fixed_cases(self) -> List[Tuple[Any, ...]]:
        """
        Retorna casos fijos/especiales (edge cases).

        Los casos fijos son casos críticos que siempre deben probarse,
        como valores límite, casos vacíos, etc.

        Returns:
            Lista de tuplas donde cada tupla contiene los argumentos
            para la función a probar.

        Example:
            >>> def get_fixed_cases(self):
            ...     return [
            ...         (0, 0),      # Caso: ceros
            ...         (1, 1),      # Caso: positivos pequeños
            ...         (-1, 1),     # Caso: negativo y positivo
            ...     ]
        """
        pass

    @abstractmethod
    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[Any, ...]]:
        """
        Genera n casos aleatorios.

        Args:
            n: Número de casos a generar
            seed: Semilla para reproducibilidad (opcional).
                  Si se proporciona, los casos generados serán siempre los mismos.

        Returns:
            Lista de tuplas con argumentos aleatorios

        Example:
            >>> def generate_random_cases(self, n, seed=None):
            ...     if seed is not None:
            ...         random.seed(seed)
            ...     return [(random.randint(0, 100),) for _ in range(n)]
        """
        pass

    def generate_all_cases(self, num_random: int, seed: Optional[int] = None) -> List[Tuple[Any, ...]]:
        """
        Genera todos los casos (fijos + aleatorios).

        Este método combina los casos fijos (que siempre son los mismos)
        con casos aleatorios generados.

        Args:
            num_random: Número de casos aleatorios a generar
            seed: Semilla para reproducibilidad de casos aleatorios

        Returns:
            Lista completa de casos (fijos primero, luego aleatorios)

        Example:
            >>> gen = IntegerPairGenerator()
            >>> casos = gen.generate_all_cases(num_random=100, seed=42)
            >>> # Primero vienen los casos fijos, luego 100 aleatorios
        """
        fixed = self.get_fixed_cases()
        random_cases = self.generate_random_cases(num_random, seed)
        return fixed + random_cases

    def get_num_fixed_cases(self) -> int:
        """
        Retorna el número de casos fijos.

        Returns:
            Cantidad de casos fijos

        Example:
            >>> gen = IntegerPairGenerator()
            >>> gen.get_num_fixed_cases()
            4
        """
        return len(self.get_fixed_cases())


class IntegerPairGenerator(TestCaseGenerator):
    """
    Genera pares de enteros (a, b).

    Útil para funciones que reciben dos argumentos enteros, como:
    - suma(a, b)
    - resta(a, b)
    - multiplicacion(a, b)
    - mcd(a, b)

    Args:
        fixed_cases: Casos fijos personalizados. Si no se proporcionan,
                     usa casos predeterminados (ceros, positivos, negativos, extremos)
        min_val: Valor mínimo para casos aleatorios
        max_val: Valor máximo para casos aleatorios

    Example:
        >>> # Usar casos fijos por defecto
        >>> gen = IntegerPairGenerator(min_val=-1000, max_val=1000)
        >>>
        >>> # Casos fijos personalizados
        >>> gen = IntegerPairGenerator(
        ...     fixed_cases=[(0, 0), (10, 20), (-5, 5)],
        ...     min_val=-100,
        ...     max_val=100
        ... )
    """

    def __init__(self,
                 fixed_cases: Optional[List[Tuple[int, int]]] = None,
                 min_val: int = -1000,
                 max_val: int = 1000):
        self.fixed_cases = fixed_cases or [
            (0, 0),           # Ceros
            (1, 1),           # Positivos pequeños
            (-1, 1),          # Negativo y positivo
            (100, -100),      # Valores medios
            (max_val, min_val)  # Valores extremos
        ]
        self.min_val = min_val
        self.max_val = max_val

    def get_fixed_cases(self) -> List[Tuple[int, int]]:
        return self.fixed_cases

    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[int, int]]:
        if seed is not None:
            random.seed(seed)

        cases = []
        for _ in range(n):
            a = random.randint(self.min_val, self.max_val)
            b = random.randint(self.min_val, self.max_val)
            cases.append((a, b))
        return cases


class SingleIntegerGenerator(TestCaseGenerator):
    """
    Genera enteros individuales (n,).

    Útil para funciones que reciben un solo argumento entero, como:
    - factorial(n)
    - fibonacci(n)
    - es_primo(n)
    - cuadrado(n)

    Args:
        fixed_cases: Casos fijos personalizados
        min_val: Valor mínimo para casos aleatorios
        max_val: Valor máximo para casos aleatorios

    Example:
        >>> gen = SingleIntegerGenerator(
        ...     fixed_cases=[(0,), (1,), (5,), (10,)],
        ...     min_val=0,
        ...     max_val=20
        ... )
    """

    def __init__(self,
                 fixed_cases: Optional[List[Tuple[int]]] = None,
                 min_val: int = 0,
                 max_val: int = 20):
        self.fixed_cases = fixed_cases or [
            (0,),
            (1,),
            (5,),
            (10,),
            (max_val,)
        ]
        self.min_val = min_val
        self.max_val = max_val

    def get_fixed_cases(self) -> List[Tuple[int]]:
        return self.fixed_cases

    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[int]]:
        if seed is not None:
            random.seed(seed)

        return [(random.randint(self.min_val, self.max_val),) for _ in range(n)]


class IntegerListGenerator(TestCaseGenerator):
    """
    Genera listas de enteros ([...],).

    Útil para funciones que procesan listas, como:
    - suma_lista(lst)
    - maximo(lst)
    - ordenar(lst)
    - filtrar_pares(lst)

    Args:
        fixed_cases: Casos fijos personalizados
        min_length: Longitud mínima de listas aleatorias
        max_length: Longitud máxima de listas aleatorias
        min_val: Valor mínimo de elementos
        max_val: Valor máximo de elementos

    Example:
        >>> gen = IntegerListGenerator(
        ...     fixed_cases=[([],), ([1],), ([1, 2, 3],)],
        ...     min_length=0,
        ...     max_length=10,
        ...     min_val=-100,
        ...     max_val=100
        ... )
    """

    def __init__(self,
                 fixed_cases: Optional[List[Tuple[List[int]]]] = None,
                 min_length: int = 0,
                 max_length: int = 10,
                 min_val: int = -100,
                 max_val: int = 100):
        self.fixed_cases = fixed_cases or [
            ([],),              # Lista vacía
            ([1],),             # Un elemento
            ([1, 2, 3],),       # Varios elementos
            ([-1, 0, 1],),      # Negativos, cero, positivos
        ]
        self.min_length = min_length
        self.max_length = max_length
        self.min_val = min_val
        self.max_val = max_val

    def get_fixed_cases(self) -> List[Tuple[List[int]]]:
        return self.fixed_cases

    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[List[int]]]:
        if seed is not None:
            random.seed(seed)

        cases = []
        for _ in range(n):
            length = random.randint(self.min_length, self.max_length)
            lst = [random.randint(self.min_val, self.max_val) for _ in range(length)]
            cases.append((lst,))
        return cases


class StringGenerator(TestCaseGenerator):
    """
    Genera cadenas de texto (str,).

    Útil para funciones que procesan strings, como:
    - contar_vocales(s)
    - invertir_string(s)
    - es_palindromo(s)
    - capitalizar(s)

    Args:
        fixed_cases: Casos fijos personalizados
        min_length: Longitud mínima de strings aleatorios
        max_length: Longitud máxima de strings aleatorios
        charset: Conjunto de caracteres para generar strings

    Example:
        >>> gen = StringGenerator(
        ...     fixed_cases=[("",), ("a",), ("hola",)],
        ...     min_length=0,
        ...     max_length=20,
        ...     charset="abcdefghijklmnopqrstuvwxyz"
        ... )
    """

    def __init__(self,
                 fixed_cases: Optional[List[Tuple[str]]] = None,
                 min_length: int = 0,
                 max_length: int = 20,
                 charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        self.fixed_cases = fixed_cases or [
            ("",),              # String vacío
            ("a",),             # Un carácter
            ("hola",),          # Palabra simple
            ("Hola Mundo",),    # Con espacio y mayúscula
        ]
        self.min_length = min_length
        self.max_length = max_length
        self.charset = charset

    def get_fixed_cases(self) -> List[Tuple[str]]:
        return self.fixed_cases

    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[str]]:
        if seed is not None:
            random.seed(seed)

        cases = []
        for _ in range(n):
            length = random.randint(self.min_length, self.max_length)
            s = ''.join(random.choice(self.charset) for _ in range(length))
            cases.append((s,))
        return cases


class CustomGenerator(TestCaseGenerator):
    """
    Generador personalizado usando funciones lambda.

    Útil cuando necesitas lógica de generación específica pero no quieres
    crear una clase completa.

    Args:
        fixed_cases: Lista de casos fijos
        random_func: Función que genera casos aleatorios.
                     Firma: (n: int, seed: Optional[int]) -> List[Tuple[Any, ...]]

    Example:
        >>> def generar_pares_ordenados(n, seed=None):
        ...     if seed:
        ...         random.seed(seed)
        ...     cases = []
        ...     for _ in range(n):
        ...         a = random.randint(0, 100)
        ...         b = random.randint(a, 100)  # b siempre >= a
        ...         cases.append((a, b))
        ...     return cases
        >>>
        >>> gen = CustomGenerator(
        ...     fixed_cases=[(0, 0), (1, 10)],
        ...     random_func=generar_pares_ordenados
        ... )
    """

    def __init__(self,
                 fixed_cases: List[Tuple[Any, ...]],
                 random_func: Callable[[int, Optional[int]], List[Tuple[Any, ...]]]):
        self.fixed_cases = fixed_cases
        self.random_func = random_func

    def get_fixed_cases(self) -> List[Tuple[Any, ...]]:
        return self.fixed_cases

    def generate_random_cases(self, n: int, seed: Optional[int] = None) -> List[Tuple[Any, ...]]:
        return self.random_func(n, seed)
