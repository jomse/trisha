import const


def init(config='config.cfg'):
    use_dict = []
    with open(config) as config_file:
        const.num = int(config_file.readline())
        const.num_len = int(config_file.readline())
        const.quiz_list_len = int(config_file.readline())
        const.filter_view = config_file.readline()
        for lines in config_file:
            use_dict.append(lines.split('\n')[0])
    return use_dict[:-1]