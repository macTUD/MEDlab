################################
#       DEVELOPMENT NOTES/LOG
################################




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
max_runtime = 600 #sec
max_sweeptime = 60 #sec

rf_power = 0
norm_runs = 2
exp_runs=1


start_frequency= 10
stop_frequency= 12750
sweep_points =100


#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)


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

if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.100.22::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('cpw 10um and 20um centerpin width (EOS1)')
med.set_setup('poormans RF dipstick')
med.set_user('Ben,Sal,Vibhor,Raj')

print rigol.query('*IDN?')
print smb.query('*IDN?')
print fsl.query('*IDN?')


#SMB 100A instrument
smb.reset()
smb.set_RF_power(-10)
smb.set_RF_frequency(start_frequency)
smb.set_RF_state(True)


#FSL18 instrument variables
kHz=0.001
fsl_bandwidth = .1*kHz      #MHz
fsl_span = 0.01*kHz           #MHz
fsl_sweep_points =101

def fsl_start(f_center,span):
    return float(f_center-span/2)

def fsl_stop(f_center, span):
    return float(f_center+span/2)

fsl.reset()
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
filename = 'pm_temp_fsl_normed_ext_signal.py'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=sweep_points)
data.add_coordinate('time [s]')
data.add_value('RF Power (dBm)')
data.add_value('Summed trace ')
data.add_value('Temp (K)')

data.create_file()
data.copy_file('pm_temp_fsl_normed_ext_signal.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


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

print 'Start measurement'

while (x_time < max_runtime and run_index<norm_runs):

    x_time = time() - tstart
    y_temp = (float(rigol.value()[13:])-221.47)/0.23377+4.2
    #temperature converted to [K] (calibration by Vibhor)

    #Take trace
    trace_index=0
    trace=[]
    while(trace_index<sweep_points):

        smb.set_RF_frequency(flist[trace_index])
        fsl.set_start_frequency(fsl_start(flist[trace_index],fsl_span))
        fsl.set_stop_frequency(fsl_stop(flist[trace_index],fsl_span))

        #sleep(1)
            
        trace.append(fsl.get_trace()[51])        

        print trace_index, trace[trace_index], smb.get_RF_frequency(), fsl.get_start_frequency(), fsl.get_stop_frequency()

        trace_index += 1

    summed_trace+=trace
    time_list = x_time*ones(len(trace))
    temp_list = y_temp*ones(len(trace))
    
    data.new_block()
    data.add_data_point(flist,time_list,trace,summed_trace, temp_list) #store data
    spyview_process(data,start_frequency,stop_frequency,x_time) 
    qt.msleep(0.01) #wait 10 usec so save etc

    run_index=run_index+1
    print run_index, x_time

normalization = summed_trace/(run_index)

data.close_file()
qt.mend()
#end of normalization routine

print 'end of normalization routine'

var = raw_input("Enter name for normalization file: ")
print "the normalization is save as",var,".txt"

var = var+'.txt'

np.savetxt(var,normalization, delimiter=' ')

##
###start measurement routine
##
##print 'prepare FSL for experiment'
###required preperation stuff (FSL)
##fsl.reset()
##fsl.set_start_frequency(start_frequency)
##fsl.set_stop_frequency(stop_frequency)
###span=stop_frequency-start_frequency
##fsl.set_resolution_bandwidth(bandwidth)
###fsl.set_averages(1) #set the number of normalization runs
##fsl.set_tracking(True)
##fsl.set_source_power(rf_power)
##fsl.get_all() #get all the settings and store it in the settingsfile
##
##qt.mstart()
##spyview_process(reset=True) #clear old meta-settings
##filename = 'pm_temp_fsl_normed'
##
##print 'prepare datafile'
##data = qt.Data(name=filename)
##data.add_coordinate('Frequency [MHz]',size=fsl.get_sweeppoints())
##data.add_coordinate('time [s]')
##data.add_value('RF Power [dBm]')
##data.add_value('normed RF Power [dBm]')
###data.add_coordinate('Temp [K]')
##data.add_value('Temp [K]')
###data.add_value(rigol.get_function()[1:-1]+ ' ') #whatever rigol is set to
##data.create_file()
##data.copy_file('pm_temp_fsl_normed.py')
##
###time variable
##
##    
##print 'prepare 2D plot'
###plot3d=qt.Plot3D(data, name=filename, coorddim=(0,1), valdim=3) #creates bugs
##plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=3) #creates bugs
##
####print 'Measure with Rigol: ' + rigol.get_function()[1:-1]
#####rigol.set_disp_off()
##fsl.set_trace_continuous(False)    
##tstart = time()
##sleep(0.1)
##
###normed_trace = normalization
##x_time = 0
##run_index=0
###normed_trace = array(fsl.get_trace())
##normed_trace=0
##print 'measurement loop:'
##while (x_time < max_runtime and run_index<exp_runs):
##    x_time = time()- tstart
##    y_temp = (float(rigol.value()[13:])-221.47)/0.23377+4.2 #temperature converted to [K] (calibration by Vibhor)
##    trace=fsl.get_trace() #FSL measurement
##    time_list = x_time*ones(len(trace))   #make list
##    temp_list = y_temp*ones(len(trace))   #make list
##
##    normed_trace = array(trace)-normalization
##
##    data.new_block()
##    
##    data.add_data_point(flist, time_list, trace, normed_trace, temp_list) #store data
##    spyview_process(data,start_frequency,stop_frequency,x_time) 
##    qt.msleep(0.01) #wait 10 usec so save etc
##
##    run_index+=1
##    print run_index, x_time,y_temp
##
##data.close_file()
##qt.mend()
##
###end measurement routine
##
##
##fsl.set_trace_continuous(True)
###rigol.set_disp_on()
