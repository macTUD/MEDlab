################################
#       DESCRIBTION
################################

#Measurement script that does single tone qubit spectroscopy using the ADwin
#as a DAC to either sweep magnetic field of gate voltage.


################################
#       DEVELOPMENT NOTES/LOG
################################


#transform into virtual spectrum analyser module




################################
#      IMPORTS
################################

import qt
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen1D.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec

start_freq= 3e9
stop_freq= 5e9
f_points =2001

#Dependent Variables
flist=np.linspace(float(start_freq),float(stop_freq),f_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS3_minitransmon')
med.set_setup('BF')
med.set_user('Sal')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')



#FSV instrument variables
#This script assumes that the signal analyser is already setup with the SMB100A tracking generator
kHz=0.001
bandwidth = 1e6     #MHz
power=-30

pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq)
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
sweeptime = pna.get_sweeptime()+.1
pna.sweep()
qt.msleep(sweeptime)

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone_PNA_1D'
data = qt.Data(name=filename)

data.add_coordinate('Frequency (MHz)')
data.add_value('Magnitude transmission (dBm)')
data.add_value('Phase transmission')

data.create_file()
data.copy_file('bf_single_tone_PNA_1D.py')


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()

x_time = 0
y_temp =0
measurement_time=0

print 'Start Experiment'


pna.sweep()
qt.msleep(sweeptime+.1)
trace=pna.fetch_data(polar=True)
data.add_data_point(flist,trace[0],trace[1])

spyview_process(data,start_freq,stop_freq)
qt.msleep(0.01) #wait 10 usec so save etc

data.close_file()
qt.mend()
#end of experiment routine

