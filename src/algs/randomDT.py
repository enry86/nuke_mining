#!/usr/bin/env/python

import math
import random
import time

class RandomDT:
    """
        In leaf node label indicate the class. The leaf one is recognized by
        the absence of childs (set to None).
        If the feature is discrete, then the threshold is None, else is the
        threshold and the left child (corresponding as 0) is '<' and the right
        one is '>='
    """

    def __init__(self, attributes, ranges):
        """
           Initialize the tree, setting the root or the leaf
        """
        # If true than is requested a leaf
        if ranges == 0:
            self.label = attributes
            self.threshold = 0
            self.childs = None
            self.examples_n = 0
        else:
            # Root node
            random.seed(time.time())
            # Not used cause difficulty to retrieve the object position in the
            # list:: self.label = random.choice(attributes)[0]
            self.random_element = random.randrange(0,len(attributes))
            self.label = attributes[self.random_element][0]
            self.threshold = random.uniform(ranges[self.random_element][0],
                ranges[self.random_element][1])
            self.childs = []
            self.examples_n = 0

    def get_probability(self, tuple, attributes):
        """
            This provide the probability P(y|x) accrodingly to trained model,
            where x is the training set
            tuple       is the tuple to classify
            attributes  is the list of attributes
        """
        tree = self
        while tree.childs != None:
            value = tuple[attributes.index(tree.label)]
            parent = tree
            if float(value) < float(tree.threshold):
                tree = tree.childs[0]
            else:
                tree = tree.childs[1]
            if tree == None:
                return '', 0
        return tree.label, float(tree.examples_n)/float(parent.examples_n)

    def range_splitting(self, ranges):
        ranges_tmp_sx = ranges[:]
        ranges_tmp_dx = ranges[:]
        ranges_tmp_sx[self.random_element] = [ranges[self.random_element][0],\
                self.threshold]
        ranges_tmp_dx[self.random_element] = [self.threshold,\
                ranges[self.random_element][1]]
        return ranges_tmp_sx, ranges_tmp_dx

    def generate_tree(self, attributes, ranges, depth):
        """
           Generate the tree according to the attributes, chosing randomly at
           each node one of them. In particular the depth of tree is set on
           the dimension of attributes
           attributes   is the list of attributes
           ranges       is a dictionary of 'attribues': 'ranges'
           depth        is the forseen depth
        """
        if depth == 0:
            return None
        node = RandomDT(attributes, ranges)

        r_sx, r_dx = node.range_splitting(ranges)

        left_child = self.generate_tree(attributes, r_sx, depth - 1)
        right_child = self.generate_tree(attributes, r_dx, depth - 1)
        
        node.childs.append(left_child)
        node.childs.append(right_child)
        return node

    def generate(self, attributes, ranges):
        # Dictionary with the attribute as key
        # ranges_tmp = dict([(i[0], j) for i,j in zip(attributes, ranges)])
        r_sx, r_dx = self.range_splitting(ranges[:])
        left_child = self.generate_tree(attributes, r_sx, len(attributes) - 1)
        right_child = self.generate_tree(attributes, r_dx, len(attributes) - 1)
        self.childs.append(left_child)
        self.childs.append(right_child)


class Forest:
    """
        This class contains the Forest build up of Random Decision Tree.
        The main parameters are the number of random tree to generate, that
        are at least 30 (for achieve a good accuracy) and the tree's depth
        that is 0 as default since the attributes are required.
        The trees list contain the root nodes of the Forest
    """
    
    def __init__(self, trees_n, attributes, range):
        """
            This is the constructor of the forest of RDTs. Default dimension
            is 30 as suggested in order to obtain a good estimate with low
            variance.
            trees_n     is the number of tree to construct
            attributes  are the dataset's useful attributes
            range       is the range of the continuous dataset's attributes
        """
        if trees_n != 0:
            self.trees_n = trees_n
        else:
            self.trees_n = 30
        self.trees = []
        self.tree_depth = len(attributes)
        self.attributes = attributes
        self.ranges = range[:]
        
    def visit_tree(self, tree, space, pos):
        """
            Only for testing propouse. It represents the tree
        """
        if tree == None:
            return True
        print space + tree.label+' ('+pos+')'+'   '+str(tree.threshold)+\
                '                          '+str(tree.examples_n)
        if (tree.childs == None):
            return True
        self.visit_tree(tree.childs[0],space + '   ','sx')
        self.visit_tree(tree.childs[1],space + '   ','dx')

    def get_statistics(self):
        """
            Return the number of trees starting with the relative attribute
        """
        att_dict = dict([(i[0], 0) for i in self.attributes])
        print "==================================================\nTREES"
        print "=================================================="
        for i in xrange(len(self.trees)):
            att_dict[self.trees[i].label] += 1
            print "Root:  label", self.trees[i].label, "    Threshold", self.trees[i].threshold
        print "==================================================\nRESULTS"
        print "=================================================="
        print att_dict
        print "=================================================="

    def populate(self):
        """
            Generate tree_n different RDT based on the attributes given but
            ignoring data
        """
        for i in xrange(self.trees_n):
            rdt = RandomDT(self.attributes, self.ranges)
            rdt.generate(self.attributes, self.ranges)
            self.trees.append(rdt)
        #self.get_statistics()


