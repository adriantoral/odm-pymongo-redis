def reducer():
    from sys import stdin

    tipo_actual = None
    total_peticiones = 0

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 2: continue
        if type(datos[0]) != str: continue

        # Procesamiento
        tipo = datos[0]

        if tipo_actual == tipo:
            total_peticiones += 1
        else:
            if tipo_actual: print(f'{tipo_actual};{total_peticiones}')
            tipo_actual = tipo
            total_peticiones = 1

    if tipo_actual: print(f'{tipo_actual};{total_peticiones}')


if __name__ == '__main__': reducer()
