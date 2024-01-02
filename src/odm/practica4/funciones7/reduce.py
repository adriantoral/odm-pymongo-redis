def reducer():
    from sys import stdin

    dominio_anterior = ""
    suma_bytes = 0

    top3 = {
        1: "dominio1",
        2: "dominio2",
        3: "dominio3"
    }

    for linea in stdin:
        datos = linea.split(';')

        # Comprobaciones
        if len(datos) != 2: continue

        # Procesamiento
        if datos[0] != dominio_anterior:
            if suma_bytes > min(top3.keys()):
                top3.pop(min(top3.keys()))
                top3[suma_bytes] = dominio_anterior

            dominio_anterior = datos[0]
            suma_bytes = 0

        else:
            suma_bytes += int(datos[1])

    claves_ordenadas = list(top3.keys())
    claves_ordenadas.sort(reverse=True)

    for x in claves_ordenadas:
        print(f'{x};{top3[x]}')


if __name__ == '__main__': reducer()
