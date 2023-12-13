def reducer():
    from sys import stdin

    hora_actual = None
    total = 0
    total_anterior = 0

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 2: continue
        if type(datos[0]) != str: continue

        # Procesamiento
        hora, cantidad = datos
        try:
            cantidad = int(cantidad)
        except: continue

        if hora_actual == hora:
            total += cantidad
        else:
            if hora_actual: print(f'{hora_actual};{(total_anterior / total) * 100}%')
            hora_actual = hora
            total_anterior = total
            total = cantidad

    print(f'{hora_actual};{(total_anterior / total) * 100}%')


if __name__ == '__main__': reducer()
