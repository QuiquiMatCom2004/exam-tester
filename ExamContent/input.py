"""
Generadores de casos de prueba para los ejercicios del examen.

Por cada ejercicio en config.py, definir una funcion con el nombre:
    generar_casos_{name}(num_casos)

donde {name} es el campo "name" del ejercicio en config.py.

Cada generador debe retornar una lista de tuplas, donde cada tupla
contiene los argumentos para una llamada a la funcion del estudiante.
Los casos fijos (edge cases) deben ir al INICIO de la lista.

Ejemplo:
    Si config.py tiene un ejercicio con "name": "suma", definir:

    def generar_casos_suma(num_casos):
        casos = []
        # Casos fijos (edge cases)
        casos.append((0, 0))
        casos.append((1, -1))
        # Casos aleatorios
        import random
        for _ in range(num_casos - 2):
            a = random.randint(-100, 100)
            b = random.randint(-100, 100)
            casos.append((a, b))
        return casos
"""
