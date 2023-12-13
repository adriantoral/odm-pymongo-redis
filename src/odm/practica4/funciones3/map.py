def mapper():
    from sys import stdin

    total = 0

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue
        if type(datos[4]) != str: continue

        # Procesamiento
        total += 1
        print(f'{datos[4]};1')

    print(f'{total}')


if __name__ == '__main__': mapper()
