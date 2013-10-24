def chunks(l, n, length=None):
    """ Yield successive n-sized chunks from l.
    """
    if length is None:
        length = len(l)

    for i in xrange(0, length, n):
        yield l[i:i + n]
