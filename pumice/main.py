import py
import sys

from pumice.interpreter import load_file, repl
from pumice.nucleus import Ground, Encapsulation


def load_kernel(which, env):
    return load_file("kernel/%s" % which, env)

def main(argv):
    if len(argv) == 2:
        load_kernel('boot.pmc', Ground)
        load_kernel('encapsulation.pmc', Encapsulation)
        load_file(argv[1], Ground)

        return 0
    elif len(argv) == 1:
        load_kernel('boot.pmc', Ground)
        load_kernel('encapsulation.pmc', Encapsulation)

        try:
            repl(Ground)
        except SystemExit:
            print "\nSee ya!"

        return 0
    else:
        print "Usage: %s foo.pmc" % argv[0]
        return 1


def target(driver, args):
    driver.exe_name = 'pumice-%(backend)s'
    return main, None


if __name__ == '__main__':
    main(sys.argv)

