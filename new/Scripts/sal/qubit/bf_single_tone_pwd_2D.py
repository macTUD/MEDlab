################################
#       DESCRIBTION
################################

#Measurement script that does single tone qubit spectroscopy changing the input power 

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
execfile('metagen2D.py')




################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV',address='TCPIP::192.168.1.101::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

##if 'adwin_DAC' not in instlist:
##    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS3_minitransmon')
med.set_setup('BF')
med.set_user('Sal')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')

#some global variables
kHz=0.001

################################
#     EXPERIMENT VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec

#1st coordinate    SWEEP AROUND CAVITY FREQ
start_frequency= 3587
stop_frequency= 3590
f_points =101

##
###2nd coordinate
start_power =0
stop_power = -80
power_points = 81
##
power_list=np.linspace(float(start_power),float(stop_power),power_points)





#########################################
#            INSTRUMENTS VARIABLES
#########################################


#This script assumes that the signal analyser is already setup with the SMB100A tracking generator (TTL mode)
#Also this script assumes all the REF's 10MHz are well set up


#FSV instrument variables

#fsv_bandwidth = 40*kHz     #MHz
fsv_bandwidth = 30*kHz     #MHz
#fsv_bandwidth=10
fsv_source_power =0

fsv.set_resolution_bandwidth(fsv_bandwidth)
fsv.set_start_frequency(start_frequency)
fsv.set_stop_frequency(stop_frequency)
fsv.set_trace_continuous(False)

#start_frequency = 2000
#stop_frequency=5000

####################### JUNK THIS IS, CHANGE LATER ################################
sweeppoints = 201
fsv.set_sweeppoints(sweeppoints)

sweep_runs = 1
trace_len=fsv.get_sweeppoints()
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_runs*trace_len)
sweeplist=np.linspace(start_frequency,stop_frequency,sweep_runs)

f_points=sweep_runs*sweeppoints
fsv.set_sweeppoints(f_points)
######################################################################################


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone_2D'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Power (dBm)')
#data.add_coordinate('Magnet Voltage (V)')
data.add_value('transmission (dBm)')

data.create_file(file)
data.copy_file('bf_single_tone_pwd_2D.py')


#########################################
#           MANUAL INSTRUMENT INIT
#########################################


########################################
###         MEASUREMENT LOOP
########################################

print 'Start Experiment'

for power in power_list:

    print power

    fsv.set_source_power(power)
    qt.msleep(.1)

    trace = fsv.get_trace()
    data.add_data_point(flist, list(power*ones(len(flist))),trace)

    data.new_block()
    spyview_process(data,start_frequency,stop_frequency,power)
  
    qt.msleep(0.01) #wait 10 usec so save etc

data.close_file()
qt.mend()
#end of experiment routine

