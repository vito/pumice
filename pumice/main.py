import py
import sys

from pumice import nucleus
from pumice.interpreter import load_file, repl, ignore


def main(argv):
    if len(argv) == 2:
        load_file(argv[1], nucleus.load(), ignore)

        return 0
    elif len(argv) == 1:
        try:
            repl(nucleus.load())
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

