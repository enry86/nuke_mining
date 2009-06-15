#!/usr/bin/env python

import math

class Node:
    data = None
    label = None
    attr = None
    value = None
    child = None

    def init(self):
        self.data = []
        self.label = None
        self.attr = 0
        self.value = None
        self.child = {}

class Sorter:
    def __init__(self, index):
        self.index = index

    def cmp(self, x, y):
        if x[self.index] < y[self.index]:
            return -1
        elif x[self.index] == y[self.index]:
            return 0
        else:
            return 1



class Classifier:
    def __init__(self, ds_in, ds_out, attrs, cl_att):
        self.ds_in = ds_in
        self.ds_out = ds_out
        self.attrs = attrs
        self.cl_att = cl_att
        
        for i in range(len(self.attrs)):
            if self.attrs[i][0] == cl_att:
                self.class_n = i
        dataset = self.fetch_data()
        self.root = Node()
        self.root.data = dataset
        
    def fetch_data(self):
        list = []
        data = self.ds_in.get_next()
        while data != None:
            list.append(data)
            data = self.ds_in.get_next()
        return list

    def train(self):
        

    def info_gain(self, data, label, attr):
        return self.entropy(data, label) - self.con_entropy(data, label, attr)

    def num_info_gain(self, data, label, attr, thres):
        print 'olaola'

    def entropy(self, data, attr):
        entr = 0
        sorter = Sorter(attr)
        data.sort(sorter.cmp)
        i = 0
        while i < len(data):
            pr, i = self.prob(data, attr, 0, data[i][attr],i)
            entr = entr - (pr * math.log(pr,2))
        return entr

    def spec_con_entropy(self, data, label, attr, value, k):
        entr = 0
        count = 0
        sel = []
        i = k
        while i < len(data) and data[i][attr] == value:
            sel.append(data[i])
            i = i + 1
        sorter = Sorter(label)
        sel.sort(sorter.cmp)
        n = 0
        while n < len(sel):
            pr, n = self.prob(sel, label, 0, sel[n][label], n)
            entr = entr - (pr * math.log(pr, 2))
        return entr 

    def con_entropy(self, data, label, attr):
        entr = 0
        sorter = Sorter(attr)
        data.sort(sorter.cmp)
        i = 0
        entr = 0
        while i < len(data):
            sce = self.spec_con_entropy(data, label, attr, data[i][attr],i)
            pr, i = self.prob(data, attr, 0, data[i][attr],i) 
            entr = entr + (pr * sce)
        return entr

    def num_con_entropy(self, data, label, attr, thres, less):
        print 'olaola'
    
    def prob(self, data, attr, rel, value,i):
        count = 0
        if rel == -1:
            while i < len(data) and data[i][attr] < value:
                count = count + 1
                i = i + 1
        elif rel == 0:
            while i < len(data) and data[i][attr] == value:
                count = count + 1
                i = i + 1
        elif rel == 1:
            while i < len(data) and data[i][attr] > value:
                count = count + 1
                i = i + 1 
        elif rel == 2:
            while i < len(data) and data[i][attr] <= value:
                count = count + 1
                i = i + 1
        elif rel == 3:
            while i < len(data) and data[i][attr] >= value:
                count = count + 1
                i = i + 1
        return float(count) / len(data) , i 
        
            

    

        
