def mapper():
    from sys import stdin

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 9: continue

        # Procesamiento
        dominio = datos[0]
        tipo = datos[4]
        _bytes = datos[-1]

        if tipo.lower() in ['get', 'post']:
            print(f'{dominio};{tipo};{_bytes}')


if __name__ == '__main__': mapper()
