"""
Clase base para definir ejercicios.

Este módulo proporciona la clase abstracta Exercise que debe ser heredada
para crear ejercicios personalizados.

Example:
    Ejercicio simple:

    >>> from exam_tester import Exercise
    >>> from exam_tester.generators import IntegerPairGenerator
    >>>
    >>> class SumaExercise(Exercise):
    ...     def __init__(self):
    ...         super().__init__(
    ...             name="suma",
    ...             function_name="suma",
    ...             file_suffix=1
    ...         )
    ...
    ...     def get_solution(self):
    ...         return lambda a, b: a + b
    ...
    ...     def get_test_generator(self):
    ...         return IntegerPairGenerator(min_val=-1000, max_val=1000)
"""

from abc import ABC, abstractmethod
from typing import Callable

from .generators import TestCaseGenerator
from .exceptions import ValidationError


class Exercise(ABC):
    """
    Clase base abstracta para definir un ejercicio.

    Cada ejercicio debe heredar de esta clase e implementar:
    - get_solution(): Retorna la función de solución correcta
    - get_test_generator(): Retorna el generador de casos de prueba

    La clase base proporciona:
    - Validación automática de parámetros
    - Representación string útil para debugging
    - Interfaz consistente para el framework

    Args:
        name: Identificador único del ejercicio. Debe ser un identificador
              Python válido (sin espacios ni caracteres especiales).
              Se usa como clave en el JSON de casos de prueba.
        function_name: Nombre de la función que el estudiante debe implementar.
                       Debe coincidir exactamente con el nombre en su archivo.
        file_suffix: Sufijo del archivo del estudiante.
                     Por ejemplo, si file_suffix=1 y el estudiante se llama
                     "Juan_Perez", se buscará el archivo "Juan_Perez_1.py"
        comparator: Nombre del comparador a usar para validar resultados.
                    Comparadores disponibles:
                    - "default": Igualdad directa (==)
                    - "list_equal": Compara listas elemento a elemento
                    - "tuple_result": Para funciones que retornan (bool, valor)
                    También puedes crear comparadores personalizados.

    Raises:
        ValidationError: Si algún parámetro es inválido

    Example:
        Ejercicio básico:

        >>> class FactorialExercise(Exercise):
        ...     def __init__(self):
        ...         super().__init__(
        ...             name="factorial",
        ...             function_name="factorial",
        ...             file_suffix=2,
        ...             comparator="default"
        ...         )
        ...
        ...     def get_solution(self):
        ...         def factorial(n):
        ...             if n <= 1:
        ...                 return 1
        ...             return n * factorial(n - 1)
        ...         return factorial
        ...
        ...     def get_test_generator(self):
        ...         from exam_tester.generators import SingleIntegerGenerator
        ...         return SingleIntegerGenerator(
        ...             fixed_cases=[(0,), (1,), (5,), (10,), (20,)],
        ...             min_val=0,
        ...             max_val=20
        ...         )
    """

    def __init__(self,
                 name: str,
                 function_name: str,
                 file_suffix: int,
                 comparator: str = "default"):
        """
        Inicializa el ejercicio.

        Args:
            name: Identificador único (debe ser identificador Python válido)
            function_name: Nombre de la función a implementar
            file_suffix: Sufijo del archivo (>= 1)
            comparator: Nombre del comparador (default: "default")

        Raises:
            ValidationError: Si los parámetros no son válidos
        """
        self.name = name
        self.function_name = function_name
        self.file_suffix = file_suffix
        self.comparator = comparator

        # Validar parámetros
        self._validate()

    def _validate(self):
        """
        Valida la configuración del ejercicio.

        Raises:
            ValidationError: Si algún parámetro es inválido
        """
        # Validar name
        if not self.name:
            raise ValidationError("name no puede estar vacío")

        if not self.name.isidentifier():
            raise ValidationError(
                f"name debe ser un identificador Python válido (sin espacios ni "
                f"caracteres especiales): '{self.name}'"
            )

        # Validar function_name
        if not self.function_name:
            raise ValidationError("function_name no puede estar vacío")

        # Validar file_suffix
        if not isinstance(self.file_suffix, int) or self.file_suffix < 1:
            raise ValidationError(
                f"file_suffix debe ser un entero >= 1, got: {self.file_suffix}"
            )

        # Validar que get_solution retorna callable
        try:
            solution = self.get_solution()
            if not callable(solution):
                raise ValidationError(
                    f"get_solution() debe retornar una función callable, "
                    f"got: {type(solution).__name__}"
                )
        except NotImplementedError:
            # Está bien si aún no se implementó (durante construcción de clase)
            pass

        # Validar que get_test_generator retorna TestCaseGenerator
        try:
            generator = self.get_test_generator()
            if not isinstance(generator, TestCaseGenerator):
                raise ValidationError(
                    f"get_test_generator() debe retornar una instancia de "
                    f"TestCaseGenerator, got: {type(generator).__name__}"
                )
        except NotImplementedError:
            # Está bien si aún no se implementó
            pass

    @abstractmethod
    def get_solution(self) -> Callable:
        """
        Retorna la función de solución correcta.

        Esta función se ejecutará para generar las respuestas esperadas
        de los casos de prueba. Debe tener la misma firma que la función
        que implementarán los estudiantes.

        Returns:
            Función que implementa la solución correcta

        Example:
            >>> def get_solution(self):
            ...     def suma(a, b):
            ...         return a + b
            ...     return suma
            >>>
            >>> # O usando lambda para funciones simples:
            >>> def get_solution(self):
            ...     return lambda a, b: a + b
        """
        pass

    @abstractmethod
    def get_test_generator(self) -> TestCaseGenerator:
        """
        Retorna el generador de casos de prueba.

        El generador define tanto los casos fijos (edge cases) como
        la lógica para generar casos aleatorios.

        Returns:
            Instancia de TestCaseGenerator (o subclase)

        Example:
            >>> def get_test_generator(self):
            ...     from exam_tester.generators import IntegerPairGenerator
            ...     return IntegerPairGenerator(
            ...         fixed_cases=[(0, 0), (1, 1), (-1, 1)],
            ...         min_val=-1000,
            ...         max_val=1000
            ...     )
        """
        pass

    def __repr__(self):
        """
        Representación string del ejercicio.

        Returns:
            String descriptivo del ejercicio

        Example:
            >>> ex = SumaExercise()
            >>> print(ex)
            <SumaExercise(name='suma', func='suma', suffix=1)>
        """
        return (f"<{self.__class__.__name__}"
                f"(name='{self.name}', "
                f"func='{self.function_name}', "
                f"suffix={self.file_suffix})>")

    def __str__(self):
        """
        Representación string amigable para el usuario.

        Example:
            >>> ex = SumaExercise()
            >>> print(str(ex))
            Ejercicio 'suma' - función 'suma' (archivo sufijo 1)
        """
        return (f"Ejercicio '{self.name}' - "
                f"función '{self.function_name}' "
                f"(archivo sufijo {self.file_suffix})")
