#!/usr/bin/env python

import sys
import os


def read_opts():
    from getopt import gnu_getopt as getopt
    res = {}
    for o,a in getopt(sys.argv,'t:a:d:o:')[0]:
        if o == '-t':
            res['train_file'] = a
        elif o == '-a':
            res['class_attr'] = a
        elif o == '-d':
            res['test_file'] = a
        elif o == '-o':
            res['out_file'] = a
    return res 

def main():
    opts = read_opts()
    try:
        os.stat(opts['train_file'])
        arff = arff_reader.ArffReader(opts['train_file'])
    except KeyError:
        return 1, 'No training dataset provided'
    except OSError:
        return 2, 'Training file not found'
    return 0,None

if __name__ == '__main__':
    sys.path.append(os.getcwd()+'/modules')
    import arff_reader
    r = main()
    if r[0] != 0:
        sys.stderr.write('Error: '+r[1]+'\n')
    sys.exit(r[0])
