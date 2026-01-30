"""
Script para generar todos los casos de prueba y guardarlos en JSON.
Ejecutar este script UNA VEZ antes de correr el tester.

Lee la configuracion de config.py y los generadores de ExamContent/input.py.
Los generadores deben seguir la convencion: generar_casos_{name}(num_casos)
"""

import json
import sys
from pathlib import Path

# Agregar directorio raiz al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

# Agregar ExamContent al path para importar generadores
sys.path.insert(0, str(Path(__file__).parent.parent / "ExamContent"))
import input as input_generator


def main():
    """
    Genera todos los casos de prueba y los guarda en ExamContent/test_cases.json
    """
    exam = config.EXAM_CONFIG
    exercises = exam['exercises']
    num_random = exam.get('num_random_cases', 100)

    if not exercises:
        print("No hay ejercicios configurados en config.py")
        return

    print("Generando casos de prueba...")

    all_cases = {}

    for ex in exercises:
        name = ex['name']
        num_fixed = ex['num_fixed_cases']
        total_cases = num_random + num_fixed
        generator_name = f"generar_casos_{name}"

        if hasattr(input_generator, generator_name):
            generator_func = getattr(input_generator, generator_name)
            cases = generator_func(total_cases)
            all_cases[name] = cases
            print(f"  - Casos para '{name}': {len(cases)}")
        else:
            print(f"  ADVERTENCIA: No se encontro generador '{generator_name}' en ExamContent/input.py")

    if not all_cases:
        print("No se generaron casos. Verifica que ExamContent/input.py tenga los generadores.")
        return

    archivo_salida = Path(__file__).parent.parent / "ExamContent" / "test_cases.json"

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)

    print(f"Casos guardados en: {archivo_salida}")


if __name__ == '__main__':
    main()
