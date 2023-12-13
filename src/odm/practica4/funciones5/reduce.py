def reducer():
    from sys import stdin

    tipo_archivo = None
    total = 0

    for linea in stdin:
        # Comprobaciones
        if not linea: continue

        # Procesamiento
        if tipo_archivo == linea.strip():
            total += 1
        else:
            if tipo_archivo: print(f'{tipo_archivo};{total}')
            tipo_archivo = linea.strip()
            total = 1

    print(f'{tipo_archivo};{total}')


if __name__ == '__main__': reducer()
