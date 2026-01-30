"""
Archivo de configuracion del examen.
Editar este archivo para cada nuevo examen.
"""

EXAM_CONFIG = {
    # Nombre del examen (aparece en los reportes)
    "exam_name": "Nombre del Examen",

    # Cantidad de casos aleatorios a generar por ejercicio
    "num_random_cases": 100,

    # Lista de ejercicios
    # Cada ejercicio define:
    #   - name: identificador del ejercicio (usado como key en test_cases.json)
    #   - function_name: nombre de la funcion que el estudiante debe implementar
    #   - file_suffix: sufijo del archivo del estudiante ({nombre}_{suffix}.py)
    #   - num_fixed_cases: cantidad de casos fijos/edge cases al inicio de la lista
    #   - comparator: nombre del comparador a usar (ver Tester/comparators.py)
    "exercises": [
        # Ejemplo:
        # {
        #     "name": "mi_ejercicio",
        #     "function_name": "mi_funcion",
        #     "file_suffix": 1,
        #     "num_fixed_cases": 5,
        #     "comparator": "default",
        # },
    ]
}
