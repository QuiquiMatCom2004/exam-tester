"""
Registro de funciones de comparacion de resultados.
Cada funcion recibe (esperado, obtenido) y retorna bool.
Agregar nuevos comparadores aqui para nuevos tipos de ejercicio.
"""


def default_equal(esperado, obtenido):
    """Comparacion directa de igualdad."""
    return esperado == obtenido


def list_equal(esperado, obtenido):
    """Compara dos listas elemento a elemento."""
    if not isinstance(esperado, list) or not isinstance(obtenido, list):
        return esperado == obtenido
    if len(esperado) != len(obtenido):
        return False
    return all(e == o for e, o in zip(esperado, obtenido))


def tuple_result(esperado, obtenido):
    """
    Para funciones que retornan tuplas (bool, valor).
    Si ambas retornan un primer elemento falsy, se consideran iguales.
    De lo contrario compara elemento a elemento.
    """
    if not isinstance(esperado, tuple) or not isinstance(obtenido, tuple):
        return False
    if not esperado[0] and not obtenido[0]:
        return True
    return all(e == o for e, o in zip(esperado, obtenido))


# Registro: mapea nombres string a funciones
COMPARATORS = {
    "default": default_equal,
    "list_equal": list_equal,
    "tuple_result": tuple_result,
}


def get_comparator(name):
    """Busca un comparador por nombre. Si no existe, usa default."""
    return COMPARATORS.get(name, default_equal)
