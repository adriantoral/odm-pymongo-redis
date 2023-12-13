def reducer():
    from sys import stdin

    total_gets = 0
    for _ in stdin: total_gets += 1

    print(total_gets)


if __name__ == '__main__': reducer()
