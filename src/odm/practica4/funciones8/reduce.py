from time import sleep


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
        if dominio_anterior != datos[0] or tipo_anterior != datos[1]:
            if not datos_sumados.get(dominio_anterior, None):
                datos_sumados[dominio_anterior] = {}

            datos_sumados[dominio_anterior][suma_bytes] = tipo_anterior
            dominio_anterior = datos[0]
            tipo_anterior = datos[1]

            try: suma_bytes = int(datos[2])
            except: suma_bytes = 0

        else:
            try: suma_bytes += int(datos[2])
            except: pass

    datos_sumados[dominio_anterior][suma_bytes] = tipo_anterior

    for dominio in datos_sumados.keys():
        claves_ordenadas = list(datos_sumados[dominio].keys())
        claves_ordenadas.sort(reverse=True)

        for x in claves_ordenadas[:3]:
            print(f'{dominio};{datos_sumados[dominio][x]};{x}')


if __name__ == '__main__': reducer()