class Trainer:
    """
        self.data are data
        self.range is a list of form [min, max] used to generate the random
        threshold of trees
    """

    def __init__(self):
        pass

    def feature_expansion(self, example):
        """
            Accordingly with the solution proposed by Wei Fan et al. the
            number of features are weak. So with this function we increment
            the number from 4 to 12: each data value is supported by two
            non-linear value function of it.
        """
        expanded_example = []
        for i in example:
            expansion_1 = i * i
            expansion_2 = math.log(i + 1)
            expanded_example.append([i, expansion_1, expansion_2])
        return expanded_example

    def purge_tuple (self, element, ignore):
        """
            Remove from tuple the element to ignore
            element     is the tuple under analysis
            ignore      is the position of attributes to ignore
        """
        purged = []
        for i in xrange(len(element)):
            if (not ignore.__contains__(i)):
                purged.append(element[i])
        return purged

    def tree_training(self, tree, element, ignore, class_att):
        """
            Perform the training of a tree basing the entire dataset
            tree        is the current tree to train
            element     is the tuple the tree should be trained with
            ignore      are the position of the tuple to ignore
            class_att   is the position of the classifying attribute
        """
        tree.examples_n += 1
        purged = self.purge_tuple(element, ignore)
        for i in xrange(len(purged)):
            if float(purged[tree.random_element]) < float(tree.threshold):
                if tree.childs[0] == None:
                    tree.childs[0] = RandomDT(element[class_att], 0)
                tree = tree.childs[0]
            else:
                if tree.childs[1] == None:
                    tree.childs[1] = RandomDT(element[class_att], 0)
                tree = tree.childs[1]
            tree.examples_n += 1

    def train (self, rdt_forest, training_data, ignore_attributes, class_att_pos):
        """
            The procedure aims to train the rdtForest given a starting dataset
            rdt_forest          is the forest of RDT
            training_data       is the dataset in Main Memory
            ignore_attributes   are the positions to ignore of a tuple
            class_att_pos       is the position of the classifying attribute
        """
        tmp = training_data.pop(0)
        while tmp != None: 
            try:
                for i in xrange(len(rdt_forest.trees)):
                    self.tree_training(rdt_forest.trees[i], tmp,\
                            ignore_attributes, class_att_pos)
                tmp = training_data.pop(0) 
            except IndexError:
                tmp = None


