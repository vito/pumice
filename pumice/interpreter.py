import os

from pypy.rlib.streamio import open_file_as_stream

from pumice.parser import parse
from pumice.values import VContinuation


def load_file(filename, env, k):
    f = open_file_as_stream(filename)
    t = parse(f.readall(), filename)
    f.close()
    trampoline(t.evaluate(env, k))
    return t


def load_source(source, env, k):
    return trampoline(parse(source).evaluate(env, k))

def trampoline(v):
    while isinstance(v, VContinuation):
        v = v.go()

    return v

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
    _say("> ")

    source = _readline()
    if source:
        return load_source(source, env, VContinuation(_repl2, [env]))

def _repl2(res, args):
    print(res.show())
    return repl(args[0])


def _ignore(val, _args):
    return val

ignore = VContinuation(_ignore)
