#!/usr/bin/env python

import sys
import os

def read_opts():
    """
    Reads the options from command line
    """
    from getopt import gnu_getopt as getopt
    res = {}
    for o,a in getopt(sys.argv,'t:a:d:o:c:i:x:')[0]:
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
        elif o == '-i':
            res['ignored'] = a.split(',')
        elif o == '-x':
            res['cross'] = a
    return res 

def main():
    """
    The main function checks the parameters passed from the command line,
    instantiating the manager class following the desired options
    """
    opts = read_opts()
    cross = True
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
        cross_per = opts['cross']
    except KeyError:
        cross = False
        cross_per = -1

    if not cross:
        try:
            arff_test = arff_reader.ArffReader(opts['test_file'])
        except KeyError:
            return 4, 'Test dataset not provided'
        except OSError:
            return 5, 'Test dataset not found'
    else:
        arff_test = None

    try:
        arff_out = arff_writer.ArffWriter(opts['out_file'],'class')
    except KeyError:
        return 6, 'Output file not provided'
    
    try:
        class_alg = opts['classifier']
        if class_alg.count(',') == 1:
            class_alg, class_par = class_alg.split(',')
        else:
            class_par = None
    except KeyError:
        class_alg = 'generalClass'
    try:
        ign_att = opts['ignored']
    except KeyError:
        ign_att = []
    manager = class_mgr.ClassMgr(arff_in, attr, arff_test, class_alg,\
    arff_out, ign_att, cross_per, class_par)
    tt, ct, nodes, leafs = manager.perform_test()
    if cross:
        acc = manager.get_accuracy(opts['out_file'])
        print 'Accuracy =', acc 
    print 'Training time =', tt
    print 'Classification time =', ct
    print 'Nodes =', nodes
    print 'Leafs =', leafs
    print 'Memory = Uff, a lot XD'
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
