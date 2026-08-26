"""
Funciones de comparación para validar resultados de ejercicios.

Este módulo proporciona comparadores que determinan si la respuesta de un
estudiante es equivalente a la respuesta esperada.

Comparadores disponibles:
- default: Igualdad directa (==)
- list_equal: Compara listas elemento a elemento
- tuple_result: Para funciones que retornan (bool, valor)
- json_equal: Compara estructuras JSON (dicts/listas) con tolerancia para floats

Example:
    Usar comparador personalizado en un ejercicio:

    >>> class MiEjercicio(Exercise):
    ...     def __init__(self):
    ...         super().__init__(
    ...             name="mi_ejercicio",
    ...             function_name="mi_funcion",
    ...             file_suffix=1,
    ...             comparator="list_equal"  # Usar comparador de listas
    ...         )

    Agregar comparador personalizado:

    >>> from exam_tester.comparators import COMPARATORS
    >>>
    >>> def mi_comparador(esperado, obtenido):
    ...     # Lógica personalizada
    ...     return esperado == obtenido
    >>>
    >>> COMPARATORS["mi_comparador"] = mi_comparador
"""

from typing import Any, Callable


def default_equal(esperado: Any, obtenido: Any) -> bool:
    """
    Comparación directa de igualdad usando ==.

    Este es el comparador por defecto. Funciona para la mayoría de
    tipos de datos: int, float, str, bool, None, etc.

    Args:
        esperado: Valor esperado
        obtenido: Valor obtenido del estudiante

    Returns:
        True si son iguales, False en caso contrario

    Example:
        >>> default_equal(42, 42)
        True
        >>> default_equal("hola", "hola")
        True
        >>> default_equal(3.14, 3.14)
        True
        >>> default_equal(42, 43)
        False
    """
    return esperado == obtenido


def list_equal(esperado: Any, obtenido: Any) -> bool:
    """
    Compara dos listas elemento a elemento.

    Este comparador:
    1. Verifica que ambos sean listas
    2. Verifica que tengan la misma longitud
    3. Compara cada elemento con ==

    Útil para ejercicios que retornan listas, ya que verifica
    que los elementos estén en el mismo orden.

    Args:
        esperado: Lista esperada
        obtenido: Lista obtenida del estudiante

    Returns:
        True si son listas iguales, False en caso contrario

    Example:
        >>> list_equal([1, 2, 3], [1, 2, 3])
        True
        >>> list_equal([1, 2, 3], [3, 2, 1])
        False
        >>> list_equal([1, 2], [1, 2, 3])
        False
        >>> list_equal([1, 2, 3], "not a list")
        False
    """
    # Si no son listas, usar comparación directa
    if not isinstance(esperado, list) or not isinstance(obtenido, list):
        return esperado == obtenido

    # Verificar longitud
    if len(esperado) != len(obtenido):
        return False

    # Comparar elemento a elemento
    return all(e == o for e, o in zip(esperado, obtenido))


def tuple_result(esperado: Any, obtenido: Any) -> bool:
    """
    Para funciones que retornan tuplas (bool, valor).

    Este comparador es útil para funciones que retornan un estado
    de éxito/fallo junto con un valor:
    - (True, valor): Operación exitosa
    - (False, None): Operación fallida

    Lógica:
    - Si ambos tienen primer elemento falsy (False, 0, None),
      se consideran iguales (ambos fallaron)
    - De lo contrario, compara elemento a elemento

    Args:
        esperado: Tupla esperada (bool, valor)
        obtenido: Tupla obtenida (bool, valor)

    Returns:
        True si son equivalentes, False en caso contrario

    Example:
        >>> # Ambos exitosos con mismo valor
        >>> tuple_result((True, 42), (True, 42))
        True
        >>>
        >>> # Ambos fallidos (primer elemento falsy)
        >>> tuple_result((False, None), (False, None))
        True
        >>> tuple_result((False, "error1"), (False, "error2"))
        True
        >>>
        >>> # Uno exitoso, otro fallido
        >>> tuple_result((True, 42), (False, None))
        False
        >>>
        >>> # Exitosos pero diferentes valores
        >>> tuple_result((True, 42), (True, 43))
        False
    """
    # Validar que ambos sean tuplas
    if not isinstance(esperado, tuple) or not isinstance(obtenido, tuple):
        return False

    # Si ambos tienen primer elemento falsy, son equivalentes
    # (ambos fallaron, no importa el valor del segundo elemento)
    if not esperado[0] and not obtenido[0]:
        return True

    # De lo contrario, comparar elemento a elemento
    if len(esperado) != len(obtenido):
        return False
    return all(e == o for e, o in zip(esperado, obtenido))


