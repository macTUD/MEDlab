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
execfile('metagen.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec

##rf_power = 0
###norm_runs = 40
##exp_runs=1


start_frequency= 5310
stop_frequency= 5410
f_points =1001

#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),f_points)


start_voltage = 0
stop_voltage = 9.8
v_points = 100

vlist=np.linspace(float(start_voltage),float(stop_voltage),v_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#if 'fsl' not in instlist:
#    fsl= qt.instruments.create('fsl','RS_FSL',address='TCPIP::192.168.100.21::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#if 'smb' not in instlist:
#    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.100.25::INSTR')

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


#SMB 100A instrument
#smb.reset()
#smb.set_RF_power(rf_power)
#smb.set_RF_frequency(start_frequency)
#smb.set_RF_state(True)

#FSL18 instrument variables
##kHz=0.001
##fsl_bandwidth = .001     #MHz
##fsl_span = .1*kHz           #MHz
##fsl_sweep_points =101
##
##def fsl_start(f_center,span):
##    return float(f_center-span/2)
##
##def fsl_stop(f_center, span):
##    return float(f_center+span/2)
##
##fsl.reset()
##fsl.set_resolution_bandwidth(fsl_bandwidth)
##fsl.set_tracking(False)
##fsl.set_sweeppoints(fsl_sweep_points)
##fsl.get_all() #get all the settings and store it in the settingsfile
##fsl.set_trace_continuous(False)  

#adwin_DAC initialization

adwin.start_process()       #starts the DAC program


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_value('time (ms)')
data.add_coordinate('Magnet Voltage (V)')

data.create_file()
data.copy_file('bf_single_tone.py')

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
for v in vlist:

    x_time = time()

    #adwin.set_DAC_2(v)
    data.add_data_point(x_time-tstart,0)
    print 'point', 0

    qt.msleep(0.1)

##    #Take trace
##    trace_index=0
##    trace=[]
##    while(trace_index<sweep_points):
##
##        smb.set_RF_frequency(flist[trace_index])
##        fsl.set_start_frequency(fsl_start(flist[trace_index],fsl_span))
##        fsl.set_stop_frequency(fsl_stop(flist[trace_index],fsl_span))
##
##        #sleep(1)
##            
##        trace.append(fsl.get_trace()[51])        
##
##        print run_index, trace_index, trace[trace_index], smb.get_RF_frequency()
##
##        trace_index += 1
##    now=time()
##    time_list = now*ones(len(trace))
##    
##    data.new_block()
##    data.add_data_point(flist,time_list,trace) #store data
#    spyview_process(data,start_frequency,stop_frequency,x_time) 
    spyview_process(data,start_voltage,stop_voltage,x_time)
    qt.msleep(0.01) #wait 10 usec so save etc

##    run_index=run_index+1
##    print run_index, x_time

data.close_file()
qt.mend()
#end of experiment routine

