from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

import qt

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

#if 'lockin' not in instlist:
lockin = qt.instruments.create('lockin', 'ZI_HF_2LI')
