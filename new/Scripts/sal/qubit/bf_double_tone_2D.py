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
execfile('metagen2D.py')




################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV',address='TCPIP::192.168.1.101::INSTR')

if 'sgs' not in instlist:
    sgs = qt.instruments.create('sgs','RS_SGS100A', address='TCPIP::192.168.1.102::INSTR')

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


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_double_tone_2D'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Probe Frequency (MHz)')
#data.add_coordinate('Magnet Voltage (V)')
data.add_value('transmission (dBm)')

data.create_file(file)
data.copy_file('bf_double_tone_hres_2D.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy




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
#start_frequency= 3585
#stop_frequency= 3595
start_frequency = 3000
stop_frequency=4000
f_points=1001

flist=np.linspace(float(start_frequency),float(stop_frequency),f_points)
##f_points =101

#2nd coordinate SWEEP PROBE FREQ
#start_probe_f=2000
#stop_probe_f=8000
start_probe_f=3000
stop_probe_f=4000
probe_points=100

probe_list=np.linspace(float(start_probe_f),float(stop_probe_f),probe_points)


##
###2nd coordinate
start_magvoltage =0
stop_magvoltage = 1.3
magv_points = 0
##
##magvlist=np.linspace(float(start_magvoltage),float(stop_magvoltage),magv_points)


#########################################
#            INSTRUMENTS VARIABLES
#########################################


#This script assumes that the signal analyser is already setup with the SMB100A tracking generator (TTL mode)
#Also this script assumes all the REF's 10MHz are well set up


#FSV instrument variables

#fsv_bandwidth = 50*kHz     #MHz
fsv_bandwidth = 20*kHz     #MHz
#fsv_bandwidth=10
fsv_source_power =-20


fsv.set_sweeppoints(f_points)
fsv.set_resolution_bandwidth(fsv_bandwidth)
fsv.set_start_frequency(start_frequency)
fsv.set_stop_frequency(stop_frequency)
fsv.set_trace_continuous(False)

#SGS instrument variables

sgs_power = -20


#INIT ADWIN
#print 'Set magnet to starting point and wait several seconds'
#print 'Set magnet to zero and wait till it settles'
#adwin.set_DAC_2(magvlist[0])

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program
adwin.set_DAC_2(0)

#INIT SGS
sgs.set_RF_frequency(1000)
sgs.set_RF_state(True)

#qt.msleep(10)



########################################
###         MEASUREMENT LOOP
########################################

print 'Start Experiment'


#variables
run_index=0
tstart = time()

x_time = 0
y_temp =0
measurement_time=0


for probe in probe_list:
    print probe
    #Set Voltage
    sgs.set_RF_frequency(probe)

    qt.msleep(.1)

    trace = fsv.get_trace()
    data.add_data_point(flist, list(probe*ones(len(flist))),trace)

    data.new_block()
    spyview_process(data,start_frequency,stop_frequency,probe)
    qt.msleep(0.01) #wait 10 usec so save etc

data.close_file()
adwin.set_DAC_2(0)
qt.mend()
#end of experiment routine

