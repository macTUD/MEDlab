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
max_runtime = 3600 #sec
#max_sweeptime = 60 #sec

rf_power = -10
norm_runs = 100
exp_runs=1


start_frequency= 4000
stop_frequency= 10000
sweep_points =18000


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
smb.set_RF_power(rf_power)
smb.set_RF_frequency(start_frequency)
smb.set_RF_state(True)


#FSL18 instrument variables
kHz=0.001
fsl_bandwidth = 10*kHz      #MHz
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


var = raw_input("Enter name of normalization file: ")
normalization =np.loadtxt(var,delimiter=' ')

#Set up data
filename = 'pm_temp_fsl_experiment_ext_signal'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=sweep_points)
data.add_coordinate('time [s]')
data.add_value('Normed RF Power (dBm)')
data.add_value('Raw RF Power (dBm)')
data.add_value('Temp (K)')

data.create_file()
data.copy_file('pm_temp_fsl_experiment_ext_signal.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=3) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()

summed_trace =array(0*ones(sweep_points))           #if one wants to use these results as a normalization

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

        trace.append(fsl.get_trace()[51])        

        #y_temp = (float(rigol.value()[13:])-221.47)/0.23377+4.2
        print trace_index, y_temp, trace[trace_index], smb.get_RF_frequency()

        trace_index += 1

    summed_trace+=trace
    time_list = x_time*ones(len(trace))
    temp_list = y_temp*ones(len(trace))
    
    data.new_block()
    data.add_data_point(flist,time_list,trace-normalization,trace, temp_list) #store data
    spyview_process(data,start_frequency,stop_frequency,x_time) 
    qt.msleep(0.01) #wait 10 usec so save etc

    run_index=run_index+1
    print run_index, x_time

exp_normalization = summed_trace/(run_index)

data.close_file()
qt.mend()
#end of experiment routine

print 'end of experiment routine'

exp_var = raw_input("Enter name to store normalization file: ")


if(exp_var!=None):
    np.savetxt(exp_var,exp_normalization, delimiter=' ')
