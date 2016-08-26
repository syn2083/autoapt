import datetime
from os import path, makedirs


def folder_construct():
        pathers = []
        local_path = path.dirname(path.abspath(__file__))
        template_dir = path.join(local_path, "output\\" + 'aptdemo')
        pathers.append(template_dir)
        outjif = path.join(template_dir, "jif_output")
        pathers.append(outjif)
        feed_d = path.join(template_dir, "feed_data")
        pathers.append(feed_d)
        exit_d = path.join(template_dir, "exit_data")
        pathers.append(exit_d)

        for item in pathers:
            if not path.exists(item):
                makedirs(item)

        return [outjif, feed_d, exit_d]


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



