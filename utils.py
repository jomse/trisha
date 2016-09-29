def pretty_print_dict(dictionary, sort_by_values=True):
    tuples = [(v, k) for k, v in dictionary.items()]
    if sort_by_values:
        tuples.sort(reverse=True)
    max_key_length = len(max(dictionary.keys(), key=len))

    for v, k in tuples:
        print(str(k).ljust(max_key_length + 1), v)