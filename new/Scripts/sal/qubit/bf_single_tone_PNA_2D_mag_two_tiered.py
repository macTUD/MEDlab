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
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec

#1st coordinate
##start_frequency= 5310
##stop_frequency= 5410
##f_points =101

start_freq = 5.032e9
stop_freq=5.096e9
f_points =2001
bandwidth=100
power0 =30
power1 =10
power2=0
power3=-10

ave0=1
ave1=40
ave2=80
ave3=120

flist=np.linspace(float(start_freq),float(stop_freq),f_points)

#magnetic field
start_magv = 0
stop_magv = 1.
magv_points = 41
##
magvlist=np.linspace(float(start_magv),float(stop_magv),magv_points)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS3_standard_transmon_A')
med.set_setup('BF')
med.set_user('Sal')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')



pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq)
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
sweeptime = pna.get_sweeptime()+4

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data Tier 0
filename = 'bf_single_tone_PNA_2D_mag_tier0'
data0 = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data0.add_coordinate('Frequency (MHz)')
data0.add_coordinate('V_adwin (V)')
data0.add_value('Transmission (dBm)')
data0.add_value('f_data [dBm]')
data0.add_value('Phase')

data0.create_file()
data0.copy_file('bf_single_tone_PNA_2D_mag_two_tiered.py')

#Set up data Tier1
filename = 'bf_single_tone_PNA_2D_mag_tier1'
data1 = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data1.add_coordinate('Frequency (MHz)')
data1.add_coordinate('V_adwin (V)')
data1.add_value('Transmission (dBm)')
data1.add_value('f_data [dBm]')
data1.add_value('Phase')

data1.create_file()
data1.copy_file('bf_single_tone_PNA_2D_mag_two_tiered.py')

#Set up data Tier2
filename = 'bf_single_tone_PNA_2D_mag_tier2'
data2 = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data2.add_coordinate('Frequency (MHz)')
data2.add_coordinate('V_adwin (V)')
data2.add_value('Transmission (dBm)')
data2.add_value('f_data [dBm]')
data2.add_value('Phase')

data2.create_file()
data2.copy_file('bf_single_tone_PNA_2D_mag_two_tiered.py')

#Set up data Tier3
filename = 'bf_single_tone_PNA_2D_mag_tier3'
data3 = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data3.add_coordinate('Frequency (MHz)')
data3.add_coordinate('V_adwin (V)')
data3.add_value('Transmission (dBm)')
data3.add_value('f_data [dBm]')
data3.add_value('Phase')

data3.create_file()
data3.copy_file('bf_single_tone_PNA_2D_mag_two_tiered.py')



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
exp_number = len(magvlist)

adwin.set_DAC_2(magvlist[0])
print 'wait until DAC is ramped'
qt.msleep(2)
#while (x_time < max_runtime or  and run_index<norm_runs):

for magv in magvlist:

    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60

    print magv, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    #Set Voltage
    adwin.set_DAC_2(magv)     
    qt.msleep(.5)

    #Do tier 0
    pna.set_power(power0)
    pna.sweep()
    qt.msleep(sweeptime)
    trace=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)
    data0.add_data_point(flist, list(magv*ones(len(flist))),trace[0], tr2, trace[1])

    data0.new_block()
    spyview_process(data0,start_freq,stop_freq,magv)
    qt.msleep(0.01) #wait 10 usec so save etc

    #Do tier 1
    pna.set_power(power1)
    pna.sweep()
    qt.msleep(sweeptime)
    trace=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)
    data1.add_data_point(flist, list(magv*ones(len(flist))),trace[0], tr2, trace[1])

    data1.new_block()
    spyview_process(data1,start_freq,stop_freq,magv)
    qt.msleep(0.01) #wait 10 usec so save etc

    #Do tier 2
    pna.set_power(power2)
    pna.sweep()
    qt.msleep(sweeptime)
    trace=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)
    data2.add_data_point(flist, list(magv*ones(len(flist))),trace[0], tr2, trace[1])

    data2.new_block()
    spyview_process(data2,start_freq,stop_freq,magv)
    qt.msleep(0.01) #wait 10 usec so save etc

    #Do tier 3
    pna.set_power(power3)
    pna.sweep()
    qt.msleep(sweeptime)
    trace=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)
    data3.add_data_point(flist, list(magv*ones(len(flist))),trace[0], tr2, trace[1])

    data3.new_block()
    spyview_process(data3,start_freq,stop_freq,magv)
    qt.msleep(0.01) #wait 10 usec so save etc



data0.close_file()
data1.close_file()
data2.close_file()
data3.close_file()
qt.mend()
#end of experiment routine

