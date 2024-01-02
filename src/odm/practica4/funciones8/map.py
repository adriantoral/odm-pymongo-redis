def mapper():
    from sys import stdin

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue

        # Procesamiento
        if x := datos[5].split('/')[-1].split('.'):
            if len(x) == 2:
                print(f'{datos[0]};{x[-1].lower()};{datos[-1]}')


if __name__ == '__main__': mapper()
