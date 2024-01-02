def reducer():
    from sys import stdin

    dominio_anterior = ""
    tipo_anterior = ""
    suma_bytes = 0

    datos_sumados = {}

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 3: continue

        # Procesamiento
        if datos[0] != dominio_anterior:
            if not datos_sumados.get(dominio_anterior, None):
                datos_sumados[dominio_anterior] = 0

            dominio_anterior = datos[0]
            tipo_anterior = datos[1]
            try: suma_bytes = int(datos[2])
            except: suma_bytes = 0

        elif datos[1] != tipo_anterior:
            try: suma_bytes -= int(datos[2])
            except: pass

        else:
            try: suma_bytes += int(datos[2])
            except: pass

        datos_sumados[dominio_anterior] = suma_bytes

    for x, y in datos_sumados.items():
        print(f'{x};{y}')


if __name__ == '__main__': reducer()
