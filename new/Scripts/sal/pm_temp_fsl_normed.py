################################
#       DEVELOPMENT NOTES/LOG
################################

#line 65 needs cleaning like set trace=[] and later fill it inside loop
#line 110 also same issue


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

#Independent Variables 
start_frequency= 10
stop_frequency= 18000
bandwidth = 0.07 #MHz
max_runtime = 600 #sec
rf_power = 0
norm_runs = 1
exp_runs=1


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'rigol' not in instlist:
    rigol= qt.instruments.create('rigol','rigol_dm3058',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')

if 'fsl' not in instlist:
    fsl= qt.instruments.create('fsl','RS_FSL',address='TCPIP::192.168.100.21::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#measurement information stored in manual in MED instrument
med.set_device('cpw 10um and 20um centerpin width (EOS1)')
med.set_setup('poormans RF dipstick')
med.set_user('Ben,Sal,Vibhor,Raj')

print rigol.query('*IDN?')
print fsl.query('*IDN?')

#Set up FSL
print 'prepare FSL for normalization'

fsl.reset()
fsl.set_start_frequency(start_frequency)
fsl.set_stop_frequency(stop_frequency)
fsl.set_resolution_bandwidth(bandwidth)
fsl.set_tracking(True)
fsl.set_source_power(rf_power)
#fsl.set_averages(normalization_averages) #set the number of normalization runs
fsl.get_all() #get all the settings and store it in the settingsfile
fsl.set_trace_continuous(False)                                                         #WHAT IS THIS FUNCTION???

#Dependent Variables     NEEDS CLEANING SET trace=[] and later fill it.
#Do test trace to set up frequency list
trace=fsl.get_trace()
flist=np.linspace(float(start_frequency),float(stop_frequency),num=len(trace))


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'fsl_temp_sec_normalization'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=fsl.get_sweeppoints())
data.add_coordinate('time [s]')
data.add_value('RF Power (dBm)')
data.add_value('Summed trace ')
data.add_value('Temp (K)')

data.create_file()
data.copy_file('pm_temp_fsl_normed.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


################################
#      NORMALIZATION LOOP
################################

print 'Start normalization experiment:'

run_index=0
summed_trace =0                         #Change this into summed_trace = array([])
summed_trace = array(fsl.get_trace()) #first local_trace
tstart = time()
x_time = 0
y_temp =0

while (x_time < max_runtime and run_index<norm_runs):

    x_time = time()- tstart
    y_temp = (float(rigol.value()[13:])-221.47)/0.23377+4.2
    #temperature converted to [K] (calibration by Vibhor)
    
    trace=fsl.get_trace() #FSL measurement

    summed_trace+=trace
    time_list = x_time*ones(len(trace))   #make list
    temp_list = y_temp*ones(len(trace))   #make list


    data.new_block()
    data.add_data_point(flist,time_list,trace,list(numpy.array(summed_trace).reshape(-1,)),temp_list) #store data
    spyview_process(data,start_frequency,stop_frequency,x_time) 
    qt.msleep(0.01) #wait 10 usec so save etc

    run_index=run_index+1
    print run_index, x_time,y_temp 

print run_index, x_time,y_temp

#now all the traces are summed into local_trace, now the number of traces summed is run_index + 2 
normalization = summed_trace/(run_index+1)

data.close_file()
qt.mend()
#end of normalization routine

print 'end of normalization'

var = raw_input("Enter something to start experiment: ")
print "you entered ", var


####################################################################
####################################################################
##      EXPERIMENT
####################################################################
####################################################################


################################
#      INSTRUMENTS
################################

#IS THIS AGAIN NECESSARY??
fsl.reset()
fsl.set_start_frequency(start_frequency)
fsl.set_stop_frequency(stop_frequency)
fsl.set_resolution_bandwidth(bandwidth)
fsl.set_tracking(True)
fsl.set_source_power(rf_power)
fsl.get_all() #get all the settings and store it in the settingsfile
fsl.set_trace_continuous(False)    


################################
#      DATA INITIALIZATION
################################

qt.mstart()
spyview_process(reset=True) #clear old meta-settings
filename = 'pm_temp_fsl_normed'

print 'prepare datafile'
data = qt.Data(name=filename)
data.add_coordinate('Frequency [MHz]',size=fsl.get_sweeppoints())
data.add_coordinate('time [s]')
data.add_value('RF Power [dBm]')
data.add_value('normed RF Power [dBm]')
data.add_value('Temp [K]')
data.create_file()
data.copy_file('pm_temp_fsl_normed.py')
    
print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=3) #creates bugs


################################
#   EXPERIMENT LOOP
################################

tstart = time()
sleep(0.1)
x_time = 0
run_index=0
#normed_trace = array(fsl.get_trace())
normed_trace=0


print 'measurement loop:'
while (x_time < max_runtime and run_index<exp_runs):
    x_time = time()- tstart
    y_temp = (float(rigol.value()[13:])-221.47)/0.23377+4.2 #temperature converted to [K] (calibration by Vibhor)
    trace=fsl.get_trace() #FSL measurement
    time_list = x_time*ones(len(trace))   #make list
    temp_list = y_temp*ones(len(trace))   #make list

    normed_trace = array(trace)-normalization

    data.new_block()
    
    data.add_data_point(flist, time_list, trace, normed_trace, temp_list) #store data
    spyview_process(data,start_frequency,stop_frequency,x_time) 
    qt.msleep(0.01) #wait 10 usec so save etc

    run_index+=1
    print run_index, x_time,y_temp

data.close_file()
qt.mend()

#Set FSL back to continuous tracing
fsl.set_trace_continuous(True)
