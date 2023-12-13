def reducer():
    from sys import stdin

    tipo_peticion = None
    respuesta = None
    total_peticiones = 0

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 3: continue
        if type(datos[0]) != str or type(datos[1]) != str: continue

        # Procesamiento
        if tipo_peticion != datos[0] or respuesta != datos[1]:
            print(f'{tipo_peticion};{respuesta};{total_peticiones}')
            tipo_peticion = datos[0]
            respuesta = datos[1]
            total_peticiones = 1
        else:
            total_peticiones += int(datos[2])

    print(f'{tipo_peticion};{respuesta};{total_peticiones}')


if __name__ == '__main__': reducer()
