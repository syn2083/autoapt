import datetime
from os import path, makedirs


def folder_construct():
        scriptdir, script = path.split(__file__)
        local_path = scriptdir
        template_dir = path.join(local_path, "output\\" + 'aptdemo')

        exit_d = path.join(template_dir, "exit_data")

        if not path.exists(exit_d):
            makedirs(exit_d)

        return exit_d


def str_to_list(in_str):
    nlist = []

    for i in in_str.split(','):
        nlist.append(i.strip())

    return nlist


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def find_shift():
    now = datetime.datetime.time(datetime.datetime.now())
    if time_in_range(datetime.time(8, 00, 00), datetime.time(15, 59, 59), now):
        return 1
    elif time_in_range(datetime.time(16, 00, 00), datetime.time(23, 59, 59), now):
        return 2
    elif time_in_range(datetime.time(00, 00, 00), datetime.time(7, 59, 59), now):
        return 3
    else:
        return 1



