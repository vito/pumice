from pypy.rlib.streamio import open_file_as_stream

from pumice.parser import parse


def load_file(filename, env):
    f = open_file_as_stream(filename)
    t = parse(f.readall(), filename)
    f.close()
    t.evaluate(env)
    return t
