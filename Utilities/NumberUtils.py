def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return '.' not in n and float(n).is_integer()

def is_float(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return '.' in n

