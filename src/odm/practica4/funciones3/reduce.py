def reducer():
    from sys import stdin

    total = 0
    tipo_actual = None
    total_peticiones = 0

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 2:
            if len(datos) == 1: total = int(datos[0])
            continue
        if type(datos[0]) != str: continue

        # Procesamiento
        tipo = datos[0]

        if tipo_actual == tipo:
            total_peticiones += int(datos[1])
        else:
            if tipo_actual: print(f'{tipo_actual};{(total_peticiones / total) * 100}%')
            tipo_actual = tipo
            total_peticiones = int(datos[1])

    if tipo_actual: print(f'{tipo_actual};{(total_peticiones / total) * 100}%')


if __name__ == '__main__': reducer()
