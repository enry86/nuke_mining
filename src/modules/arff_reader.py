#!/usr/bin/env python

class FileException(Exception): pass

class ArffReader:
    """
    This class provides support for retrieving data from a .arff
    file
    """
    
    def __init__(self,filename):
        """
        Constructor, takes the path to the arff file to process
        """
        self.filename = filename
        self.att_list = None
        self.start_data = 0
        self.buffer = []
        self.buffer_dim = 100

    def get_attributes(self):
        """
        Retrieves from the file header the atributes specification,
        returns it as a list of lists
        """
        if self.att_list != None:
            return self.att_list
        else:
            res = []    
            file = open(self.filename,'r')
            line = file.readline()
            while line.count('@DATA') == 0 and line != '':
                if line.count('@ATTRIBUTE') != 0:
                    attr = line.split()[1:]
                    res.append(attr)
                line = file.readline()
            self.start_data = file.tell()
            self.last_read = self.start_data
            file.close()
            self.att_list = res
            if self.start_data == 0 or len(self.att_list) == 0:
                raise FileException
            return res

    def fill_buffer(self):
        """
        reads self.bufferDim lines of the file and stores it into
        self.buffer
        """
        file = open(self.filename,'r')
        if file == None:
            raise FileException
        count_lines = 0
        file.seek(self.last_read)
        line = file.readline()
        while line != '' and count_lines < self.buffer_dim:
            line = line.strip()
            self.buffer.append(line.replace(' ',''))
            line = file.readline()
            count_lines += 1
        self.last_read = file.tell() - len(line)
        file.close()
        return count_lines

    def get_next(self):
        """
        reads and returns the next tuple in the buffer
        """
        if self.start_data == 0:
            self.get_attributes()
            self.last_read = self.start_data
        if len(self.buffer) == 0:
            if self.fill_buffer() == 0:
                return None
        last = self.buffer.pop(0)
        last_sp = last.split(',')
        if last_sp[-1] == '':
            return last_sp[:-1]
        else:
            return last_sp
    

