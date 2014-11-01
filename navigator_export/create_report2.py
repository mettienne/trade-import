
# -*- coding: utf-8 -*-
import sys

f0 = open(sys.argv[1])
f1 = open(sys.argv[2], 'w')
line = 1
for f in f0:
    out = 'genXYWRITE({},{},{},FORMAT("{}") + \':\');'.format(line,
                                                              1,
                                                              100,
                                                              f.strip())
    out = unicode(out, 'utf8')
    f1.write(out.encode('cp850') + '\n')
    line += 1

out = 'genXYWRITE({},1,80,  \'::\');'.format(line)
out = unicode(out, 'utf8')
f1.write(out.encode('cp850') + '\n')

f0.close()
f1.close()
