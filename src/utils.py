def zfill(s, width):
    if len(s) < width:
        return ("0" * (width - len(s))) + s
    else:
        return s


def leading_zero(number):
    return zfill(str(number), 2)


def to_log_value(val):
    return str(val).replace('.', ',')