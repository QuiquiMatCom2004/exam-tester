"""
Tester generico para evaluar el codigo de los estudiantes.
Este archivo sera copiado a cada carpeta de estudiante y ejecutado alli.
"""

import json
import sys
import importlib.util
from pathlib import Path


def cargar_modulo(ruta_archivo):
    """
    Carga un modulo de Python desde una ruta de archivo.

    Args:
        ruta_archivo: ruta al archivo .py
    Returns:
        modulo cargado o None si hay error
    """
    try:
        spec = importlib.util.spec_from_file_location("student_module", ruta_archivo)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def ejecutar_con_timeout(func, args, timeout=5):
    """
    Ejecuta una funcion capturando excepciones.

    Args:
        func: funcion a ejecutar
        args: argumentos de la funcion
        timeout: tiempo maximo de ejecucion en segundos (reservado)
    Returns:
        tupla (resultado, error_msg)
    """
    try:
        resultado = func(*args)
        return resultado, None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}"


def probar_funcion(funcion_estudiante, funcion_correcta, casos_prueba,
                   nombre_funcion, num_casos_fijados=0, comparator_func=None):
    """
    Prueba una funcion del estudiante contra la solucion correcta.

    Args:
        funcion_estudiante: funcion del estudiante a probar
        funcion_correcta: funcion correcta de referencia
        casos_prueba: lista de casos de prueba
        nombre_funcion: nombre de la funcion
        num_casos_fijados: numero de casos fijados al inicio de la lista
        comparator_func: funcion de comparacion (esperado, obtenido) -> bool
    Returns:
        diccionario con resultados de las pruebas
    """
    if comparator_func is None:
        comparator_func = lambda e, o: e == o

    resultados = {
        'nombre_funcion': nombre_funcion,
        'total_casos': len(casos_prueba),
        'casos_pasados': 0,
        'casos_fallidos': 0,
        'casos_error': 0,
        'casos_fijados_total': num_casos_fijados,
        'casos_fijados_pasados': 0,
        'detalles_fallos': []
    }

    for i, caso in enumerate(casos_prueba, 1):
        resultado_esperado, error_esperado = ejecutar_con_timeout(
            funcion_correcta, caso
        )

        resultado_estudiante, error_estudiante = ejecutar_con_timeout(
            funcion_estudiante, caso
        )

        es_caso_fijado = (i <= num_casos_fijados)

        if error_estudiante:
            resultados['casos_error'] += 1
            resultados['detalles_fallos'].append({
                'caso_numero': i,
                'entrada': [list(arg) if isinstance(arg, list) else arg for arg in caso],
                'esperado': resultado_esperado if resultado_esperado is not None else 'None',
                'obtenido': f"ERROR: {error_estudiante}",
                'tipo_error': 'excepcion'
            })
        elif not comparator_func(resultado_esperado, resultado_estudiante):
            resultados['casos_fallidos'] += 1
            resultados['detalles_fallos'].append({
                'caso_numero': i,
                'entrada': [list(arg) if isinstance(arg, list) else arg for arg in caso],
                'esperado': resultado_esperado if resultado_esperado is not None else 'None',
                'obtenido': resultado_estudiante if resultado_estudiante is not None else 'None',
                'tipo_error': 'resultado_incorrecto'
            })
        else:
            resultados['casos_pasados'] += 1
            if es_caso_fijado:
                resultados['casos_fijados_pasados'] += 1

    return resultados


def evaluar_estudiante(nombre_estudiante, ruta_carpeta, exercises_config):
    """
    Evalua todos los ejercicios de un estudiante.

    Args:
        nombre_estudiante: nombre del estudiante
        ruta_carpeta: ruta a la carpeta del estudiante
        exercises_config: lista de configuraciones de ejercicios
    Returns:
        diccionario con resultados de la evaluacion
    """
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        import correctSolution
        import case_loader
        from comparators import get_comparator
    except ImportError as e:
        return {
            'error': f'No se pudieron importar los modulos necesarios: {e}',
            'nombre_estudiante': nombre_estudiante
        }

    casos = case_loader.generar_todos_los_casos()

    resultados = {
        'nombre_estudiante': nombre_estudiante,
        'ejercicios': []
    }

    for ex in exercises_config:
        ex_name = ex['name']
        func_name = ex['function_name']
        suffix = ex['file_suffix']
        num_fixed = ex['num_fixed_cases']
        comp_func = get_comparator(ex['comparator'])

        archivo = Path(ruta_carpeta) / f"{nombre_estudiante}_{suffix}.py"

        if not hasattr(correctSolution, func_name):
            resultados['ejercicios'].append({
                'nombre_funcion': func_name,
                'error': f'Solucion correcta no tiene la funcion {func_name}'
            })
            continue

        if archivo.exists():
            modulo = cargar_modulo(archivo)
            if modulo and hasattr(modulo, func_name):
                resultado = probar_funcion(
                    getattr(modulo, func_name),
                    getattr(correctSolution, func_name),
                    casos.get(ex_name, []),
                    func_name,
                    num_casos_fijados=num_fixed,
                    comparator_func=comp_func
                )
                resultados['ejercicios'].append(resultado)
            else:
                resultados['ejercicios'].append({
                    'nombre_funcion': func_name,
                    'error': f'No se pudo cargar la funcion {func_name} o no existe'
                })
        else:
            resultados['ejercicios'].append({
                'nombre_funcion': func_name,
                'error': f'Archivo {archivo.name} no encontrado'
            })

    return resultados


def main():
    """
    Funcion principal que se ejecuta cuando se llama al tester.
    """
    if len(sys.argv) < 3:
        print(json.dumps({
            'error': 'Uso: python tester.py <nombre_estudiante> <ruta_carpeta>'
        }))
        sys.exit(1)

    nombre_estudiante = sys.argv[1]
    ruta_carpeta = sys.argv[2]

    import config
    exercises_config = config.EXAM_CONFIG['exercises']

    resultados = evaluar_estudiante(nombre_estudiante, ruta_carpeta, exercises_config)

    archivo_salida = Path(ruta_carpeta) / f"{nombre_estudiante}_resultados.json"
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(json.dumps(resultados, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
