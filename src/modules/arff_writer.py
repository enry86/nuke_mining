#!/usr/bin/env python


class ArffWriter:
    """
    This class contains all the functions used for writing data in a .arff
    file
    """

    def __init__(self, filename, relation):
        self.file = filename
        self.relation = relation
        self.buffer = []
        self.buf_size = 100

    def write_headers(self, attrs):
        """
        This function writes the header of the file containing the
        specificaion of the fields
        """

        file = open(self.file,'w')
        file.write('@RELATION '+self.relation+'\n')
        for a in attrs:
            file.write('@ATTRIBUTE ')
            for str in a:
                file.write(str+' ')
            file.write('\n')
        file.write('\n'+'@DATA'+'\n')
        file.close()
     
    def write_data(self,datapoint):
        """
        Writes the data in a temp buffer, when it's full the buffer is
        stored on file
        """
        self.buffer.append(datapoint)
        if len(self.buffer) >= self.buf_size:
            self.store_buffer()
        

    def store_buffer(self):
        """
        This function stores the content of the buffer in a file on disk
        """
        file = open(self.file,'a')
        while len(self.buffer) > 0:
            dp = self.buffer.pop(0)
            if dp == None:
                print len(self.buffer)
            for s in dp:
                file.write(s+',')
            file.write('\n')
        file.close()
