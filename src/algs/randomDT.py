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


class Forest:
    """
        This class contains the Forest build up of Random Decision Tree.
        The main parameters are the number of random tree to generate, that
        are at least 30 (for achieve a good accuracy) and the tree's depth
        that is 0 as default since the attributes are required.
        The trees list contain the root nodes of the Forest
    """
    
    def __init__(self, trees_n, attributes, range, dimension):
        """
            This is the constructor of the forest of RDTs. Default dimension
            is 30 as suggested in order to obtain a good estimate with low
            variance.
            trees_n     is the number of tree to construct
            attributes  are the dataset's attributes without both the ignoring
                        ones and the classification one
            range       is the range of the continuous dataset's attributes
        """
        if trees_n == 0:
            self.trees_n = self.best_forest(len(attributes) + 1, dimension)
        else:
            self.trees_n = trees_n
        print "Trees  = ", self.trees_n
        self.trees = []
        # Adding one to include the classifying attribute, not in attributes
        # for simplicity
        if ( len(attributes) > 10 ):
            self.tree_depth = (len(attributes) + 1 ) / 2
        else:
            self.tree_depth = len(attributes) + 1 
        print "Tree depth = ", self.tree_depth
        self.attributes = attributes
        self.ranges = range

    def best_forest(self, k, dataset_dimension):
        """
            Calculate the best number of trees to generate accordingly with
            the attrbutes given
            Supposition: The Dataset is not skewed
        """
        if dataset_dimension < 2000:
            confidence_lower_bound =  0.99
        else:
            confidence_lower_bound = 0.7
        base = 1 - float(1)/float(k)
        return int(math.log((1 - confidence_lower_bound), base))

    def visit_tree(self, tree, space, pos, show):
        """
            Only for testing propouse. It represents the tree
        """
        # If the node is None, it doesn't exist
        if tree == None:
            return 0, 0

        if show:
            # If the element has type string, then print the childs name
            if tree.label[1] == "string":
                trh = ""
                if (tree.childs != []) and (tree.childs != None):
                    for i in xrange(len(tree.childs)):
                        if tree.childs[i] == None:
                            trh = trh + " ,"
                        else:
                            trh = trh + tree.threshold[i] + ","
            else: 
                trh = str(tree.threshold)

            # Print the attribute, its position, the threshold and the number of
            # training examples through it
            print space + tree.label[0] +' ('+pos+')'+'   '+trh+\
                    '                          '+str(tree.examples_n)
            
        if (tree.childs == None) or (tree.childs == []):
            return 1, 1
        j = 0
        sum = 0
        sum_l = 0
        for i in tree.childs:
            nodes, leaves = self.visit_tree(i,space + '   ',str(j), show)
            sum_l += leaves
            sum += nodes
            j += 1
        return sum + 1, sum_l


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

    def tree_updating(self, tree, element, full_attributes, attributes, ranges, depth,\
            class_attribute, class_att_pos):
        """
            This recursive procedure aims to build the tree little by little
            the tuples come to train the model
            tree        is the current position on the tree
            element     is the tuple used to train the model
            full_attributes
                        is the complete list of attributes
            attributes  is the list of attributes that can be chosen at the
                        current level
            ranges      is the list of possible value can be chosen at this
                        level
            class_attribute
                        is the attribute to classify
            class_att_pos
                        is the order of the classification attribute

        """
        # Update the number of examples wrt classification attribute
        if ( not tree.examples_n.__contains__(element[class_att_pos]) ):
            tree.examples_n.__setitem__(element[class_att_pos], 1)
        
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

            if ( tree.childs[position] == None ):
                if next_is_leaf:
                    child = RandomDT(full_attributes[class_att_pos], None)
                else:
                    child = RandomDT(attributes, ranges)
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

    def build_train(self, forest, full_attributes, ranges, depth, training_data,\
            classification_attribute, classification_attribute_position):
        """
            This procedure is charged to train all the RDT in the Forest,
            performing the update of the all Forest for each tuple retrieved.
        """
        tmp = training_data.pop(0)
        while tmp != None: 
            try:
                for i in xrange(forest.trees_n):
                    current_attributes = forest.attributes[:]
                    current_ranges = ranges.copy()

                    # At first time the tree doesn't exist, so is necessary to
                    # generate it
                    if len(forest.trees) < forest.trees_n:
                        rdt = RandomDT(current_attributes, current_ranges)
                        self.tree_updating(rdt, tmp, full_attributes, current_attributes, current_ranges, depth,\
                            classification_attribute, classification_attribute_position)
                        forest.trees.append(rdt)
                    else:
                        self.tree_updating(forest.trees[i], tmp, full_attributes, current_attributes, current_ranges, depth,\
                            classification_attribute, classification_attribute_position)
                
                tmp = training_data.pop(0) 
            except IndexError:
                tmp = None
        

