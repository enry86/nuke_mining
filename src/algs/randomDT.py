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

        Each node is build up of
        label       'Attribute_name' 'Attribute_type'
        threshold   if type is string   =>  ['value_1', ..., 'value_n']
                    else                =>  numeric_random_threshold
                    IF LEAF             =>  PREDICTION
        childs      if type is string   =>  [child_1, ..., child_n]
                        wrt the order in threshold
                    else                =>  [child_1, child_2]
                        wrt threshold, child_1 has value <
        """

    def __init__(self, attributes, ranges):
        """
           Initialize the tree, setting the root or the leaf
           attributes      ['Attribute_name', 'Attribute_value']
           ranges          
                if Attribute is STRING  ['Attribute_name', ['value_1', ..., 'value_n']
                else                    ['Attribute_name', [min_value,  max_value]]
        """
        
        # LEAF => label is the class
        if ranges == None:
            self.label = attributes
            self.threshold = ""
            self.childs = None
        else:
            # Root node 
            random_element = random.choice(attributes)
            self.label = random_element
    
            if random_element[1] == 'string':
                self.threshold = ranges[random_element[0]]
                attributes.remove(random_element)
                ranges.pop(random_element[0])
            else:
                self.threshold = random.uniform(ranges[random_element[0]][0],\
                    ranges[random_element[0]][1])
            self.childs = []
        self.examples_n = dict() 

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
            if tree.label[1] == "string":
                try:
                    tree = tree.childs[tree.threshold.index(value)]
                except ValueError:
                    return None
            else:
                if float(value) < float(tree.threshold):
                    tree = tree.childs[0]
                else:
                    tree = tree.childs[1]
            if tree == None:
                return parent.examples_n
        return tree.examples_n#tree.label, float(tree.examples_n)/float(parent.examples_n)

    def range_splitting(self, attributes, ranges):
        """
            Split the range of a numeric attribute
            attributes      ['Attribute_name', 'Attribute_value']
            ranges          
                if Attribute is STRING  ['Attribute_name', ['value_1', ..., 'value_n']
                else                    ['Attribute_name', [min_value,  max_value]]
        """
        ranges_tmp_sx = ranges.copy()
        ranges_tmp_dx = ranges.copy()
        ranges_tmp_sx[self.label[0]] = [ranges[self.label[0]][0],\
                self.threshold]
        ranges_tmp_dx[self.label[0]] = [self.threshold,\
                ranges[self.label[0]][1]]
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
        # If there are no mode attributes or the depth is zero, the return a
        # node leaf
        if (depth == 0) or (attributes == []):
            return None
        
        #print "\nLEVEL ", depth,"   CURRENT", self.label
        #print "ATTRIBUTES ", attributes
        #print "RANGES ", ranges

        node = []
        if self.label[1] == "string":
            # Generate the number of childs accordingly with the possibile
            # elements
            current_ranges = ranges.copy()
            current_attributes = attributes[:]

            for i in self.threshold:
                ranges = current_ranges.copy()
                attributes = current_attributes[:]
                
                #print "CHILD BEFORE, ",ranges
                child = RandomDT(attributes, ranges)
                #print "CHILD AFTER, ", ranges
                child.childs = child.generate_tree(attributes, ranges, depth - 1)
                node.append(child)
        else:
            # Generate two childs for according with the threshold
            r_sx, r_dx = self.range_splitting(attributes, ranges)
            left_child = RandomDT(attributes, ranges)
            right_child = RandomDT(attributes, ranges)

            left_child.childs = left_child.generate_tree(attributes, r_sx, depth - 1)
            right_child.childs = right_child.generate_tree(attributes, r_dx, depth - 1)
        
            node.append(left_child)
            node.append(right_child)
        return node

    def generate(self, attributes, ranges, depth):
        """
            Generate the Forest of RDT
            attributes      ['Attribute_name', 'Attribute_value']
            ranges          
                if Attribute is STRING  ['Attribute_name', ['value_1', ..., 'value_n']
                else                    ['Attribute_name', [min_value,  max_value]]
        """
        self.childs = self.generate_tree(attributes, ranges, depth - 1)


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
            attributes  are the dataset's attributes without both the ignoring
                        ones and the classification one
            range       is the range of the continuous dataset's attributes
        """
        if (trees_n != 0) and (trees_n != None):
            self.trees_n = trees_n
        else:
            self.trees_n = 30
        self.trees = []
        # Adding one to include the 
        #if ( len(attributes) > 10 ):
        #    self.tree_depth = (len(attributes) + 1 ) / 2
        #else:
        #    self.tree_depth = len(attributes) + 1 
        self.tree_depth = len(attributes) + 1
        self.attributes = attributes
        self.ranges = range

    def visit_tree(self, tree, space, pos):
        """
            Only for testing propouse. It represents the tree
        """
        # If the node is None, it doesn't exist
        if tree == None:
            return 0

        if tree.label[1] != "string":
            trh = str(tree.threshold)
        else:
            trh = "LIST"
        # Print the attribute, its position, the threshold and the number of
        # training examples through it
        print space + tree.label[0] +' ('+pos+')'+'   '+trh+\
                '                          '+str(tree.examples_n)
        
        if (tree.childs == None) or (tree.childs == []):
            return 1
        j = 0
        sum = 0
        for i in tree.childs:
            sum += self.visit_tree(i,space + '   ',str(j))
            j += 1
        return sum + 1

    def populate(self):
        """
            Generate tree_n different RDT based on the attributes given but
            ignoring data
        """
        depth = self.tree_depth

        for i in xrange(self.trees_n):
            start = time.time()
            attributes = self.attributes[:]
            ranges = self.ranges.copy()
            start2 = time.time()

            rdt = RandomDT(attributes, ranges)
            rdt.generate(attributes, ranges, depth)
            self.trees.append(rdt)
            #print "JUST BUILT ", start2 - start, time.time() - start2


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

    def tree_training(self, tree, element, attributes, ignore, class_att):
        """
            Perform the training of a tree basing the entire dataset
            tree        is the current tree to train
            element     is the tuple the tree should be trained with
            ignore      are the position of the tuple to ignore
            class_att   is the position of the classifying attribute
        """
        #print "ATT", attributes
        #print "Class_att", class_att, "\n"

        while tree != None:
            #print "Element", element, "\nTree", tree.label, "\nto check", attributes.index(tree.label)
            check_attr = attributes.index(tree.label)
            
            if ( not tree.examples_n.__contains__(element[class_att]) ):
                tree.examples_n.__setitem__(element[class_att], 1)
            else:
                tree.examples_n[element[class_att]] += 1
            
            if (tree.label != attributes[class_att]):# and (element[check_attr] != "?"):
                if tree.label[1] == "string":
                    pos = tree.threshold.index(element[check_attr])
                    if tree.childs == None:
                        tree.childs = [None] * len(tree.threshold)
                    
                    if tree.childs[pos] == None:
                        tree.childs[pos] = RandomDT(attributes[class_att], None)
                        tree.childs[pos].examples_n.__setitem__(element[class_att], 1)
                    #   tree = None
                    #else:
                    #    tree = tree.childs[pos]
                    tree = tree.childs[pos]

                else:
                    if tree.childs == None:
                        tree.childs = [None, None]
                    
                    if float(element[check_attr]) < float(tree.threshold):
                        dir = 0
                    else:
                        dir = 1

                    if tree.childs[dir] == None:
                        tree.childs[dir] = RandomDT(attributes[class_att], None)
                        tree.childs[dir].examples_n.__setitem__(element[class_att], 1)

                    tree = tree.childs[dir]
            else:
                tree = None

    def train (self, rdt_forest, training_data, attributes, ignore_attributes, class_att_pos):
        """
            The procedure aims to train the rdtForest given a starting dataset
            rdt_forest          is the forest of RDT
            training_data       is the dataset in Main Memory
            ignore_attributes   are the positions to ignore of a tuple
            class_att_pos       is the position of the classifying attribute
        """
        start0 = time.time()
        tmp = training_data.pop(0)
        while tmp != None: 
            try:
                #start = time.time()
                for i in rdt_forest.trees:
                    self.tree_training(i, tmp, attributes, ignore_attributes, class_att_pos)
                #print tmp, "TRAINED IN ", time.time() - start
                tmp = training_data.pop(0) 
            except IndexError:
                tmp = None
        #print "ALL TRAINED ", time.time() - start0 
   

    def tree_updating(self, tree, element, full_attributes, attributes, ranges, depth,\
            class_attribute, class_att_pos):

        #print "ATTRS,", attributes, " DEPTH ", depth 

        # If is the root node, tree is the Forest of RDT
        #if depth == self.rdtForest.tree_depth:
        #    node = RandomDT(attributes[:], ranges.copy())
        #    tree.trees.append(node)
        #    tree = node

        # Update the number of examples wrt classification attribute
        if ( not tree.examples_n.__contains__(element[class_att_pos]) ):
            tree.examples_n.__setitem__(element[class_att_pos], 1)
        else:
            tree.examples_n[element[class_att_pos]] += 1

        # If the current tree is the leaf, the tuple is completely analyzed
        if depth == 0:
            return True
        
        # If the node is the last but one, require to generate a leaf node
        if depth == 1:
            next_is_leaf = 1
        else:
            next_is_leaf = 0

        check_attr = full_attributes.index(tree.label)
        
        #print "RANGES ", ranges

        #if ( tree.label != attributes[class_attribute]):
        #    print "ERROR: label is different", tree.label, attributes[class_attribute]

        # If the comparing attribute is a string
        if ( tree.label[1] == "string" ):
            
            # Retrieve the position in the childs' list, where
            # element[check_attr] is the value of the attribute stored in
            # tree.label[0]
            position = tree.threshold.index(element[check_attr])

            if ( attributes.__contains__(tree.label) ):
                    attributes.remove(tree.label)

            # If is the first time that the node is reached
            if ( tree.childs == [] ):
                current_attributes = attributes[:]
                current_ranges = ranges.copy()
                
                # Copy is needed to preserve the integrity of the
                # parameters for the siblings and to give to descendant
                # the modified ones
                attributes = current_attributes[:]
                ranges = current_ranges.copy()
                tree.childs = [None] * len(tree.threshold)

            if next_is_leaf:
                child = RandomDT(full_attributes[class_att_pos], None)
            else:
                child = RandomDT(attributes, ranges)
            
            # Remove the value just checked, since for strings it cannot
            # appear in the subtree by construction
            #element.pop(check_attr)
            tree.childs[position] = child
            tree = tree.childs[position]
        # If the comparing attribute is a value
        else:
            if float(element[check_attr]) < float(tree.threshold):
                dir = 0
            else:
                dir = 1

            if tree.childs == []:
                tree.childs = [None, None]

            if tree.childs[dir] == None:
                if next_is_leaf:
                    child = RandomDT(full_attributes[class_att_pos], None)
                else:
                    child = RandomDT(attributes, ranges)
                    r_sx, r_dx = tree.range_splitting(attributes, ranges)

                    if dir == 0:
                        ranges = r_sx
                    else:
                        ranges = r_dx

                tree.childs[dir] = child
            tree = tree.childs[dir]
       
        self.tree_updating(tree, element, full_attributes, attributes, ranges, depth - 1,
                class_attribute, class_att_pos)


    def build_train(self, forest, full_attributes, attributes, ranges, depth, training_data,\
            classification_attribute, classification_attribute_position):
        
        start0 = time.time()
        self.rdtForest = forest

        tmp = training_data.pop(0)
        while tmp != None: 
            try:
                start = time.time()

                #print "TUPLE ", tmp
                for i in xrange(forest.trees_n):
                    current_attributes = attributes[:]
                    current_ranges = ranges.copy()
                    if len(forest.trees) < forest.trees_n:
                        rdt = RandomDT(current_attributes, current_ranges)
                        self.tree_updating(rdt, tmp, full_attributes,
                                current_attributes, current_ranges, depth,\
                            classification_attribute, classification_attribute_position)
                        forest.trees.append(rdt)
                    else:
                        self.tree_updating(forest.trees[i], tmp, full_attributes, current_attributes, current_ranges, depth,\
                            classification_attribute, classification_attribute_position)

                #break
                #print tmp, " TRAINED IN ", time.time() - start
                tmp = training_data.pop(0) 
            except IndexError:
                tmp = None
        
        #print forest.visit_tree(forest.trees[0],'','root')
        print "FOREST TRAINED ======== ", time.time() - start0



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
        random.seed(time.time())

        self.training = tr_arff
        self.outgoing = out_arff
        self.full_attributes = attrs
        self.attributes, self.ignore_att_pos, self.class_att_pos = self.purify(attrs, cl_attr, ign_attr)
        self.class_attribute = cl_attr
        self.ignore_attribute = ign_attr
        self.data = []   
        self.rdtForest = None
        self.trees_n = trees_n

    def retrieve_range(self):
        """
            This procedure acquire the range of each attribute in the training dataset and
            collect data into the memory
            If data presents "?" it is ignored
        """
        import copy
        self.elements = []
        second = copy.deepcopy(self.training)
        start = time.time()

        import sys
        range = dict()
        temp = self.training.get_next()
        dim = len(temp)

        while temp != None:
            for i in xrange(dim):
                if (i not in self.ignore_att_pos):# and (temp[i] != "?"):
                    attr = self.full_attributes[i][0]
                    # If attribute is not in list, then add it
                    if (not range.__contains__(attr)):
                        range.__setitem__(attr, [])
            
                    if (self.full_attributes[i][1] == "string"):
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
            self.data.append(temp)
            temp = self.training.get_next()

        print "RETRIEVE RANGES ", time.time() - start

        start = time.time()

        temp = second.get_next()
        while temp != None:
            temp = second.get_next()
            self.elements.append(temp)

        print "JUST SCANNING ", time.time() - start

        start = time.time()
        temp = self.data.pop(0)
        while temp != None:
            try:
                temp = self.data.pop(0)
            except IndexError:
                temp = None
        print "RAM ", time.time() - start

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
                ignore_list.append( class_att_pos )
        ignore_list.sort()
        holy_list.reverse()
        return holy_list, ignore_list, class_att_pos

    def calculate_dimension(self):
        return int(math.pow(len(self.attributes), 2)), int(math.pow(2, len(self.attributes) - 1)), []

    def train(self):
        """
            Given the RDT's Forest generated, the dataset in Main Memory, and
            the list of attributes, train all the RDTs contained in the Forest
            with the data
        """
        # Once the retrieve_range is called, data are in main memory.

        #start = time.time()
        #self.data.sort

        self.rdtForest = Forest(self.trees_n, self.attributes, self.retrieve_range())
        #self.rdtForest.populate()

        trainer = Trainer()
        attributes = self.attributes[:]
        #attributes.insert(self.class_att_pos, self.full_attributes[self.class_att_pos][0])
        trainer.build_train(self.rdtForest, self.full_attributes, attributes, self.rdtForest.ranges.copy(),\
                self.rdtForest.tree_depth, self.data, self.class_attribute,
                self.class_att_pos)
        #trainer.train(self.data)
        #trainer.train(self.rdtForest, self.data, self.full_attributes, self.ignore_att_pos, self.class_att_pos)
        
        return self.calculate_dimension()
    
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
        #print "\nPREDICTIONS: ",predictions, "\nPREDICTED", max
        return max 

    def classify_tuple(self, tuple, attributes):
        """
            Given a tuple, the function retrieve the classification
            probability coming from each Tree in the Forest, scanning all the
            tuple attributes, ignoring the ones not present in the tree
        """
        sum = dict()
        total = 0
        #start = time.time()
        for i in xrange(len(self.rdtForest.trees)):
            #start1 = time.time()
            prediction =  self.rdtForest.trees[i].get_probability(tuple,\
                attributes)
            #print "TUPLE TREE CLASSIFICATION TIME, ", time.time() - start1
            
            if prediction == None:
       #         print "UNKNOWN"
                return "UNKNOWN"
            #try:
            for class_label in prediction:
                if (not sum.__contains__(class_label)):
                    sum.__setitem__(class_label, 0)
                sum[class_label] += prediction[class_label]
                total += prediction[class_label]
            #except TypeError:
            #    print "TUPLE", tuple, prediction
            #    return None
        
        for i in sum:
            sum[i] = sum[i]/len(self.rdtForest.trees)
        if sum == {}:
        #    print "SUMM IS UNKNOWN, but PREDICTION is ", prediction
            return "UNKNOWN"
        #print "TUPLE CLASSIFICATION TIME ", time.time() - start
        return self.loss_function(sum)

    def classify(self, file):
        """
            Given a set of tuples, peform the classification according with
            the rdtForest train. Each tuple is enriched by the predict label
            using the trained model. The new tuple is then written in the
            output file.
            file        the dataset to classify, in arff format
        """
        #print "\nATTRIBUTES ", self.full_attributes
        #print "==================================="
        #print "\nRANGES ", self.rdtForest.ranges
        #print "==================================="
        #print self.rdtForest.visit_tree(self.rdtForest.trees[0],'','root')
        unknown = 0
        total = 0
        
        attributes = file.get_attributes()
        attributes.append([str(self.class_attribute)+'_label',\
                self.full_attributes[self.class_att_pos][1]])
        self.outgoing.write_headers(attributes)

        tmp = file.get_next()
        while tmp != None:
            prediction = self.classify_tuple(tmp, attributes)
            
            tmp.append(prediction)
            self.outgoing.write_data(tmp)
            tmp = file.get_next()

            #if prediction == "UNKNOWN":
            #    unknown += 1
            #total += 1

        #print "\n\nTOTAL, ",total," of which UNKNOWN are ", unknown
        self.outgoing.store_buffer()
