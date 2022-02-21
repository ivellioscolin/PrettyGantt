#!/usr/bin/env python
import sys, os
import PrettyGantt

def main():
    if ((len(sys.argv) >= 2) and (os.path.isfile(sys.argv[1]))):
        PrettyGantt.PlotGantt('ProgramAll', sys.argv[1])
    else:
        print('Need JSON')

if __name__== '__main__':
    main()