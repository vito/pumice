class VValue:
    def evaluate(self, env):
        return self

    def show(self):
        return str(self)

    def eq(self, other):
        return self is other

    def equal(self, other):
        return self is other


class VList(VValue):
    pass


class VNull(VList):
    def equal(self, other):
        return self is other or isinstance(other, VNull)

    def evaluateAll(self, env):
        return self

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

    def evaluate(self, env):
        c = self.car.evaluate(env)

        if isinstance(c, VOperative):
            return c.apply(env, self.cdr)
        elif isinstance(c, VApplicative):
            return c.unwrap().apply(env, self.cdr.evaluateAll(env))
        else:
            print("Not applicable: %s" % c.show())
            return VInert() # TODO: error

    def evaluateAll(self, env):
        return VPair(self.car.evaluate(env), self.cdr.evaluateAll(env))

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

    def apply(self, env, args):
        newEnv = VEnvironment({}, [self.static_environment])
        newEnv.define(self.formals, args)
        newEnv.define(self.eformal, env)
        return self.body.evaluate(newEnv)


class VCoreOperative(VOperative):
    def __init__(self, fun):
        self.function = fun

    def apply(self, env, args):
        return self.function(args, env)


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

    def evaluate(self, env):
        val = env.lookup(self.name)
        if val:
            return val
        else:
            print("Unknown symbol: %s" % self.show())
            return VInert() # TODO: error

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
    
    def evaluate(self, env):
        res = VInert()

        for sexp in self.sexps:
            res = sexp.evaluate(env)

        return res


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
