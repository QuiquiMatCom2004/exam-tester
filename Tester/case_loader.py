"""
Cargador de casos de prueba desde JSON.
Este modulo carga los casos pre-generados desde ExamContent/test_cases.json.
"""

import json
from pathlib import Path


def generar_todos_los_casos():
    """
    Carga todos los casos de prueba desde el archivo JSON.

    Returns:
        diccionario con casos para cada ejercicio
    """
    archivo_casos = Path(__file__).parent / "test_cases.json"

    if not archivo_casos.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de casos de prueba: {archivo_casos}\n"
            "Ejecuta generate_test_cases.py primero para generar los casos."
        )

    with open(archivo_casos, 'r', encoding='utf-8') as f:
        casos = json.load(f)

    # Convertir las listas JSON a tuplas para todos los ejercicios
    for key in casos:
        casos[key] = [tuple(caso) for caso in casos[key]]

    return casos
