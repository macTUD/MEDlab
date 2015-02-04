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


rf_power = 0
aver=30
start_frequency= 3190
stop_frequency= 3290
sweep_points = 501

KHz =0.001
zvb_bandwidth = 0.005*KHz

#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points*sweep_sections)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'zvb' not in instlist:
    zvb = qt.instruments.create('zvb','RS_ZVB',address='TCPIP::192.168.100.23::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('Vibhor & Raj hangers')
med.set_setup('50 ohm device')
med.set_user('Vibhor')


#R&S ZVB VNA instruments

#zvb.reset()
#1zvb.set_source_power(rf_power)
#2zvb.set_resolution_bandwidth(zvb_bandwidth)
#3zvb.set_sweeppoints(sweep_points)
#zvb.get_all() #get all the settings and store it in the settingsfile
#4zvb.set_trace_continuous(True)  
#5zvb.set_averages(aver)
#6wait_time=zvb.get_sweeptime()*aver

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_vna_hres_wait_avg_and_grab_phase.py'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=sweep_points)
data.add_value('S11 [degree]')
#data.add_value('Summed trace ')

data.create_file()
data.copy_file('bf_vna_hres_wait_avg_and_grab_phase.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
tstart = time()

#1zvb.set_start_frequency(start_frequency)
#1zvb.set_stop_frequency(stop_frequency)
#1qt.msleep(wait_time)
trace = zvb.grab_trace()

data.add_data_point(flist,trace)
spyview_process(data,start_frequency,stop_frequency) 
qt.msleep(0.01)

data.close_file()
qt.mend()
#end of normalization routine
