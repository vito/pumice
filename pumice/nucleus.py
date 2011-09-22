import time

from pumice.values import *


def _multiply(args, env):
    x = args
    num = 0
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)
        num *= v.value
        x = x.cdr

    return VNumber(num)

def _add(args, env):
    x = args
    num = 0
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)
        num += v.value
        x = x.cdr

    return VNumber(num)

def _subtract(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)
        num -= v.value
        x = x.cdr

    return VNumber(num)

def _eq(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value != num:
            return VFalse()

        x = x.cdr

    return VTrue()

def _lt(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value > num:
            num = v.value
        else:
            return VFalse()

        x = x.cdr

    return VTrue()

def _gt(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value < num:
            num = v.value
        else:
            return VFalse()

        x = x.cdr

    return VTrue()

def _lte(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value >= num:
            num = v.value
        else:
            return VFalse()

        x = x.cdr

    return VTrue()

def _gte(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value <= num:
            num = v.value
        else:
            return VFalse()

        x = x.cdr

    return VTrue()

def _print(args, env):
    assert isinstance(args, VPair)
    print(args.car.show())
    return VInert()

def _define(args, env):
    assert isinstance(args, VPair)
    assert isinstance(args.cdr, VPair)

    pat = args.car
    val = args.cdr.car.evaluate(env)
    env.define(pat, val)
    return VInert()

def _vau(args, env):
    assert isinstance(args, VPair)
    formals = args.car
    eformal = args.cdr.car
    body = args.cdr.cdr.car
    return VOperative(formals, eformal, body, env)

def _wrap(args, env):
    assert isinstance(args, VPair)
    return VApplicative(args.car)

def _unwrap(args, env):
    assert isinstance(args, VPair)
    assert isinstance(args.car, VApplicative)
    return args.car.unwrap()

def _if(args, env):
    assert isinstance(args, VPair)
    assert isinstance(args.cdr, VPair)
    assert isinstance(args.cdr.cdr, VPair)

    cond = args.car.evaluate(env)
    yes = args.cdr.car
    no = args.cdr.cdr.car

    if isinstance(cond, VTrue):
        return yes.evaluate(env)
    elif isinstance(cond, VFalse):
        return no.evaluate(env)
    else:
        print("Not boolean: %s" % cond.show())
        return VInert()

def _eval(args, env):
    assert isinstance(args, VPair)
    return args.car.evaluate(args.cdr.car)

def _time(args, env):
    assert isinstance(args, VPair)

    a = time.clock()
    r = args.car.evaluate(env)
    print(time.clock() - a)
    return r

def _booleanp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VTrue) or \
            isinstance(args.car, VFalse):
        return VTrue()
    else:
        return VFalse()

def _eqp(args, env):
    assert isinstance(args, VPair)

    if args.car.eq(args.cdr.car):
        return VTrue()
    else:
        return VFalse()

def _equalp(args, env):
    assert isinstance(args, VPair)

    if args.car.equal(args.cdr.car):
        return VTrue()
    else:
        return VFalse()

def _symbolp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VSymbol):
        return VTrue()
    else:
        return VFalse()

def _stringp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VString):
        return VTrue()
    else:
        return VFalse()

def _inertp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VInert):
        return VTrue()
    else:
        return VFalse()

def _pairp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VPair):
        return VTrue()
    else:
        return VFalse()

def _nullp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VNull):
        return VTrue()
    else:
        return VFalse()

def _ignorep(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VIgnore):
        return VTrue()
    else:
        return VFalse()

def _numberp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VNumber):
        return VTrue()
    else:
        return VFalse()

def _operativep(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VOperative):
        return VTrue()
    else:
        return VFalse()

def _applicativep(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VApplicative):
        return VTrue()
    else:
        return VFalse()

def _environmentp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VEnvironment):
        return VTrue()
    else:
        return VFalse()

def _combinerp(args, env):
    assert isinstance(args, VPair)

    if isinstance(args.car, VOperative) or \
            isinstance(args.car, VApplicative):
        return VTrue()
    else:
        return VFalse()

def _cons(args, env):
    assert isinstance(args, VPair)
    assert isinstance(args.cdr, VPair)
    return VPair(args.car, args.cdr.car)

def _make_environment(args, env):
    assert isinstance(args, VList)
    return VEnvironment({}, args.to_list())

def _bindsp(args, env):
    assert isinstance(args, VPair)

    where = args.car.evaluate(env)
    assert isinstance(where, VEnvironment)

    syms = args.cdr
    while isinstance(syms, VPair):
        sym = syms.car
        if isinstance(sym, VSymbol):
            if not where.binds(sym.name):
                return VFalse()

        syms = syms.cdr
    
    return VTrue()

def _max(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    max = start

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value > max.value:
            max = v

        x = x.cdr

    return max

def _min(args, env):
    assert isinstance(args, VPair)

    start = args.car
    assert isinstance(start, VNumber)

    min = start

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber)

        if v.value < min.value:
            min = v

        x = x.cdr

    return min


Ground = VEnvironment({
    # basic predicates
    "boolean?": VApplicative(VCoreOperative(_booleanp)),
    "symbol?": VApplicative(VCoreOperative(_symbolp)),
    "string?": VApplicative(VCoreOperative(_stringp)),
    "inert?": VApplicative(VCoreOperative(_inertp)),
    "pair?": VApplicative(VCoreOperative(_pairp)),
    "null?": VApplicative(VCoreOperative(_nullp)),
    "environment?": VApplicative(VCoreOperative(_environmentp)),
    "ignore?": VApplicative(VCoreOperative(_ignorep)),
    "number?": VApplicative(VCoreOperative(_numberp)),
    "operative?": VApplicative(VCoreOperative(_operativep)),
    "applicative?": VApplicative(VCoreOperative(_applicativep)),
    "combiner?": VApplicative(VCoreOperative(_combinerp)),

    # equality
    "eq?": VApplicative(VCoreOperative(_eqp)),
    "equal?": VApplicative(VCoreOperative(_equalp)),

    # constructors
    "cons": VApplicative(VCoreOperative(_cons)),
    "wrap": VApplicative(VCoreOperative(_wrap)),
    "vau": VCoreOperative(_vau),
    "unwrap": VApplicative(VCoreOperative(_unwrap)),

    # environment
    "make-environment": VApplicative(VCoreOperative(_make_environment)),
    "binds?": VCoreOperative(_bindsp),
    "define": VCoreOperative(_define),
    "eval": VApplicative(VCoreOperative(_eval)),

    # numeric
    "max": VApplicative(VCoreOperative(_max)),
    "min": VApplicative(VCoreOperative(_min)),
    "*": VApplicative(VCoreOperative(_add)),
    "+": VApplicative(VCoreOperative(_add)),
    "-": VApplicative(VCoreOperative(_subtract)),
    "=?": VApplicative(VCoreOperative(_lt)),
    "<?": VApplicative(VCoreOperative(_lt)),
    ">?": VApplicative(VCoreOperative(_gt)),
    "<=?": VApplicative(VCoreOperative(_lte)),
    ">=?": VApplicative(VCoreOperative(_gte)),

    # misc
    "print": VApplicative(VCoreOperative(_print)),
    "if": VCoreOperative(_if),
    "time": VCoreOperative(_time),
})
