from enum import EnumMeta


def filter_model(data):
    result = {}
    for k, v in data.items():
        if k.startswith("_"):
            continue

        try:
            if not isinstance(v, EnumMeta) and not isinstance(v, str) and not isinstance(v, int):
                v.__dict__
                result[k] = filter_model(v)
            else:
                result[k] = v
        except AttributeError:
            result[k] = v
            pass
    return result