class Classifier:
    def __init__(self, dataset, ranges, out_arff, attrs, cl_attr, ign_attr, trees_n):
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

        self.data = dataset
        self.full_attributes = attrs
        attributes, self.ignore_att_pos, self.class_att_pos = self.purify(attrs, cl_attr, ign_attr)
        self.class_attribute = cl_attr
        self.ignore_attribute = ign_attr
        self.trees_n = trees_n
        self.rdtForest = Forest(self.trees_n, attributes, ranges, len(self.data))
        self.outgoing = out_arff

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

        holy_list.reverse()
        return holy_list, ignore_list, class_att_pos

    def train(self):
        """
            Given the RDT's Forest generated, the dataset in Main Memory, and
            the list of attributes, train all the RDTs contained in the Forest
            with the data
        """
        trainer = Trainer()
        trainer.build_train(self.rdtForest, self.full_attributes, self.rdtForest.ranges.copy(),\
                self.rdtForest.tree_depth, self.data, self.class_attribute, self.class_att_pos)

    def count_nodes(self):
        """
            This function is charged to count the number of node and leaves in
            the tree
        """
        self.random_tree = random.randrange(self.rdtForest.trees_n)
        nodes, leaves =  self.rdtForest.visit_tree(self.rdtForest.trees[self.random_tree],'','root',0)
        return nodes, leaves

    def loss_function(self, predictions):
        """
            This is the function that is charged to do the prediction once the
            probabilities of classes are given.
            It returns the best one. At moment i 0-1 function
            predictions     dictionary  'Class_label'='Probability'
        """
        max = predictions.keys()[0]
        for class_attribute in predictions:
            if predictions[class_attribute] > predictions[max]:
                max = class_attribute
        return max

    def get_probabilities(self, predictions):
        """
            Calculate the probability of each element coming from the forest
            predictions         list of dictionaries
                                [['Class1':n],['Class2':m],...]
        """
        probabilities = []
        # Calculate Class Probability for each tree
        for prediction in predictions:
            if ( prediction == "UNKNOWN"):
                # If the prediction is UNKNOW, maybe others are values
                predictions.remove(prediction)
            else:
                total = 0
                class_probability = dict()
                for class_attribute in prediction:
                    total += prediction[class_attribute]

                for class_attribute in prediction:
                    elements_prob = float(prediction[class_attribute])/float(total)
                    class_probability.__setitem__(class_attribute, elements_prob)

                probabilities.append(class_probability)

        # Whenever the probabilities structure is empty, the element to
        # classify is not been recognized by any Tree
        if probabilities == []:
            return "UNKNOWN"

        # Calculate global Class Probability, for the entire Forest
        for prediction in probabilities:
            for class_attribute in prediction:
                if ( not probabilities[0].__contains__(class_attribute) ):
                    probabilities[0].__setitem__(class_attribute, 0)
                probabilities[0][class_attribute] += prediction[class_attribute]
        
        for class_attribute in probabilities[0]:
            probabilities[0][class_attribute] =\
                    probabilities[0][class_attribute] / self.rdtForest.trees_n 

        return probabilities[0]

    def classify_tuple(self, tuple, attributes):
        """
            Given a tuple, the function retrieve the classification
            probability coming from each Tree in the Forest, scanning all the
            tuple attributes, ignoring the ones not present in the tree
        """
        predictions = []
        total = 0

        # Consulting the Forest :) (The Ent Council)
        for i in xrange(len(self.rdtForest.trees)):
            prediction =  self.rdtForest.trees[i].get_probability(tuple,\
                attributes)

            # The tuple was not recognized by the model, in other cases the
            # prediction is stored as the tree order number
            if prediction == None:
                predictions.append("UNKNOWN")
            else:
                predictions.append(prediction)

        probabilities = self.get_probabilities(predictions)
        
        if probabilities == "UNKNOWN":
            return probabilities

        return self.loss_function(probabilities)

    def classify(self, file):
        """
            Given a set of tuples, peform the classification according with
            the rdtForest train. Each tuple is enriched by the predict label
            using the trained model. The new tuple is then written in the
            output file.
            file        the dataset to classify, in arff format
        """
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

        self.outgoing.store_buffer()

    def get_memory_node(self, node):
        '''
            visits the tree summing the memory occupied by each node
        '''
        # Label is a list build up of two strings
        memo = 32 + 32 + 32
        # Threshold may be a REAL if the type of the attribute is REAL (or
        # numeric) or it can be a list of strings indicating the
        # childs-connection's name
        if node.label[1] == "string":
            memo = memo + 32 + (32 * len(node.threshold))
        else:
            memo = memo + 64
        # Examples_n is a dictionary, it contains the Class Attribute name as
        # key and a integer that counts how many examples pass through it
        memo = memo + 32 + (32 * len(node.examples_n))
        # Childs
        if node.childs != None:
            for child_n in xrange(len(node.childs)):
                if ( node.childs[child_n] != None ):
                    memo = memo + 32 + self.get_memory_node(node.childs[child_n])
        return memo

    def get_memory(self):
        '''
            retrieves the total memory consumption for the tree and transform it into a string
        '''
        tot = self.get_memory_node(self.rdtForest.trees[self.random_tree]) / 8
        tot = tot * self.rdtForest.trees_n
        if tot >= 1000000:
            return str(tot) + ' Bytes ' + '(' + str(float(tot) / (1024 * 1024))  + ' MB ' + ' )'
        elif tot >= 1000:
            return str(tot) + ' Bytes ' + '( ' + str(float(tot) / 1024) + ' KB ' + ' )'
        else:
            return str(tot) + ' Bytes '
