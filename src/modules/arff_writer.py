class ArffWriter:
    def __init__(self, filename, relation):
        self.file = filename
        self.relation = relation
        self.buffer = []
        self.buf_size = 100

    def write_headers(self, attrs):
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
        self.buffer.append(datapoint)
        if len(self.buffer) >= self.buf_size:
            self.store_buffer()
        

    def store_buffer(self):
        file = open(self.file,'a')
        while len(self.buffer) > 0:
            dp = self.buffer.pop(0)
            for s in dp:
                file.write(s+',')
            file.write('\n')
        file.close()
