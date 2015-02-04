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
averages=1

flist=np.linspace(float(start_freq),float(stop_freq),f_points)

#2nd coordinate
##start_magvoltage = 0
##stop_magvoltage = 9.8
##magv_points = 10
##
##magvlist=np.linspace(float(start_magvoltage),float(stop_magvoltage),magv_points)
start_power=30
stop_power=-30
power_points=5
power_list=np.linspace(float(start_power),float(stop_power),power_points)

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
sweeptime = pna.get_sweeptime()*1.1
pna.set_averages_on()

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program

adwin.set_DAC_2(1)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone_PNA_2D_power'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Power (dBm)')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')
data.add_value('averages')

data.create_file()
data.copy_file('bf_single_tone_PNA_2D_power.py')

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
exp_number = len(power_list)


#while (x_time < max_runtime or  and run_index<norm_runs):

adwin.set_DAC_2(-1.)

for power in power_list:

    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60

    ave = 1 #int(averages-power)

    ave_list=np.linspace(1,ave,ave)

    print power, ave, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    #Set Voltage
    #adwin.set_DAC_2(magv)     
    qt.msleep(0.1)
    pna.set_power(power)
    pna.set_averages(ave)
    sweeptime = pna.get_sweeptime()*1.1

    for i in ave_list:
        pna.sweep()
        qt.msleep(sweeptime)
        
    trace=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)

    data.add_data_point(flist, list(power*ones(len(flist))),trace[0], tr2, trace[1],list((ave)*ones(len(flist))))

    data.new_block()
    spyview_process(data,start_freq,stop_freq,power)
    qt.msleep(0.01) #wait 10 usec so save etc


##        index=0
##    for f in flist:
##        print 'frequency [MHz]', f, trace[index],v
##        index=index+1
data.close_file()
qt.mend()
#end of experiment routine
