def mapper():
    from sys import stdin

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue
        if type(datos[4]) != str: continue

        # Procesamiento
        print(f'{datos[4]};{datos[7][0]}XX;1')


if __name__ == '__main__': mapper()
