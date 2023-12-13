def mapper():
    from sys import stdin

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue
        if type(datos[4]) != str: continue

        # Procesamiento
        if (datos[4].lower() == 'get'): print(1)


if __name__ == '__main__': mapper()