class Classifier:
    def __init__(self, tr_arff, out_arff, attrs, cl_attr, ign_attr, trees_n):
        """
            Core algorithm function invoked to run the RDT algorithm on
            given parameters.
            tr_arff     is the incoming training data set resident on a "arff"
                        file
            out_arff    is the the output file in arff format
            attrs
            cl_attr     is the attribute to classify
        """
        self.training = tr_arff
        self.outgoing = out_arff
        self.full_attributes = attrs
        self.attributes, self.ignore_att_pos, self.class_att_pos = self.purify(attrs, cl_attr, ign_attr)
        self.class_attribute = cl_attr
        self.ignore_attribute = ign_attr
        self.data = []   

        # Forest of trees_number Random Decision Tree
        # self.retrievfe_range() EMPTY the self.training...if you use
        # everywhere that, you lose data
        print "Generating Forest"
        self.rdtForest = Forest(trees_n, self.attributes,
                self.retrieve_range())
        print "Populating Forest"
        self.rdtForest.populate() 

    def retrieve_range(self):
        """
            This procedure acquire the range of each attribute in the training dataset and
            collect data into the memory
        """
        import sys
        range = []
        max = []
        #mind = []
        temp = self.training.get_next()
        dim = len(temp) - len(self.ignore_att_pos)
        for i in xrange(dim):
            max.append(0)
        #    min.append(sys.maxint)
        dim_record = len(temp)
        while temp != None:
            j = 0
        #    r = 0
            for i in xrange(dim_record):
                if (i not in self.ignore_att_pos):
                    if max[j] < float(temp[i]):
                        max[j] = float(temp[i])
        #            if min[r] > float(temp[i]):
        #                min[r] = float(temp[i])
                    j += 1
        #            r += 1
            self.data.append(temp)
            temp = self.training.get_next()
        for i in xrange(dim):
            range.append([0, max[i]])
            #range.append([min[i], max[i]])
        return range

    def purify (self, attrs, cl_attr, ign_attr):
        """
            This function take the attributes list retrieved and consider
            returns the list of  useful attributes
            attrs       list of attributes of type: ['Name', 'Value']
            cl_attr     attribute to perform the classification: 'Name'
            ign_attr    list of attribute to ignore ['Name', 'Name']
        """
        attrs_tmp = attrs[:]
        holy_list = []
        ignore_list = []
        dim = len(attrs)
        class_att_pos = None
        for i in xrange(dim):
            tmp = attrs_tmp.pop()
            if (cl_attr != tmp[0]):
                if (not ign_attr.__contains__(tmp[0])):
                    holy_list.append(tmp)
                else:
                    ignore_list.append( (dim - 1) - i)
            else: 
                class_att_pos = dim - 1 - i
                ignore_list.append( (dim - 1) - i)
        ignore_list.sort()
        holy_list.reverse()
        return holy_list, ignore_list, class_att_pos

    def train(self):
        """
            Given the RDT's Forest generated, the dataset in Main Memory, and
            the list of attributes, train all the RDTs contained in the Forest
            with the data
        """
        trainer = Trainer()
        trainer.train(self.rdtForest, self.data, self.ignore_att_pos,
                self.class_att_pos)
        return int(math.pow(len(self.attributes), 2)), int(math.pow(2,\
                len(self.attributes) - 1)), []
    
    def loss_function(self, predictions):
        """
            This is the function that is charged to do the prediction once the
            probabilities of classes are given.
            It returns the best one. At moment i 0-1 function
            predictions     dictionary  'Class_label'='Probability'
        """
        max = predictions.keys()[0]
        for i in predictions:
            if predictions[i] > predictions[max]:
                max = i
        return max 

    def classify_tuple(self, tuple, attributes):
        """
            Given a tuple, the function retrieve the classification
            probability coming from each Tree in the Forest, scanning all the
            tuple attributes, ignoring the ones not present in the tree
        """
        sum = dict()
        for i in xrange(len(self.rdtForest.trees)):
            class_label, prob =  self.rdtForest.trees[i].get_probability(tuple,\
                attributes)
            if (not sum.__contains__(class_label)):
                sum.__setitem__(class_label, 0)
            sum[class_label] += prob
        for i in sum:
            sum[i] = sum[i]/len(self.rdtForest.trees)
        return self.loss_function(sum)

    def simplified_attrs(self, attributes):
        """
            Simple reduce a list of list in a list of attributes name
        """
        tmp = []
        for i in attributes:
            tmp.append(i[0])
        return tmp

    def classify(self, file):
        """
            Given a set of tuples, peform the classification according with
            the rdtForest train. Each tuple is enriched by the predict label
            using the trained model. The new tuple is then written in the
            output file.
            file        the dataset to classify, in arff format
        """
        #self.rdtForest.visit_tree(self.rdtForest.trees[0],'','root')
        attributes = file.get_attributes()
        simple_attrs = self.simplified_attrs(attributes)
        attributes.append([str(self.class_attribute)+'_label',\
                self.full_attributes[self.class_att_pos][1]])
        self.outgoing.write_headers(attributes)
        tmp = file.get_next()
        while tmp != None:
            prediction = self.classify_tuple(tmp, simple_attrs)
            tmp.append(prediction)
            self.outgoing.write_data(tmp)
            tmp = file.get_next()
        self.outgoing.store_buffer()
