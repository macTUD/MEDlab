################################
#       DESCRIBTION
################################

#Measurement script that does double tone qubit spectroscopy using the SGMA
#as the swept probe frequency


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
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec


#PNA sweep
start_freq = 5.067e9
stop_freq=5.071e9
f_points =601
bandwidth=100
power=-22
ave=15
#96attenuation outside

#SMB & SGS Sweep
probe_start = 5050
probe_stop = 5030
probe_points = 200
probe_power=-12

flist=np.linspace(float(start_freq),float(stop_freq),f_points)
plist=np.linspace(float(probe_start),float(probe_stop),probe_points)

#magnetic field
v_adwin=0.0074

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'sgs' not in instlist:
    sgs = qt.instruments.create('sgs','RS_SGS100A', address='TCPIP::192.168.1.100::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb', 'RS_SMB100A_DEV', address='TCPIP::192.168.1.50::INSTR')

#if 'adwin_DAC' not in instlist:
#    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS3_standard_transmon_A')
med.set_setup('BF')
med.set_user('Sal')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')


#PNA initialization
pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq)
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
sweeptime = pna.get_sweeptime()*1.01
pna.set_averages_on()
pna.set_averages(ave)

#SGS initialization
smb.set_RF_frequency(1000)
smb.set_RF_state(True)
smb.set_RF_power(probe_power)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_double_tone_PNA_2D_quick'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Probe_frequency (MHz)')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file()
data.copy_file('bf_double_tone_PNA_2D_quick.py')

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
exp_number = len(plist)*ave


#set ADWIN to right value:


adwin.set_DAC_2(v_adwin)
ave_list=np.linspace(1,ave,ave)

#while (x_time < max_runtime or  and run_index<norm_runs):

for probe_f in plist:

    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60

        
    smb.set_RF_frequency(float(probe_f))
    print probe_f, smb.get_RF_frequency(), 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    #Set Voltage
    #adwin.set_DAC_2(magv)     
    qt.msleep(0.1)
    print 'sweep'
    #clear pna
    pna.reset_averaging()
    
    for i in ave_list:
        print 'sweep', i        
        pna.sweep()
        qt.msleep(sweeptime)

    trace=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)
    data.add_data_point(flist, list(probe_f*ones(len(flist))),trace[0], tr2, trace[1])

    data.new_block()
    spyview_process(data,start_freq,stop_freq,probe_f)
    qt.msleep(0.01) #wait 10 usec so save etc


##        index=0
##    for f in flist:
##        print 'frequency [MHz]', f, trace[index],v
##        index=index+1
data.close_file()
qt.mend()
#end of experiment routine

