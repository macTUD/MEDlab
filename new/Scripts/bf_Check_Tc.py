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
max_runtime = 600000 #sec
max_sweeptime = 600000 #sec

rf_power = -50
norm_runs = 10000000
exp_runs=1

GHz=1000
start_frequency= 6.0*GHz
stop_frequency= 6.0*GHz
sweep_points =1



#FSL18 instrument variables
kHz=0.001
fsl_bandwidth = 10*kHz#MHz
fsl_span = 0.01*kHz           #MHz
fsl_sweep_points =101




#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)


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
med.set_device('BigWafer3_mix Tc')
med.set_setup('BluFors')
med.set_user('Vibhor')

print smb.query('*IDN?')
print fsl.query('*IDN?')


#SMB 100A instrument
#smb.reset()
smb.set_RF_power(rf_power)
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
#spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_trace_Tc'
data = qt.Data(name=filename)
data.add_coordinate('time [s]')
data.add_value('RF Power (dBm)')
data.create_file()
data.copy_file('bf_Check_Tc.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()

while (x_time < max_runtime and run_index<norm_runs):

    x_time = time() - tstart

    #Take trace
    trace_index=0
    trace=[]
    poi=fsl.get_trace()[51];
    tm=time();
    data.add_data_point(tm,poi) 
    qt.msleep(1) #wait 10 usec so save etc

    run_index=run_index+1
    print run_index, x_time,poi

normalization = summed_trace/(run_index)

data.close_file()
qt.mend()
#end
