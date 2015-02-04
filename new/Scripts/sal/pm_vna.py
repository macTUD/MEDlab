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
#max_runtime = 60000 #sec
#max_sweeptime = 60000 #sec

rf_power = 0
exp_run=20


start_frequency= 2600
stop_frequency= 4000
sweep_points = 1000
KHz =0.001
zvb_bandwidth = 0.1*KHz

#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)


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
med.set_setup('poormans RF dipstick A-C cable device')
med.set_user('Vibhor,Raj')


#R&S ZVB VNA instruments

#zvb.reset()
zvb.set_source_power(rf_power)

zvb.set_resolution_bandwidth(zvb_bandwidth)
zvb.set_sweeppoints(1000)
#zvb.get_all() #get all the settings and store it in the settingsfile
#zvb.set_trace_continuous(False)  


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'pm_vna'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=sweep_points)
data.add_value('S12')
#data.add_value('Summed trace ')

data.create_file()
data.copy_file('pm_vna.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
#tstart = time()
#trace=[]
while (run_index<exp_run):
    
    
    data.new_block()

    trace = zvb.get_trace()

    data.add_data_point(flist,trace)
    spyview_process(data,start_frequency,stop_frequency) 
    run_index+=1
    qt.msleep(0.001)
    
data.close_file()
qt.mend()
#end of normalization routine
