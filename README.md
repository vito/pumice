# Running

For a excruciatingly slow interpreter, you can just run `main.py` with Python.

It's recommended though that you use PyPy to compile to a native executable,
which is much much faster.

    brew install pypy
    hg clone https://bitbucket.org/pypy/pypy $PYPY
    export PYTHONPATH=.
    pypy $PYPY/pypy/translator/goal/translate.py pumice/main.py
    ./pumice-c
