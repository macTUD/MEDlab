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

#some global variables
kHz=0.001

################################
#     EXPERIMENT VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables

#cw_frequency = 3.586874e9 #this is the center of the cavity resonance
cw_frequency = 5e9
#delta = .1e6 #this is the detuning we want to set the PNA Receiver to.

#smb_center_freq=cw_frequency/1e3

#stop_probe_f = 9000
start_probe_f=1.5e9
stop_probe_f=2e9
sweep_points = 2000

#point_list=np.linspace(1,sweep_points,sweep_points)
#sweep_t = 200 #sweeptime in seconds that the PNA sweeps.

probe_list=np.linspace(float(start_probe_f),float(stop_probe_f),sweep_points)

start_delta=-40
stop_delta=40
delta_points=200

#delta_list=np.linspace(float(start_delta),float(stop_delta),delta_points)
delta_list=np.linspace(cw_frequency/1e6+start_delta,cw_frequency/1e6+stop_delta,delta_points)


step_size = int(sweep_points/delta_points)

point_list=[]
j=0
for i in delta_list:
    j=0
    while j<step_size:
        point_list.append(i)
        j=j+1

##
###2nd coordinate
##start_magvoltage =-.8
##stop_magvoltage = .8
##magv_points = 2
####
##magvlist=np.linspace(float(start_magvoltage),float(stop_magvoltage),magv_points)

start_power=-30
stop_power=10
power_points=8

power_list=np.linspace(float(start_power),float(stop_power),power_points)

#########################################
#            INSTRUMENTS VARIABLES
#########################################


#This script assumes that the signal analyser is already setup with the SMB100A tracking generator (TTL mode)
#Also this script assumes all the REF's 10MHz are well set up


#PNA instrument variables

probe_source_power = -30 #dBm
cav_source_power = -30 #dBm
bandwidth = 500e3


######################################################################################



################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_double_tone_PNA'
data = qt.Data(name=filename)
data.add_coordinate('Detuning from CW [MHz]')
#data.add_coordinate('Probe Frequency (MHz)')
data.add_coordinate('Power (dBm)')
#data.add_value('Mlog R2,1 (dBm)')
data.add_value('f_data [dBm]')
#data.add_value('Phase R2,1')

data.create_file(file)
data.copy_file('bf_double_tone_PNA.py')


#########################################
#           MANUAL INSTRUMENT INIT
#########################################

print 'Init instruments'


#INIT ADWIN

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program
adwin.set_DAC_2(0)

#INIT SGS
smb.set_RF_frequency(float(cw_frequency/1e6))
smb.set_RF_power(cav_source_power)
smb.set_RF_state(True)
##
##pna.reset()
##pna.setup()
##
###receiver_freq=cw_frequency-delta
##
##pna.setup_2tone_spectroscopy(cw_freq=cw_frequency, start_freq=start_probe_f,
##                             stop_freq=stop_probe_f)
##
##pna.set_power(probe_source_power)
##pna.set_resolution_bandwidth(bandwidth)
##pna.set_sweeppoints(sweep_points)
##sweeptime = pna.get_sweeptime()
##

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

timestep = float(10)/float(delta_points)

for power in power_list:
#    sgs.set_RF_state(False)
    #print probe

    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60
    
    print power, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]


    smb.set_RF_power(power)
    smb.set_RF_frequency(cw_frequency/1e6)
    pna.sweep()
    for delta in delta_list:
        #smb.set_RF_frequency(cw_frequency/1e6+delta)
        smb.set_RF_frequency(delta)
        qt.msleep(timestep)

    qt.msleep(2)
    tr2=pna.data_f()
    data.add_data_point(point_list, list(power*ones(sweep_points)),tr2)
    data.new_block()
    spyview_process(data,point_list[0],point_list[-1],power)
    qt.msleep(0.01) #wait 10 usec so save etc
    
data.close_file()

#adwin.set_DAC_2(0)
qt.mend()
#end of experiment routine

print 'ready at', localtime()[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
