
# -*- coding: utf-8 -*-
import sys

f0 = open(sys.argv[1])
#f1 = open('/tradehouse/navi/navi/t', 'w')
f1 = open('temp-report.txt', 'w')
#f1 = open('t', 'w')
#f1.write(unicode('genDESTINATION(\'/tradehouse/test.txt\', FALSE);\n', 'cp850'))
#f1.write(unicode('genDESTINATION(\'/Users/mikko/Desktop/test.txt\', FALSE);\n', 'cp850'))
line = 1
for f in f0.xreadlines():
    out = 'genXYWRITE({},{},{},FORMAT("{}") + \':\');'.format(line , 1,100, f.strip())
    out = unicode(out, 'utf8')
    f1.write(out.encode('cp850') + '\n')
    line += 1

out = 'genXYWRITE({},1,80,  \'::\');'.format(line)
out = unicode(out, 'utf8')
f1.write(out.encode('cp850') + '\n')

f0.close()
f1.close()
    ##print line
    #s = line.split('\x00\x00\x01')
    #for a in s:
        #st = ''
        ##print repr(a)
        #for x in a.strip():
            #if x.isalpha() and ord(x) > 48 or x in '()%/. ' or x.isnumeric():
                #st += x
        #if st:
            #f1.write(st.encode('utf8') + '\n')
            #print repr(st.encode('utf8'))
        ##print a
