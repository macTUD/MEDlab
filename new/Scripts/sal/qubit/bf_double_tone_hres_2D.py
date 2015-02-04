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

#2nd coordinate SWEEP PROBE FREQ
#start_probe_f = 4000

#stop_probe_f = 9000
start_probe_f=3500
stop_probe_f=9500
#probe_points = 1000
probe_points=24001

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

#fsv_bandwidth = 40*kHz     #MHz
fsv_bandwidth = 30*kHz     #MHz
#fsv_bandwidth=10
fsv_source_power =0


fsv.set_resolution_bandwidth(fsv_bandwidth)
fsv.set_start_frequency(start_frequency)
fsv.set_stop_frequency(stop_frequency)

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


#SGS instrument variables

sgs_power = 0



#fsv.set_trace_continuous(False)


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
data.add_coordinate('Probe Frequency (MHz)')
#data.add_coordinate('Magnet Voltage (V)')
data.add_value('transmission (dBm)')

data.create_file(file)
data.copy_file('bf_double_tone_hres_2D.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy


#########################################
#           MANUAL INSTRUMENT INIT
#########################################

print 'Init instruments'

#while (x_time < max_runtime or  and run_index<norm_runs):

#INIT ADWIN
#print 'Set magnet to starting point and wait several seconds'
#print 'Set magnet to zero and wait till it settles'
#adwin.set_DAC_2(magvlist[0])


#adwin_DAC initialization
##adwin.start_process()       #starts the DAC program
##adwin.set_DAC_2(0)

#INIT SGS
sgs.set_RF_frequency(1000)
sgs.set_RF_state(True)
sgs.set_RF_power(sgs_power)

qt.msleep(10)



########################################
###         MEASUREMENT LOOP
########################################

print 'Start Experiment'

def display_time(time):
    hours = time/3600
    minutes = (time-3600*floor(hours))/60
    seconds = (time-3600*floor(hours)-60*floor(minutes))

    return hours, ':', minutes, ':', seconds
    

#variables
run_index=0
tstart = time()

prev_time=tstart
now_time=0
exp_number = len(probe_list)

for probe in probe_list:
#    sgs.set_RF_state(False)
    #print probe
    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60
    
    print probe, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
  
    #Set Voltage
#    adwin.set_DAC_2(magv)
    sgs.set_RF_frequency(probe)
#    print probe, sgs.get_RF_frequency()
    #let it settle        
    qt.msleep(.1)

    trace = fsv.get_trace()
    data.add_data_point(flist, list(probe*ones(len(flist))),trace)

    data.new_block()
    spyview_process(data,start_frequency,stop_frequency,probe)
  
    qt.msleep(0.01) #wait 10 usec so save etc
    

data.close_file()
##adwin.set_DAC_2(0)
qt.mend()
#end of experiment routine

print 'ready at', localtime()[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
