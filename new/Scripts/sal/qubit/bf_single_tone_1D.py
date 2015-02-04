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

start_frequency= 5310
stop_frequency= 5410
f_points =1001

#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),f_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsl','RS_FSV',address='TCPIP::192.168.1.101::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

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
fsv_bandwidth = 1     #MHz

fsv_source_power =-20


fsv.set_resolution_bandwidth(fsv_bandwidth)
fsv.set_sweeppoints(f_points)
fsv.set_start_frequency(start_frequency)
fsv.set_stop_frequency(stop_frequency)
fsv.set_sweeppoints(f_points)
fsv.set_trace_continuous(False)

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone_1D'
data = qt.Data(name=filename)

data.add_coordinate('Frequency (MHz)')
data.add_value('transmission (dBm)')


data.create_file()
data.copy_file('bf_single_tone_1D.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy


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

#while (x_time < max_runtime or  and run_index<norm_runs):


    
trace=fsv.get_trace()
data.add_data_point(flist,trace)

spyview_process(data,start_frequency,stop_frequency)
qt.msleep(0.01) #wait 10 usec so save etc

data.close_file()
qt.mend()
#end of experiment routine

