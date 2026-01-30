"""
Script para generar todos los casos de prueba y guardarlos en JSON.
Ejecutar este script UNA VEZ antes de correr el tester.

Lee la configuracion de config.py y los generadores de ExamContent/input.py.
Los generadores deben seguir la convencion: generar_casos_{name}(num_casos)

IMPORTANTE: Este script tambien ejecuta la solucion correcta para cada caso
y guarda las respuestas esperadas en el JSON, evitando tener que ejecutar
la solucion correcta por cada estudiante.
"""

import json
import sys
from pathlib import Path

# Agregar directorio raiz al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

# Agregar ExamContent al path para importar generadores y soluciones
sys.path.insert(0, str(Path(__file__).parent.parent / "ExamContent"))
import input as input_generator
import correctSolution


def ejecutar_solucion_correcta(func, args):
    """
    Ejecuta la solucion correcta y captura el resultado o el error.

    Args:
        func: funcion de la solucion correcta
        args: tupla de argumentos
    Returns:
        tupla (resultado, error_msg)
    """
    try:
        resultado = func(*args)
        return resultado, None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}"


def main():
    """
    Genera todos los casos de prueba, ejecuta la solucion correcta para cada uno,
    y guarda tanto las entradas como las salidas esperadas en ExamContent/test_cases.json
    """
    exam = config.EXAM_CONFIG
    exercises = exam['exercises']
    num_random = exam.get('num_random_cases', 100)

    if not exercises:
        print("No hay ejercicios configurados en config.py")
        return

    print("Generando casos de prueba y ejecutando soluciones correctas...")

    all_cases = {}

    for ex in exercises:
        name = ex['name']
        func_name = ex['function_name']
        num_fixed = ex['num_fixed_cases']
        total_cases = num_random + num_fixed
        generator_name = f"generar_casos_{name}"

        # Verificar que existe el generador
        if not hasattr(input_generator, generator_name):
            print(f"  ADVERTENCIA: No se encontro generador '{generator_name}' en ExamContent/input.py")
            continue

        # Verificar que existe la funcion en la solucion correcta
        if not hasattr(correctSolution, func_name):
            print(f"  ADVERTENCIA: No se encontro funcion '{func_name}' en ExamContent/correctSolution.py")
            continue

        # Generar casos de entrada
        generator_func = getattr(input_generator, generator_name)
        input_cases = generator_func(total_cases)

        # Ejecutar solucion correcta para cada caso
        correct_func = getattr(correctSolution, func_name)
        cases_with_outputs = []

        for caso in input_cases:
            output, error = ejecutar_solucion_correcta(correct_func, caso)
            cases_with_outputs.append({
                "inputs": list(caso),
                "expected_output": output,
                "expected_error": error
            })

        all_cases[name] = cases_with_outputs
        print(f"  - Casos para '{name}': {len(cases_with_outputs)} (con respuestas pre-generadas)")

    if not all_cases:
        print("No se generaron casos. Verifica que ExamContent/input.py y ExamContent/correctSolution.py esten correctos.")
        return

    archivo_salida = Path(__file__).parent.parent / "ExamContent" / "test_cases.json"

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)

    print(f"\nCasos guardados en: {archivo_salida}")
    print("Las respuestas esperadas estan pre-generadas, no es necesario ejecutar la solucion correcta por cada estudiante.")


if __name__ == '__main__':
    main()
