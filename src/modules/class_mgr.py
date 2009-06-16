#!/usr/bin/env python

import sys
import generalClass

class NoAlgException (Exception): pass

class ClassMgr:
    
    def __init__(self, tr_arff, cl_attr, ts_arff, alg_name, out_arff,
    ign_att):
        attrs = tr_arff.get_attributes()
        if alg_name == 'generalClass':
            self.alg = generalClass.Classifier(tr_arff, out_arff, attrs,
            cl_attr,ign_att)
        else:
            raise NoAlgException
    

    def perform_test(self):
        self.alg.train()
