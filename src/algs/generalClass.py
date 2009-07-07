#!/usr/bin/env python

import math

class Node:
    """
    This class represents a node in the decision tree used for
    classification.
    The difference between a normal node and a leaf is that a leaf has no
    child.
    Label is the class which this node gives to the data.
    """
    data = []    
    label = None
    attr = None
    value = None
    child = {}
    ign = []

    def __init__(self):
        self.data = []
        self.label = None
        self.attr = -1
        self.value = None
        self.child = {}
        self.ign = []

class Sorter:
    """
    This class is useful for managing the sorting of a list of lists based
    on a choosen field
    """
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
    """
    This class repersent the core of the classifier, contains the function
    used for both building the tree and classify data.
    """
    def __init__(self, ds_in, ds_out, attrs, cl_att, ign_att, thr_num):
        """
        In the constructor there is a check for the parameter which can
        specify the number of thershold to test for the maximum
        information gain for numeric values.

        ds_in   input dataset
        ds_out  output dataset
        attrs   attributes of the dataset
        cl_att  class attribute
        ign_att array of attributes to be ignored in building the tree
        thr_num number of thresold to test, if 0 a default parameter 7 is
                used
        """
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
        self.root.ign = ign_att
        self.nodes = 0
        self.leafs = 0
        self.cl_leafs = {}
        if thr_num == 0:
            self.b_size = 7;
        else:
            self.b_size = thr_num


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
        return self.nodes, self.leafs, self.cl_leafs

    def train_node(self, node):
        """
        This function train a single node, chosing the best attribute and
        thresold for splitting
        """

        self.nodes = self.nodes + 1
        trained = False
        labels = self.find_values(node.data, self.class_n)
        l_max = 0
        l_min = -1
        l_max_val = None
        l_min_val = None
        for l in labels:
            if l_min == -1:
                l_min = labels[l]
                l_min_val = l
            elif labels[l] <= l_min:
                l_min = labels[l]
                l_min_val = l
            if labels[l] > l_max:
                l_max = labels[l]
                l_max_val  = l
        if l_max != l_min or len(labels) == 1:
           node.label = l_max_val
        if len(labels) <= 1:
            trained = True
            self.leafs = self.leafs + 1
            if self.cl_leafs.has_key(node.label):
                self.cl_leafs[node.label] = self.cl_leafs[node.label] + 1
            else:
                self.cl_leafs[node.label] = 1
        if not trained:
            max = 0.0
            max_att = 0
            for i in range(len(self.attrs)):
                if i != self.class_n and \
                node.ign.count(self.attrs[i][0]) == 0:
                    tmp, tr  = self.info_gain(node.data, self.class_n, i) 
                    if tmp > max:
                        max = tmp
                        max_att = i
                        max_tr = tr
            if max == 0.0:
                trained = True
                self.leafs = self.leafs + 1
                if self.cl_leafs.has_key(node.label):
                    self.cl_leafs[node.label] = self.cl_leafs[node.label] + 1
                else:
                    self.cl_leafs[node.label] = 1
            else:
                node.attr = max_att
                node.value = max_tr
            if node.value != None and not trained:
                lt, mt = self.num_split_dataset(node.data, node.attr, node.value)
                node.child[0] = Node()
                node.child[0].data = lt
                node.child[1] = Node()
                node.child[1].data = mt
            elif node.value == None and not trained:
                node.ign.append(max_att)
                vals = self.split_dataset(node.data, max_att)
                for v in vals:
                    node.child[v] = Node()
                    node.child[v].data = vals[v]
            for c in node.child:
                node.child[c].ign = node.ign
                node.child[c].label = node.label
                self.train_node(node.child[c])

            

    def num_split_dataset(self, data, attr, value):
        """
        Splits the dataset with respect to a certain thresold, used for
        numeric values
        """

        sorter = Sorter(attr, self.attrs[attr][1])
        data.sort(sorter.cmp)
        i = 0
        while i < len(data) and data[i][attr] < value:
            i = i + 1
        return data[:i],data[i:]
            
    def split_dataset(self, data, att):
        """
        Splits the dataset with respect to the value of the field att
        """
        res = {}
        for d in data:
            if not res.has_key(d[att]):
                res[d[att]] = []
            res[d[att]].append(d)
        return res

    def find_values(self, data, att):
        """
        Searches anc counts the occurences of different values in a list
        of strings
        """
        res = {}
        for d in data:
            if not res.has_key(d[att]):
                res[d[att]] = 1
            else:
                res[d[att]] = res[d[att]] + 1
        return res

    def info_gain(self, data, label, attr):
        """
        Computes the information gain of the label and the attribute att,
        if att is a numeric attribute, the function comuputes the
        conditional information gain for a b_size number of thresolds
        """
        entr = self.entropy(data,label)
        if self.attrs[attr][1] == 'numeric':
            sorter = Sorter(attr, self.attrs[attr][1])
            data.sort(sorter.cmp)
            b_size = self.b_size
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
        """
        Computes the entropy for an attribute, specified by att
        """
        entr = 0
        sorter = Sorter(attr, self.attrs[attr][1])
        data.sort(sorter.cmp)
        i = 0
        while i < len(data):
            pr, i = self.prob(data, attr, 0, data[i][attr],i)
            entr = entr - (pr * math.log(pr,2))
        return entr

    def con_entropy(self, data, label, attr):
        """
        This funciton computes the conditional entropy of the label with
        respect to a particular attribute
        """

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


    def spec_con_entropy(self, data, label, attr, value, k):
        """
        This function computes the specific conditional entropy of the
        label with respect to an attribute attr with a specific value 
        """
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

    
    def num_con_entropy(self, data, label, attr, thres):
        """
        This function computes the specifc conditional entropy for a
        numeric attribute, with respect to a particular attribute and a
        specified threshold
        """
        sorter = Sorter(attr, self.attrs[attr][1])
        data.sort(sorter.cmp)
        pr_less, i = self.prob(data, attr, -1, thres, 0)
        pr_more = 1 - pr_less
        en_less = self.entropy(data[:i], label)
        en_more = self.entropy(data[i:], label)
        return (en_less * pr_less) + (en_more * pr_more)
    
    def prob(self, data, attr, rel, value, i):
        """
        Utility function for computing the probability of a certain
        condition in the dataset
        """
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
    
            
    def classify(self, ds_test):
        """
        This function starts the classification task, launching the base
        case for the recursive process
        """

        attr = ds_test.get_attributes()
        attr.append([self.attrs[self.class_n][0]+'_label',self.attrs[self.class_n][1]])
        self.ds_out.write_headers(attr)
        d = ds_test.get_next()
        while d != None:
            label = self.do_classification(self.root, d, attr)
            d.append(label)
            self.ds_out.write_data(d)
            d = ds_test.get_next()
        self.ds_out.store_buffer()

    def do_classification(self, node, sample, attr):
        """
        Recursive step for the classification task, this function visits
        the nodes of the tree following the condition encountered at every
        step
        """

        if node.attr == -1:
            return node.label
        else:
            for a in range(len(attr)):
                if attr[a][0] == self.attrs[node.attr][0]:
                    val = sample[a]
                    att = a
            if node.value == None:
                if node.child.has_key(sample[att]):
                    return self.do_classification(node.child[sample[att]],\
                    sample, attr)
                else:
                    return node.label
            else:
                if float(sample[att]) < float(node.value):
                    child = 0
                else:
                    child = 1
                return self.do_classification(node.child[child], sample,\
                attr)


        
