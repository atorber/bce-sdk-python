# utils/helpers.py

from itertools import zip_longest


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks, filling missing values with `fillvalue`."""
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
