#!/usr/bin/env python

import sys
import os

def main(argv=None):
    return 0,None


if __name__ == '__main__':
    sys.path.append(os.getcwd()+'/modules')
    import arff_reader
    r = main()
    if r[0] != 0:
        sys.stderr.write('Error'+r[1])
    sys.exit(r[0])
