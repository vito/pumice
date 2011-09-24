import time

from pumice.values import *
from pumice.interpreter import load_file, ignore


def _multiply(args, env, k):
    x = args
    num = 0
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"
        num *= v.value
        x = x.cdr

    return k.call(VNumber(num))

def _add(args, env, k):
    x = args
    num = 0
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"
        num += v.value
        x = x.cdr

    return k.call(VNumber(num))

def _subtract(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"
        num -= v.value
        x = x.cdr

    return k.call(VNumber(num))

def _eq(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value != num:
            return k.call(VFalse())

        x = x.cdr

    return k.call(VTrue())

def _lt(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value > num:
            num = v.value
        else:
            return k.call(VFalse())

        x = x.cdr

    return k.call(VTrue())

def _gt(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value < num:
            num = v.value
        else:
            return k.call(VFalse())

        x = x.cdr

    return k.call(VTrue())

def _lte(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value >= num:
            num = v.value
        else:
            return k.call(VFalse())

        x = x.cdr

    return k.call(VTrue())

def _gte(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    num = start.value

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value <= num:
            num = v.value
        else:
            return k.call(VFalse())

        x = x.cdr

    return k.call(VTrue())

def _print(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    print(args.car.show())
    return k.call(VInert())

def _define(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    return args.cdr.car.evaluate(env, VContinuation(_define2, [args.car, env, k]))

def _define2(val, args):
    pat, env, k = args
    env.define(pat, val)
    return k.call(VInert())

def _vau(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    formals = args.car
    eformal = args.cdr.car
    body = args.cdr.cdr.car
    return k.call(VOperative(formals, eformal, body, env))

def _wrap(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    return k.call(VApplicative(args.car))

def _unwrap(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.car, VApplicative), "must be an applicative"
    return k.call(args.car.unwrap())

def _callcc(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    return VPair(args.car, VPair(k, VNull())).evaluate(env, k)

def _apply_continuation(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"

    cont = args.car
    assert isinstance(cont, VContinuation)

    return cont.call(args.cdr.car)

def _extend_continuation(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"

    cont = args.car
    assert isinstance(cont, VContinuation)

    applicative = args.cdr.car

    if isinstance(args.cdr.cdr, VPair):
        env = args.cdr.cdr.car
    else:
        env = VEnvironment({})

    return k.call(cont.extend(applicative, env))

def _if(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    assert isinstance(args.cdr.cdr, VPair), "not enough arguments"

    return args.car.evaluate(env, VContinuation(_if2, [args.cdr.car, args.cdr.cdr.car, env, k]))

def _if2(cond, args):
    yes, no, env, k = args
    if isinstance(cond, VTrue):
        return yes.evaluate(env, k)
    elif isinstance(cond, VFalse):
        return no.evaluate(env, k)
    else:
        print("Not boolean: %s" % cond.show())
        return k.call(VInert())

def _eval(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    return args.car.evaluate(args.cdr.car, k)

def _time(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    return args.car.evaluate(env, VContinuation(_time2, [VNumber(time.clock()), env, k]))

def _time2(res, args):
    started, env, k = args
    assert isinstance(started, VNumber)
    print(time.clock() - started.value)
    return k.call(res)

def _booleanp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VTrue) or \
            isinstance(args.car, VFalse):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _eqp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if args.car.eq(args.cdr.car):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _equalp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if args.car.equal(args.cdr.car):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _symbolp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VSymbol):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _stringp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VString):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _inertp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VInert):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _pairp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VPair):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _nullp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VNull):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _listp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VList):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _ignorep(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VIgnore):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _numberp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VNumber):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _operativep(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VOperative):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _applicativep(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VApplicative):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _environmentp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VEnvironment):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _combinerp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VOperative) or \
            isinstance(args.car, VApplicative):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _continuationp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    if isinstance(args.car, VContinuation):
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _cons(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    return k.call(VPair(args.car, args.cdr.car))

def _make_environment(args, env, k):
    assert isinstance(args, VList), "non-list arguments"
    return k.call(VEnvironment({}, args.to_list()))

def _bindsp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    return args.car.evaluate(env, VContinuation(_bindsp2, [args.cdr, env, k]))

def _bindsp2(where, args):
    syms, env, k = args
    assert isinstance(where, VEnvironment), "must be an environment"

    while isinstance(syms, VPair):
        sym = syms.car
        if isinstance(sym, VSymbol):
            if not where.binds(sym.name):
                return k.call(VFalse())

        syms = syms.cdr

    return k.call(VTrue())

def _max(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    max = start

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value > max.value:
            max = v

        x = x.cdr

    return k.call(max)

def _min(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    start = args.car
    assert isinstance(start, VNumber), "must be numeric"

    min = start

    x = args.cdr
    while isinstance(x, VPair):
        v = x.car
        assert isinstance(v, VNumber), "must be numeric"

        if v.value < min.value:
            min = v

        x = x.cdr

    return k.call(min)

def _load(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    val = args.car
    assert isinstance(val, VString), "must be a string"

    return load_file(val.value, env, k)

def _string2symbol(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    val = args.car
    assert isinstance(val, VString), "must be a string"

    return k.call(VSymbol(val.value))

def _symbol2string(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"

    val = args.car
    assert isinstance(val, VSymbol), "must be a symbol"

    return k.call(VString(val.name))

def _join(args, env, k):
    assert isinstance(args, VPair), "non-list arguments"

    val = args.car
    assert isinstance(val, VString), "must be a string"

    delim = val.value

    strs = []
    vals = args.cdr
    while isinstance(vals, VPair):
        val = vals.car
        assert isinstance(val, VString), "must be a string"

        strs.append(val.value)

        vals = vals.cdr

    return k.call(VString(delim.join(strs)))


Ground = {
    # basic predicates
    "boolean?": VApplicative(VCoreOperative(_booleanp)),
    "symbol?": VApplicative(VCoreOperative(_symbolp)),
    "string?": VApplicative(VCoreOperative(_stringp)),
    "inert?": VApplicative(VCoreOperative(_inertp)),
    "environment?": VApplicative(VCoreOperative(_environmentp)),
    "pair?": VApplicative(VCoreOperative(_pairp)),
    "null?": VApplicative(VCoreOperative(_nullp)),
    "list?": VApplicative(VCoreOperative(_pairp)),
    "ignore?": VApplicative(VCoreOperative(_ignorep)),
    "number?": VApplicative(VCoreOperative(_numberp)),
    "operative?": VApplicative(VCoreOperative(_operativep)),
    "applicative?": VApplicative(VCoreOperative(_applicativep)),
    "combiner?": VApplicative(VCoreOperative(_combinerp)),
    "continuation?": VApplicative(VCoreOperative(_continuationp)),

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
    "if": VCoreOperative(_if),
    "load": VApplicative(VCoreOperative(_load)),
    "print": VApplicative(VCoreOperative(_print)),
    "time": VCoreOperative(_time),

    # continuations
    "call/cc": VApplicative(VCoreOperative(_callcc)),
    "apply-continuation": VApplicative(VCoreOperative(_apply_continuation)),
    "extend-continuation": VApplicative(VCoreOperative(_extend_continuation)),

    # string
    "string->symbol": VApplicative(VCoreOperative(_string2symbol)),
    "symbol->string": VApplicative(VCoreOperative(_symbol2string)),
    "join": VApplicative(VCoreOperative(_join)),
}


def _make_encapsulation_tag(args, env, k):
    return k.call(VEncapsulationTag())

def _make_encapsulation(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    assert isinstance(args.car, VEncapsulationTag), "must be an encapsulation tag"

    tag = args.car
    assert isinstance(tag, VEncapsulationTag)

    return k.call(VEncapsulation(tag, args.cdr.car))

def _encapsulation_taggedp(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    assert isinstance(args.car, VEncapsulationTag), "must be an encapsulation tag"

    tag = args.car
    val = args.cdr.car

    if isinstance(val, VEncapsulation) and val.tag is tag:
        return k.call(VTrue())
    else:
        return k.call(VFalse())

def _deconstruct_encapsulation(args, env, k):
    assert isinstance(args, VPair), "not enough arguments"
    assert isinstance(args.cdr, VPair), "not enough arguments"
    assert isinstance(args.car, VEncapsulationTag), "must be an encapsulation tag"

    tag = args.car
    val = args.cdr.car
    assert isinstance(val, VEncapsulation), "must be an encapsulation"
    assert val.tag is tag, "encapsulation type mismatch"

    return k.call(val.value)


Encapsulation = {
    "make-encapsulation-tag": VApplicative(VCoreOperative(_make_encapsulation_tag)),
    "make-encapsulation": VApplicative(VCoreOperative(_make_encapsulation)),
    "encapsulation-tagged?": VApplicative(VCoreOperative(_encapsulation_taggedp)),
    "deconstruct-encapsulation": VApplicative(VCoreOperative(_deconstruct_encapsulation)),
}


def load_kernel(which, env, k):
    return load_file("kernel/%s" % which, env, k)


def load():
    ground = VEnvironment(Ground)
    load_kernel('boot.pmc', ground, ignore)
    load_kernel('encapsulation.pmc', VEnvironment(Encapsulation, [ground]), ignore)
    load_kernel('record.pmc', ground, ignore)
    load_kernel('object.pmc', ground, ignore)
    load_kernel('class.pmc', ground, ignore)
    return ground
