#!/usr/bin/env python

import math

class Node:
    data = []    
    label = None
    attr = None
    value = None
    child = {}

    def __init__(self):
        self.data = []
        self.label = None
        self.attr = 0
        self.value = None
        self.child = {}

class Sorter:
    def __init__(self, index, type):
        self.index = index
        self.type = type

    def do_cmp(self, x, y):
        if x < y:
            return -1
        elif x == y:
            return 0
        else:
            return 1

    def cmp(self, x ,y):
        if self.type == 'numeric':
            return self.do_cmp(float(x[self.index]), float(y[self.index]))
        else:
            return self.do_cmp(x[self.index], y[self.index])


class Classifier:
    def __init__(self, ds_in, ds_out, attrs, cl_att, ign_att ):
        self.ds_in = ds_in
        self.ds_out = ds_out
        self.attrs = attrs
        self.cl_att = cl_att
        self.ign_att = ign_att

        for i in range(len(self.attrs)):
            if self.attrs[i][0] == cl_att:
                self.class_n = i
        dataset = self.fetch_data()
        self.root = Node()
        self.root.data = dataset
        
    def fetch_data(self):
        list = []
        data = self.ds_in.get_next()
        i = 0 
        while data != None:
            list.append(data)
            data = self.ds_in.get_next()
        return list

    def train(self):
        self.train_node(self.root)

    def train_node(self, node):
        trained = False
        labels = self.find_values(node.data, self.class_n)
        l_max = 0
        l_max_val = None
        for l in labels:
            if labels[l] > l_max:
                l_max = labels[l]
                l_max_val  = l
        node.label = l_max_val
        if len(labels) <= 1:
            trained = True
            print node.label
        if not trained:
            max = 0.0
            max_att = 0
            for i in range(len(self.attrs)):
                if i != self.class_n and \
                self.ign_att.count(self.attrs[i][0]) == 0:
                    tmp, tr  = self.info_gain(node.data, self.class_n, i) 
                    if tmp > max:
                        max = tmp
                        max_att = i
                        max_tr = tr
            if max == 0.0:
                trained = True
            else:
                node.attr = max_att
                node.value = max_tr
            if node.value != None and not trained:
                lt, mt = self.num_split_dataset(node.data, node.attr, node.value)
                lc = '<'+node.value.__str__()
                node.child[lc] = Node()
                node.child[lc].data = lt
                mc = '>'+node.value.__str__()
                node.child[mc] = Node()
                node.child[mc].data = mt
            elif node.value == None and not trained:
                vals = self.split_dataset(node.data, max_att)
                for v in vals:
                    node.child[v] = Node()
                    node.child[v].data = vals[v]
            for c in node.child:
                self.train_node(node.child[c])

            

    def num_split_dataset(self, data, attr, value):
        sorter = Sorter(attr, self.attrs[attr][1])
        data.sort(sorter.cmp)
        i = 0
        while i < len(data) and data[i][attr] < value:
            i = i + 1
        return data[:i],data[i:]
            

    def find_values(self, data, att):
        res = {}
        for d in data:
            if not res.has_key(d[att]):
                res[d[att]] = 1
            else:
                res[d[att]] = res[d[att]] + 1
        return res

    def split_dataset(self, data, att):
        res = {}
        for d in data:
            if not res.has_key(d[att]):
                res[d[att]] = []
            res[d[att]].append(d)
        return res


    def info_gain(self, data, label, attr):
        entr = self.entropy(data,label)
        if self.attrs[attr][1] == 'numeric':
            sorter = Sorter(attr, self.attrs[attr][1])
            data.sort(sorter.cmp)
            b_size = 10
            if len(data) < b_size:
                b_size = len(data)
            step = len(data) / b_size
            c = step
            max = 0.0
            t_max = 0.0
            while c < len(data):
                tmp = entr - self.num_con_entropy(data, label, attr, data[c][attr])
                if tmp > max:
                    max = tmp
                    t_max = data[c][attr]
                c = c + step
            return max, t_max 
        else:
            return entr - self.con_entropy(data, label, attr), None

    def entropy(self, data, attr):
        entr = 0
        sorter = Sorter(attr, self.attrs[attr][1])
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
        sorter = Sorter(label, self.attrs[label][1])
        sel.sort(sorter.cmp)
        n = 0
        while n < len(sel):
            pr, n = self.prob(sel, label, 0, sel[n][label], n)
            entr = entr - (pr * math.log(pr, 2))
        return entr 

    def con_entropy(self, data, label, attr):
        entr = 0
        sorter = Sorter(attr, self.attrs[attr][1])
        data.sort(sorter.cmp)
        i = 0
        entr = 0
        while i < len(data):
            sce = self.spec_con_entropy(data, label, attr, data[i][attr],i)
            pr, i = self.prob(data, attr, 0, data[i][attr],i) 
            entr = entr + (pr * sce)
        return entr

    def num_con_entropy(self, data, label, attr, thres):
        sorter = Sorter(attr, self.attrs[attr][1])
        data.sort(sorter.cmp)
        pr_less, i = self.prob(data, attr, -1, thres, 0)
        pr_more = 1 - pr_less
        en_less = self.entropy(data[:i], label)
        en_more = self.entropy(data[i:], label)
        return (en_less * pr_less) + (en_more * pr_more)
    
    def prob(self, data, attr, rel, value, i):
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
    
            
            

    

        
