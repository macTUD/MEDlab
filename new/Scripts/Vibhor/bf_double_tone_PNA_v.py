################################
#       DESCRIBTION
################################

#Measurement script that does double tone qubit spectroscopy using the PNA and the ADwin
#as a DAC to either sweep magnetic field of gate voltage. The external source can be either
#the SGS or SMB


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

#if 'fsv' not in instlist:
#    fsv = qt.instruments.create('fsv','RS_FSV',address='TCPIP::192.168.1.101::INSTR')

##if 'sgs' not in instlist:
##    sgs = qt.instruments.create('sgs','RS_SGS100A', address='TCPIP::192.168.1.102::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.1.50::INSTR')

##if 'adwin_DAC' not in instlist:
##    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('W6_NG')
med.set_setup('BF')
med.set_user('Vibhor')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')

#some global variables
kHz=0.001

################################
#     EXPERIMENT VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables

cw_frequency = 5.88e9 #this is the center of the cavity resonance
delta = .1e6 #this is the detuning we want to set the PNA Receiver to.

#stop_probe_f = 9000
span=100e6
start_probe_f=cw_frequency-float(span/2)
stop_probe_f=cw_frequency+float(span/2)
sweep_points = 2001
#sweep_t = 200 #sweeptime in seconds that the PNA sweeps.

probe_list=np.linspace(float(start_probe_f),float(stop_probe_f),sweep_points)


##
###2nd coordinate
start_power = 20
stop_power = -30
power_points = 5
##
powerlist=np.linspace(float(start_power),float(stop_power),power_points)


#########################################
#            INSTRUMENTS VARIABLES
#########################################


#PNA instrument variables

bandwidth = 1e6


######################################################################################



################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_double_tone_PNA_v'
data = qt.Data(name=filename)
data.add_coordinate('Sweeptime (s)')
#data.add_coordinate('Probe Frequency (MHz)')
data.add_coordinate('PNA power (dBm@PNA)')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')


data.create_file(file)
data.copy_file('bf_double_tone_PNA_v.py')


#########################################
#           MANUAL INSTRUMENT INIT
#########################################

print 'Init instruments'


#INIT ADWIN

#adwin_DAC initialization
#adwin.start_process()       #starts the DAC program
#adwin.set_DAC_2(0)

#INIT SMB
#smb.set_RF_frequency(float(cw_frequency/1e6))
#smb.set_RF_power(cav_source_power)
#smb.set_RF_state(True)

pna.reset()
pna.setup()

#receiver_freq=cw_frequency-delta

pna.setup_2tone_spectroscopy(cw_freq=cw_frequency, start_freq=start_probe_f,
                             stop_freq=stop_probe_f)

pna.set_power(0)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
sweeptime = pna.get_sweeptime()*1.01

#pna.sweep()
#qt.msleep(300)




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

for mag_v in magvlist:
#    sgs.set_RF_state(False)
    #print probe

    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60
    
    print mag_v, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
  
    #Set Voltage
    adwin.set_DAC_2(magv)
    qt.msleep(10)
    pna.sweep()
    qt.msleep(450)
    #trace = pna.fetch_data(polar=True)
    tr2=pna.data_f()

    #let it settle        
    qt.msleep(.1)

    data.add_data_point(mag_v, list(mag_v*ones(len(magvlist))),tr2)

    data.new_block()
    spyview_process(data,start_probe_f,stop_probe_f,mag_v)
  
    qt.msleep(0.01) #wait 10 usec so save etc
    
data.close_file()

adwin.set_DAC_2(0)
qt.mend()
#end of experiment routine

print 'ready at', localtime()[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
