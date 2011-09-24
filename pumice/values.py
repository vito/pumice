class VValue:
    def evaluate(self, env, k):
        return k.call(self)

    def evaluateAll(self, env, k):
        return k.call(self)

    def show(self):
        return str(self)

    def eq(self, other):
        return self is other

    def equal(self, other):
        return self is other


class VContinuation(VValue):
    def __init__(self, cont, args = []):
        self.cont = cont
        self.args = args
        self.applied = None

    def is_ready(self):
        if self.applied:
            return True
        else:
            return False

    def call(self, val):
        self.applied = val
        return self

    def go(self):
        return self.cont(self.applied, self.args)

    def extend(self, app, env):
        return VExtendedContinuation(self, app, env)


class VExtendedContinuation(VContinuation):
    def __init__(self, parent, applicative, env):
        self.parent = parent
        self.operative = applicative.unwrap()
        self.env = env

    def is_ready(self):
        return self.parent.is_ready()

    def call(self, val):
        self.parent.call(val)
        return self

    def go(self):
        return self.operative.apply(
            self.env,
            VPair(self.parent.applied, VNull()),
            VContinuation(_callParent, [self.parent])
        )

def _callParent(val, k):
    return k[0].call(val)


class VList(VValue):
    pass


class VNull(VList):
    def equal(self, other):
        return self is other or isinstance(other, VNull)

    def show(self):
        return "()"

    def to_list(self):
        return []


class VPair(VList):
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def equal(self, other):
        return self is other or \
                isinstance(other, VPair) and \
                self.car.equal(other.car) and \
                self.cdr.equal(other.cdr)

    def evaluate(self, env, k):
        return self.car.evaluate(env, VContinuation(_apply, [self.cdr, env, k]))

    def evaluateAll(self, env, k):
        return self.car.evaluate(env, VContinuation(_evalTail, [self.cdr, env, k]))

    def show(self):
        return "(%s)" % show_pair(self)

    def to_list(self):
        x = self.cdr
        if isinstance(x, VPair) or isinstance(x, VNull):
            rest = x.to_list()
            rest.insert(0, self.car)
            return rest
        else:
            return [self.car]

def _apply(c, args):
    params, env, k = args
    if isinstance(c, VOperative):
        return c.apply(env, params, k)
    elif isinstance(c, VApplicative):
        return params.evaluateAll(env, VContinuation(_applyApp, [c.unwrap(), env, k]))
    else:
        print("Not applicable: %s" % c.show())
        return k.call(VInert())

def _applyApp(params, args):
    c, env, k = args
    assert isinstance(c, VOperative)
    return c.apply(env, params, k)

def _evalTail(h, args):
    rest, env, k = args
    return rest.evaluateAll(env, VContinuation(_makePair, [h, k]))

def _makePair(t, args):
    h, k = args
    return k.call(VPair(h, t))


class VTrue(VValue):
    def equal(self, other):
        return self is other or isinstance(self, VTrue)

    def show(self):
        return "#t"


class VFalse(VValue):
    def equal(self, other):
        return self is other or isinstance(self, VFalse)

    def show(self):
        return "#f"


class VIgnore(VValue):
    def equal(self, other):
        return self is other or isinstance(self, VIgnore)

    def show(self):
        return "#ignore"


class VInert(VValue):
    def equal(self, other):
        return self is other or isinstance(self, VInert)

    def show(self):
        return "#inert"


class VOperative(VValue):
    def __init__(self, formals, eformal, body, static_environment):
        self.formals = formals
        self.eformal = eformal
        self.body = body
        self.static_environment = static_environment

    def apply(self, env, args, k):
        newEnv = VEnvironment({}, [self.static_environment])
        newEnv.define(self.formals, args)
        newEnv.define(self.eformal, env)
        return self.body.evaluate(newEnv, k)


class VCoreOperative(VOperative):
    def __init__(self, fun):
        self.function = fun

    def apply(self, env, args, k):
        return self.function(args, env, k)


class VApplicative(VValue):
    def __init__(self, operative):
        self.operative = operative

    # TODO: verify with kernel report
    def equal(self, other):
        return self is other or \
                isinstance(other, VApplicative) and \
                self.operative.equal(other.operative)

    def unwrap(self):
        return self.operative


class VEnvironment(VValue):
    def __init__(self, bindings, parents = []):
        self.bindings = bindings
        self.parents = parents

    def lookup(self, name):
        if name in self.bindings:
            return self.bindings[name]
        else:
            for parent in self.parents:
                val = parent.lookup(name)
                if val:
                    return val

            return None

    def binds(self, name):
        if name in self.bindings:
            return True
        else:
            for parent in self.parents:
                if parent.binds(name):
                    return True

            return False

    def define(self, pattern, value):
        if isinstance(pattern, VSymbol):
            self.bindings[pattern.name] = value
        elif isinstance(pattern, VPair) and isinstance(value, VPair):
            self.define(pattern.car, value.car)
            self.define(pattern.cdr, value.cdr)
        elif isinstance(pattern, VNull) and isinstance(value, VNull):
            pass
        elif isinstance(pattern, VIgnore):
            pass
        else:
            # TODO: error
            pass


class VSymbol(VValue):
    def __init__(self, name):
        self.name = name

    def equal(self, other):
        return self is other or \
                isinstance(other, VSymbol) and \
                self.name == other.name

    def evaluate(self, env, k):
        val = env.lookup(self.name)
        if val:
            return k.call(val)
        else:
            print("Unknown symbol: %s" % self.show())
            return k.call(VInert())

    def show(self):
        return self.name


class VString(VValue):
    def __init__(self, value):
        self.value = value

    def equal(self, other):
        return self is other or \
                isinstance(other, VString) and \
                self.value == other.value

    def show(self):
        # TODO
        return self.value


class VNumber(VValue):
    def __init__(self, value):
        self.value = value

    def equal(self, other):
        return self is other or \
                isinstance(other, VNumber) and \
                self.value == other.value

    def show(self):
        return str(self.value)


class VTree(VValue):
    def __init__(self, sexps):
        self.sexps = sexps
    
    def evaluate(self, env, k):
        return _evalTree(VInert(), [self, env, k])

def _evalTree(res, args):
    tree, env, k = args

    rest = tree.sexps

    if len(rest) == 0:
        return k.call(res)

    return rest[0].evaluate(env, VContinuation(_evalTree, [VTree(rest[1:]), env, k]))


class VEncapsulation(VValue):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value


class VEncapsulationTag(VValue):
    pass


def show_pair(what):
    if isinstance(what, VPair):
        if isinstance(what.cdr, VPair):
            return "%s %s" % (what.car.show(), show_pair(what.cdr))
        elif isinstance(what.cdr, VNull):
            return what.car.show()
        else:
            return "%s . %s" % (what.car, what.cdr.show())
    else:
        return what.show()
