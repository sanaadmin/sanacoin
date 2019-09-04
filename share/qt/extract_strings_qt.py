#!/usr/bin/python
'''
Extract _("...") strings for translation and convert to Qt stringdefs so that
they can be picked up by Qt linguist.
'''
from __future__ import division,print_function,unicode_literals
from subprocess import Popen, PIPE
import glob
import operator
import os
import sys

OUT_CPP="qt/sanacoinstrings.cpp"
EMPTY=['""']

def parse_po(text):
    """
    Parse 'po' format produced by xgettext.
    Return a list of (msgid,msgstr) tuples.
    """
    messages = []
    msgid = []
    msgstr = []
    in_msgid = False
    in_msgstr = False

    for line in text.split('\n'):
        line = line.rstrip('\r')
        if line.startswith('msgid '):
            if in_msgstr:
                messages.append((msgid, msgstr))
                in_msgstr = False
            # message start
            in_msgid = True

            msgid = [line[6:]]
        elif line.startswith('msgstr '):
            in_msgid = False
            in_msgstr = True
            msgstr = [line[7:]]
        elif line.startswith('"'):
            if in_msgid:
                msgid.append(line)
            if in_msgstr:
                msgstr.append(line)

    if in_msgstr:
        messages.append((msgid, msgstr))

    return messages

files = sys.argv[1:]

# xgettext -n --keyword=_ $FILES
XGETTEXT=os.getenv('XGETTEXT', 'xgettext')
if not XGETTEXT:
    print('Cannot extract strings: xgettext utility is not installed or not configured.',file=sys.stderr)
    print('Please install package "gettext" and re-run \'./configure\'.',file=sys.stderr)
    exit(1)
child = Popen([XGETTEXT,'--output=-','-n','--keyword=_'] + files, stdout=PIPE)
(out, err) = child.communicate()

messages = parse_po(out.decode('utf-8'))

f = open(OUT_CPP, 'w')
f.write("""

#include <QtGlobal>

// Automatically generated by extract_strings.py
#ifdef __GNUC__
#define UNUSED __attribute__((unused))
#else
#define UNUSED
#endif
""")
f.write('static const char UNUSED *sanacoin_strings[] = {\n')
messages.sort(key=operator.itemgetter(0))
for (msgid, msgstr) in messages:
    if msgid != EMPTY:
        f.write('QT_TRANSLATE_NOOP("sanacoin-core", %s),\n' % ('\n'.join(msgid)))
f.write('};\n')
f.close()
