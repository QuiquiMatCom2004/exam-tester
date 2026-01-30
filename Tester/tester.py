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


def probar_funcion(funcion_estudiante, casos_prueba,
                   nombre_funcion, num_casos_fijados=0, comparator_func=None):
    """
    Prueba una funcion del estudiante contra respuestas pre-generadas.

    Args:
        funcion_estudiante: funcion del estudiante a probar
        casos_prueba: lista de casos con inputs y expected_output pre-generados
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
        # Obtener inputs y output esperado pre-generado
        inputs = tuple(caso['inputs'])
        resultado_esperado = caso['expected_output']
        error_esperado = caso.get('expected_error')

        # Ejecutar funcion del estudiante
        resultado_estudiante, error_estudiante = ejecutar_con_timeout(
            funcion_estudiante, inputs
        )

        es_caso_fijado = (i <= num_casos_fijados)

        # Si la solucion correcta genera error, el estudiante tambien debe generarlo
        if error_esperado:
            if error_estudiante:
                # Ambos generan error, consideramos correcto
                resultados['casos_pasados'] += 1
                if es_caso_fijado:
                    resultados['casos_fijados_pasados'] += 1
            else:
                # El estudiante no genero error cuando deberia
                resultados['casos_fallidos'] += 1
                resultados['detalles_fallos'].append({
                    'caso_numero': i,
                    'entrada': list(inputs),
                    'esperado': f"ERROR: {error_esperado}",
                    'obtenido': resultado_estudiante if resultado_estudiante is not None else 'None',
                    'tipo_error': 'deberia_generar_error'
                })
        elif error_estudiante:
            # El estudiante genero error cuando no deberia
            resultados['casos_error'] += 1
            resultados['detalles_fallos'].append({
                'caso_numero': i,
                'entrada': list(inputs),
                'esperado': resultado_esperado if resultado_esperado is not None else 'None',
                'obtenido': f"ERROR: {error_estudiante}",
                'tipo_error': 'excepcion'
            })
        elif not comparator_func(resultado_esperado, resultado_estudiante):
            resultados['casos_fallidos'] += 1
            resultados['detalles_fallos'].append({
                'caso_numero': i,
                'entrada': list(inputs),
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
        nombre_estudiante: nombre del estudiante (puede contener espacios, ej: "Adriana Amador")
        ruta_carpeta: ruta a la carpeta del estudiante
        exercises_config: lista de configuraciones de ejercicios
    Returns:
        diccionario con resultados de la evaluacion
    """
    sys.path.insert(0, str(Path(__file__).parent))

    try:
        import case_loader
        from comparators import get_comparator
    except ImportError as e:
        return {
            'error': f'No se pudieron importar los modulos necesarios: {e}',
            'nombre_estudiante': nombre_estudiante
        }

    # Cargar casos con respuestas pre-generadas
    casos = case_loader.generar_todos_los_casos()

    resultados = {
        'nombre_estudiante': nombre_estudiante,
        'ejercicios': []
    }

    # Convertir nombre con espacios a nombre con guiones bajos para archivos
    # Ejemplo: "Adriana Amador" -> "Adriana_Amador"
    nombre_archivo = nombre_estudiante.replace(' ', '_')

    for ex in exercises_config:
        ex_name = ex['name']
        func_name = ex['function_name']
        suffix = ex['file_suffix']
        num_fixed = ex['num_fixed_cases']
        comp_func = get_comparator(ex['comparator'])

        # Buscar archivo usando nombre con guiones bajos
        archivo = Path(ruta_carpeta) / f"{nombre_archivo}_{suffix}.py"

        if archivo.exists():
            modulo = cargar_modulo(archivo)
            if modulo and hasattr(modulo, func_name):
                resultado = probar_funcion(
                    getattr(modulo, func_name),
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
