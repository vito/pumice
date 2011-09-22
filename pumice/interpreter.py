import os

from pypy.rlib.streamio import open_file_as_stream

from pumice.parser import parse


def load_file(filename, env):
    f = open_file_as_stream(filename)
    t = parse(f.readall(), filename)
    f.close()
    t.evaluate(env)
    return t


def load_source(source, env):
    return parse(source).evaluate(env)


def _readline():
    strs = []
    while True:
        s = os.read(0, 1)
        if s == "\n":
            break

        if s == "" and len(strs) == 0:
            raise SystemExit

        strs.append(s)

    return "".join(strs)


def _say(msg):
    os.write(1, msg)


def repl(env):
    while True:
        _say("> ")

        source = _readline()
        if not source:
            break

        print(load_source(source, env).show())
