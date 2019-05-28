#!/usr/bin/python3
# check python version is > 3.6

import subprocess as subproc
import sys

# FIXME: use an importable main function instead of a [BLEEP]ing subproc
args = ['python3', 'load.py'] + list(sys.argv[1:])
subproc.run(args)
