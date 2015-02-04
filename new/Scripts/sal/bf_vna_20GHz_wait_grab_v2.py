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
#execfile('metagen.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
#max_runtime = 60000 #sec
#max_sweeptime = 60000 #sec


#KHz =0.001


#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)



#power_list=np.linspace(power_start,power_stop,power_points)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'zvm' not in instlist:
    zvm = qt.instruments.create('zvm','RS_ZVM',address='GPIB::20::INSTR')
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


rf_power = zvm.get_source_power()
start_frequency= zvm.get_start_frequency()
stop_frequency= zvm.get_stop_frequency()
sweep_points = zvm.get_sweeppoints()
zvm_bandwidth = zvm.get_resolution_bandwidth()

#measurement information stored in manual in MED instrument
med.set_device('Vibhor & Raj hangers')
med.set_setup('BF 50 Ohm device')
med.set_user('Vibhor')


#R&S zvm VNA instruments

#zvm.reset()
#1zvm.set_source_power(-20)
#1zvm.set_resolution_bandwidth(zvm_bandwidth)
#1zvm.set_sweeppoints(sweep_points)
#zvm.get_all() #get all the settings and store it in the settingsfile
#1zvm.set_trace_continuous(True)  


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_vna_20GHz_wait_grab_v2'
data = qt.Data(name=filename)
data.add_coordinate('Frequency [MHz]',size=sweep_points)
#data.add_coordinate('Power [dBm]',size=power_points)
data.add_value('S21 [dB]')
data.add_value('S21 [degree]')
#data.add_value('S21 []')
#data.add_value('Summed trace ')

data.create_file()
data.copy_file('bf_vna_20GHz_wait_grab_v2.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables

#tstart = time()

#1sweep_time = eval(zvm.query('SWEep:TIME?'))
trace=[]
#zvm.set_start_frequency(flist[sweep_section_index*sweep_points])
#zvm.set_stop_frequency(flist[(sweep_section_index+1)*sweep_points-1])
#qt.msleep(500)
trace=zvm.grab_trace()
trace_X=trace[::2]
trace_Y=trace[1::2]
trace_r=map(lambda x,y:x*x+y*y,X,Y)
trace_theta=map(lambda x,y:180/3.14*math.atan2(y,x),X,Y)
data.add_data_point(flist,trace_r,trace_theta)
#spyview_process(data,start_frequency,stop_frequency)
qt.msleep(0.001)
data.close_file()
qt.mend()
#end of normalization routine
