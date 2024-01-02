def mapper():
    from sys import stdin

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue

        # Procesamiento
        print(f'{datos[0]};{datos[-1]}')


if __name__ == '__main__': mapper()
