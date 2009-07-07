#!/usr/bin/env python

import sys
import generalClass
import randomDT
import random
import arff_reader
import arff_writer
import time

class NoAlgException (Exception): pass

class ClassMgr:
    
    def __init__(self, tr_arff, cl_attr, ts_arff, alg_name, out_arff,\
    ign_att, cross_per, class_par):
        self.attrs = tr_arff.get_attributes()
        self.cl_attr = cl_attr
        if class_par == None:
            class_par = 0
        else:
            class_par = int(class_par)
        if cross_per == -1:
            self.ts_arff = ts_arff
            self.tr_arff = tr_arff 
        else:
            self.tr_arff, self.ts_arff = self.create_cross_ds(tr_arff,\
            cross_per, self.attrs)
        if alg_name == 'generalClass':
            self.alg = generalClass.Classifier(self.tr_arff, out_arff,\
            self.attrs, cl_attr, ign_att, class_par)
        elif alg_name == 'randomDT':
            self.alg = randomDT.Classifier(self.tr_arff, out_arff,\
            self.attrs, cl_attr, ign_att, class_par)
        else:
            raise NoAlgException

    
    def create_cross_ds(self, data, per, attr):
        train_name = 'cv_train_'+per+'.arff'
        test_name = 'cv_test_'+per+'.arff'
        tr = arff_writer.ArffWriter(train_name, 'cross_train')
        ts = arff_writer.ArffWriter(test_name, 'cross_test')
        tr.write_headers(attr)
        ts.write_headers(attr)
        r = random.Random()
        d = data.get_next()
        while d != None:
            n = r.random() * 100
            if n < float(per):
                tr.write_data(d)
            else:
                ts.write_data(d)
            d = data.get_next()
        tr.store_buffer()
        ts.store_buffer()
        return arff_reader.ArffReader(train_name),\
        arff_reader.ArffReader(test_name)

    def get_accuracy(self, out_file):
        in_arff = arff_reader.ArffReader(out_file)
        d = in_arff.get_next()
        hit = 0
        err1 = 0
        err2 = 0
        count = 0
        for i in range(len(self.attrs)):
            if self.attrs[i][0] == self.cl_attr:
                lab = i
        d = in_arff.get_next()
        while d != None:
            if d[lab] == d[-1]:
                hit = hit + 1
            elif d[lab] == '<=50K' and d[-1] != d[lab]:
                err1 = err1 + 1
            elif d[lab] == '>50K' and d[-1] != d[lab]:
                err2 = err2 + 1
            count = count + 1
            d = in_arff.get_next()
        return float(hit) / float(count)

    def perform_test(self):
        tr_start = time.time()
        nodes, leafs, cl_leafs = self.alg.train()
        tr_stop = time.time()
        tr_time = tr_stop - tr_start
        cl_start = time.time()
        self.alg.classify(self.ts_arff)
        cl_stop = time.time()
        cl_time = cl_stop - cl_start
        return tr_time, cl_time, nodes, leafs, cl_leafs
