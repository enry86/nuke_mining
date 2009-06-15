#!/usr/bin/env python

import sys
import os

def read_opts():
    from getopt import gnu_getopt as getopt
    res = {}
    for o,a in getopt(sys.argv,'t:a:d:o:c:')[0]:
        if o == '-t':
            res['train_file'] = a
        elif o == '-a':
            res['class_attr'] = a
        elif o == '-d':
            res['test_file'] = a
        elif o == '-o':
            res['out_file'] = a
        elif o == '-c':
            res['classifier'] = a
    return res 

def main():
    opts = read_opts()
    try:
        os.stat(opts['train_file'])
        arff_in = arff_reader.ArffReader(opts['train_file'])
    except KeyError:
        return 1, 'No training dataset provided'
    except OSError:
        return 2, 'Training file not found'
    
    try:
        attr = opts['class_attr']
    except KeyError:
        return 3, 'Class attribute not provided'
    
    try:
        arff_test = arff_reader.ArffReader(opts['test_file'])
    except KeyError:
        return 4, 'Test dataset not provided'
    except OSError:
        return 5, 'Test dataset not found'

    try:
        arff_out = arff_writer.ArffWriter(opts['out_file'],'class')
    except KeyError:
        return 6, 'Output file not provided'
    
    try:
        class_alg = opts['classifier']
    except KeyError:
        class_alg = 'RandomDT'

    manager = class_mgr.ClassMgr(arff_in, attr, arff_test, class_alg, arff_out)
    manager.perform_test()
    return 0,None

if __name__ == '__main__':
    sys.path.append(os.getcwd()+'/modules')
    sys.path.append(os.getcwd()+'/algs')
    import arff_reader
    import arff_writer
    import class_mgr
    r = main()
    if r[0] != 0:
        sys.stderr.write('Error: '+r[1]+'\n')
    sys.exit(r[0])