def json_equal(esperado: Any, obtenido: Any, epsilon: float = 1e-6) -> bool:
    """
    Compara estructuras JSON (dicts, listas, valores) recursivamente.

    Maneja correctamente:
    - Dicts: compara que tengan las mismas claves y valores equivalentes
    - Listas: compara elemento a elemento en orden
    - Floats: usa tolerancia epsilon para evitar errores de precisión
    - int vs float: 1 y 1.0 se consideran iguales
    - Otros tipos: comparación directa con ==

    Args:
        esperado: Estructura JSON esperada
        obtenido: Estructura JSON obtenida del estudiante
        epsilon: Tolerancia para comparación de floats (default: 1e-6)

    Returns:
        True si son equivalentes, False en caso contrario

    Example:
        >>> json_equal({"a": 1.0}, {"a": 1.0})
        True
        >>> json_equal({"a": 1.0000001}, {"a": 1.0})
        True
        >>> json_equal([{"x": 1}, {"x": 2}], [{"x": 1}, {"x": 2}])
        True
        >>> json_equal({"a": 1}, {"a": 2})
        False
        >>> json_equal([1, 2], [1, 2, 3])
        False
    """
    if isinstance(esperado, dict) and isinstance(obtenido, dict):
        if set(esperado.keys()) != set(obtenido.keys()):
            return False
        return all(
            json_equal(esperado[k], obtenido[k], epsilon)
            for k in esperado
        )

    if isinstance(esperado, list) and isinstance(obtenido, list):
        if len(esperado) != len(obtenido):
            return False
        return all(
            json_equal(e, o, epsilon)
            for e, o in zip(esperado, obtenido)
        )

    if isinstance(esperado, (int, float)) and isinstance(obtenido, (int, float)):
        return abs(float(esperado) - float(obtenido)) < epsilon

    return esperado == obtenido


# ================================================================
# REGISTRO DE COMPARADORES
# ================================================================

COMPARATORS: dict[str, Callable[[Any, Any], bool]] = {
    "default": default_equal,
    "list_equal": list_equal,
    "tuple_result": tuple_result,
    "json_equal": json_equal,
}
"""
Registro global de comparadores disponibles.

Puedes agregar comparadores personalizados:

Example:
    >>> def float_approx(esperado, obtenido, epsilon=1e-6):
    ...     '''Compara floats con tolerancia'''
    ...     return abs(esperado - obtenido) < epsilon
    >>>
    >>> COMPARATORS["float_approx"] = float_approx
"""


def get_comparator(name: str) -> Callable[[Any, Any], bool]:
    """
    Obtiene un comparador por nombre.

    Si el nombre no existe en el registro, retorna el comparador
    por defecto (default_equal).

    Args:
        name: Nombre del comparador

    Returns:
        Función comparadora

    Example:
        >>> comp = get_comparator("list_equal")
        >>> comp([1, 2], [1, 2])
        True
        >>>
        >>> # Si no existe, usa default
        >>> comp = get_comparator("no_existe")
        >>> comp(42, 42)
        True
    """
    return COMPARATORS.get(name, default_equal)


def register_comparator(name: str, func: Callable[[Any, Any], bool]):
    """
    Registra un comparador personalizado.

    Args:
        name: Nombre del comparador
        func: Función comparadora con firma (esperado, obtenido) -> bool

    Raises:
        ValueError: Si name ya existe en el registro
        TypeError: Si func no es callable

    Example:
        >>> def set_equal(esperado, obtenido):
        ...     '''Compara conjuntos sin importar orden'''
        ...     return set(esperado) == set(obtenido)
        >>>
        >>> register_comparator("set_equal", set_equal)
    """
    if name in COMPARATORS:
        raise ValueError(f"El comparador '{name}' ya existe")

    if not callable(func):
        raise TypeError(f"func debe ser callable, got {type(func).__name__}")

    COMPARATORS[name] = func
