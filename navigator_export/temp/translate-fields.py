# -*- coding: utf-8 -*-
import sys
f = open(sys.argv[1])
f1 = open('temp.txt', 'w')
for f in f.xreadlines():
    #print repr(f)
    line = unicode(f, 'cp850')
    #print line
    s = line.split('\x00\x00\x01')
    for a in s:
        st = ''
        #print repr(a)
        for x in a.strip():
            if x.isalpha() and ord(x) > 48 or x in '()%/-.+ ' or x.isnumeric():
                st += x
        if st:
            f1.write(st.encode('utf8') + '\n')
            print repr(st.encode('utf8'))
        #print a
