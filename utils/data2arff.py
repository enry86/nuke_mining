#!/usr/bin/python
# Utility to convert dataset file in arff format

import sys
import os

if len(sys.argv)!=3:
        print 'Usage data2arff <input file> <output file>'
        sys.exit()
inp=open(sys.argv[1],'r')
out=open(sys.argv[2],'w')
attline=inp.readline()
attrs=attline.split()
out.write('% Xenon concentration dataset\n')
out.write('@RELATION xenon\n\n')
for a in attrs:
        if a=='Index':
                type='string'
        elif a=='B/E':
                type='string'
        else:
                type='numeric'
        out.write('@ATTRIBUTE '+a+' '+type+'\n')
out.write('\n@DATA\n')
line=inp.readline()
while line!='':
        data=line.split()
        for d in data:
                out.write(d+',')
        out.write('\n')
        line=inp.readline()
inp.close()
out.close()




