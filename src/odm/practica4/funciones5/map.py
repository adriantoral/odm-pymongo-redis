def mapper():
    from sys import stdin

    hora = 2
    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue
        if type(datos[4]) != str: continue

        # Procesamiento
        if datos[7][0] == '4':
            if int(datos[3].split()[-1].split(':')[0]) == hora:
                if x := datos[5].split('/')[-1].split('.'):
                    if len(x) == 2:
                        print(x[-1].lower())


if __name__ == '__main__': mapper()
