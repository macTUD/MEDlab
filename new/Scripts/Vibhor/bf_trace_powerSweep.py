################################
#       DEVELOPMENT NOTES/LOG
################################

#transform into virtual spectrum analyser module
# build in normalization check / security measure



################################
#      IMPORTS
################################

import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables

def_rf_power = -80

power_start=-50
power_stop= -40
power_points=2

GHz=1000
start_frequency= 6.970*GHz
stop_frequency= 7.0*GHz
sweep_points =101+1

#FSL18 instrument variables
kHz=0.001
fsl_bandwidth = 1*kHz#MHz
fsl_span = 0.01*kHz           #MHz
fsl_sweep_points =101




#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)
power_list=np.linspace(power_start,power_stop,power_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsl' not in instlist:
    fsl= qt.instruments.create('fsl','RS_FSL',address='TCPIP::192.168.100.21::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.100.25::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS2_5.5GHz_Q=25k')
med.set_setup('BF Darkside')
med.set_user('Sal & Vibhor')

print smb.query('*IDN?')
print fsl.query('*IDN?')


#SMB 100A instrument
#smb.reset()
smb.set_RF_power(def_rf_power)
smb.set_RF_frequency(start_frequency)
smb.set_RF_state(True)




def fsl_start(f_center,span):
    return float(f_center-span/2)

def fsl_stop(f_center, span):
    return float(f_center+span/2)

#fsl.reset()
fsl.set_resolution_bandwidth(fsl_bandwidth)
fsl.set_tracking(False)
fsl.set_sweeppoints(101)
fsl.get_all() #get all the settings and store it in the settingsfile
fsl.set_trace_continuous(False)  


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_trace'
data = qt.Data(name=filename)
data.add_coordinate('RF Power [dBm]')
data.add_coordinate('Frequency (MHz)',size=sweep_points)
data.add_value('RF Power (dBm)')

data.create_file()
data.copy_file('bf_trace_powerSweep.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=1, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()


summed_trace =array(0*ones(sweep_points))


x_time = 0
y_temp =0
measurement_time=0

x_time = time() - tstart

for i in power_list:
    smb.set_RF_power(i)
    trace_index=0
    trace=[]
    while(trace_index<sweep_points):
        smb.set_RF_frequency(flist[trace_index])
        fsl.set_start_frequency(fsl_start(flist[trace_index],fsl_span))
        fsl.set_stop_frequency(fsl_stop(flist[trace_index],fsl_span))
        trace.append(fsl.get_trace()[51])        

        print i, smb.get_RF_frequency()

        trace_index += 1
    
    data.new_block()
    dummy_power=np.linspace(i,i,len(flist))
    data.add_data_point(dummy_power,flist,trace) #store data
    spyview_process(data,start_frequency,stop_frequency,i) 
    qt.msleep(0.01) #wait 10 usec so save etc
    run_index=run_index+1
    print run_index, x_time

data.close_file()
qt.mend()
#end
