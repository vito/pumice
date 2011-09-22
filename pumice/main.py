import py
import sys

from pumice.interpreter import load_file
from pumice.nucleus import Ground


BootFile = str(py.path.local(__file__).dirpath().dirpath().join('kernel').join('boot.pmc'))


def main(argv):
    if len(argv) == 2:
        load_file(BootFile, Ground)
        load_file(argv[1], Ground)

        return 0
    else:
        print "Usage: %s foo.pmc" % argv[0]
        return 1


def target(driver, args):
    driver.exe_name = 'pumice-%(backend)s'
    return main, None


if __name__ == '__main__':
    main(sys.argv)

