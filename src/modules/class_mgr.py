#!/usr/bin/env python

import sys
import copy
import generalClass
import randomDT
import random
import arff_reader
import arff_writer
import time

class NoAlgException (Exception): pass

class ClassMgr:
    """
    This class intialize the classifier and manages the execution of the
    algorithms.
    It provides support for executing the cross validation, creating the
    testing and training dataset following the parameters given
    """

    def __init__(self, tr_arff, cl_attr, ts_arff, alg_name, out_arff,\
    ign_att, cross_per, class_par):
        """
        Initializes the manager class and loads the classifier selected,
        if used in cross validation mode, creates the datasets
        """
        self.attrs = tr_arff.get_attributes()
        self.cl_attr = cl_attr
        ignore_attributes = ign_att
        ignore_attributes.append(cl_attr)
        self.data, ranges = self.retrieve_ranges(copy.deepcopy(tr_arff),
                self.attrs, ignore_attributes)
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
            self.alg = randomDT.Classifier(self.data, ranges, out_arff,\
            self.attrs, cl_attr, ign_att, class_par)
        else:
            raise NoAlgException

    def retrieve_ranges(self, training, attributes, ignore_attributes):
        """
           This procedure acquire the range of each attribute in the training dataset and
           collect data into the memory
        """
        data = []
        range = dict()
        temp = training.get_next()
        dim = len(temp)

        while temp != None:
            for i in xrange(dim):
                if (attributes[i][0] not in ignore_attributes):
                    attr = attributes[i][0]
                    # If attribute is not in list, then add it
                    if (not range.__contains__(attr)):
                        range.__setitem__(attr, [])
            
                    if (attributes[i][1] == "string"):
                        if (not range[attr].__contains__(temp[i])):
                            range[attr].append(temp[i])
                    else:
                        if (range[attr] == []):
                            range[attr] = [sys.maxint, 0]
                        new = range[attr]
                        # So this is numeric or real
                        if range[attr][0] > float(temp[i]):
                            new[0] = float(temp[i])
                        if range[attr][1] < float(temp[i]):
                            new[1] = float(temp[i])
                        range[attr] = new
            data.append(temp)
            temp = training.get_next()
        return data, range

    def create_cross_ds(self, data, per, attr):
        """
        This function splits the dataset as specified via command line for
        performing the cross validation, returns the datasets ready for
        read in data
        """

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
        """
        This function computes the accuracy of the classification task
        performed, comparing the real classification read from the testing
        dataset, with the output of the classifier.
        """

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
            count = count + 1
            d = in_arff.get_next()
        if count == 0:
            return float(0)
        return float(hit) / float(count)

    def perform_test(self):
        """
        This function starts and manages the execution of the test, it
        stores the time taken for build the classifier, for classify the
        data, the number of total nodes and the number of leafs
        """
        tr_start = time.time()
        nodes, leafs, cl_leafs = self.alg.train()
        tr_stop = time.time()
        tr_time = tr_stop - tr_start
        cl_start = time.time()
        self.alg.classify(self.ts_arff)
        cl_stop = time.time()
        cl_time = cl_stop - cl_start
        return tr_time, cl_time, nodes, leafs, cl_leafs


