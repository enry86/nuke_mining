#!/usr/bin/env python

class FileException(Exception): pass

class ArffReader:
    def __init__(self, filename):
        self.filename=filename
        self.attList= None
        self.startData=0
        self.buffer=[]
        self.bufferDim=100

    def getAttributes(self):
        if self.attList != None:
            return self.attList
        else:
            res=[]    
            file=open(self.filename,'r')
            if file == None:
                raise FileException
            line=file.readline()
            while line.count('@DATA') == 0:
                if line.count('@ATTRIBUTE') != 0:
                    attr=line.split()[1:]
                    res.append(attr)
                line=file.readline()
            self.startData=file.tell()
            file.close()
            self.attList=res
            return res

    def fillBuffer(self):
        file=open(self.filename,'r')
        if file == None:
            raise FileException
        countLines=0
        file.seek(self.lastRead)
        line=file.readline()
        while line != '' and countLines<self.bufferDim:
            self.buffer.append(line.strip())
            line=file.readline()
            countLines+=1
        self.lastRead=file.tell()-len(line)
        file.close()
        return countLines

    def getNext(self):
        if self.startData==0:
            self.getAttributes()
            self.lastRead=self.startData
        if len(self.buffer)==0:
            if self.fillBuffer() == 0:
                return None
        last = self.buffer.pop(0)
        return last.split(',')
    
if __name__=='__main__':
    arff=ArffReader('/home/enry/progetti/nuke_mining/dataset/training_st.arff')
    a=arff.getNext()
    while a != None:
        print a[0]+','+a[1]
        a=arff.getNext()
