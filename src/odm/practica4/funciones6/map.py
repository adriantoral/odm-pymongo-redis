def mapper():
    from sys import stdin

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue
        if type(datos[4]) != str: continue

        # Procesamiento
        print(f'{datos[3].split()[-1].split(":")[0]};{datos[-1]}')


if __name__ == '__main__': mapper()
