from typing import Tuple


def tuple_sum(t1: Tuple, t2: Tuple):
    return t1[0] + t2[0], t1[1] + t2[1]


def tuple_diff(t1: Tuple, t2: Tuple):
    return t1[0] - t2[0], t1[1] - t2[1]