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
#           FUNCTIONS
##################################

def magnitude(real,imaginary):
    return np.sqrt(real*real + imaginary*imaginary)

def phase(real,imaginary):
    return 180*np.arctan(imaginary/real)
    

################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
#max_runtime = 60000 #sec
#max_sweeptime = 60000 #sec

rf_power = -25

start_frequency= 5045
stop_frequency= 5295
sweep_points = 500
sweep_sections = 2

KHz =0.001
zvm_bandwidth = 1*KHz


print  '%s [KHz]' %(zvm_bandwidth/KHz)
print  (stop_frequency-start_frequency)/(sweep_points*sweep_sections*KHz)



#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points*sweep_sections)
sweep_section_list = np.linspace(start_frequency,stop_frequency,sweep_sections)

power_start=-20
power_stop= 0
power_points=21


power_list=np.linspace(power_start,power_stop,power_points)



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


#measurement information stored in manual in MED instrument
med.set_device('Vibhor & Raj hangers')
med.set_setup('poormans RF dipstick A-C cable device')
med.set_user('Vibhor,Raj')


#R&S zvm VNA instruments

#zvm.reset()
zvm.set_source_power(-40)

zvm.set_resolution_bandwidth(zvm_bandwidth)
zvm.set_sweeppoints(sweep_points)

#zvm.set_trace_continuous(False)  


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'pm_vna_20GHz_hres_powerSweep_v03'  # Actually this is folder name
data = qt.Data(name=filename)
data.add_coordinate('Power [dBm]',size=power_points)
data.add_coordinate('Frequency [MHz]',size=sweep_points)
data.add_value('S21 [dB]')
data.add_value('S21 [degree]')
data.create_file()
data.copy_file('pm_vna_20GHz_hres_powerSweep_v03.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables



for i in power_list:
    zvm.set_source_power(i)
    print i
    
    sweep_section_index=0
    
    temp_odd =[]
    temp_even =[]
    magnitude_list=[]
    phase_list=[]
    while(sweep_section_index<sweep_sections):
        print sweep_section_index
        trace=[]
        zvm.set_start_frequency(flist[sweep_section_index*sweep_points])
        zvm.set_stop_frequency(flist[(sweep_section_index+1)*sweep_points-1])
        print zvm.get_start_frequency()
        qt.msleep(10)
        trace=zvm.get_trace()
        temp_odd.extend(trace[1::2])
        temp_even.extend(trace[::2])
        sweep_section_index+=1
         
    index=0

    while(index<len(temp_odd)):
        magnitude_list.append(magnitude(float(temp_even[index]),
                                              float(temp_odd[index])))

        phase_list.append(phase(float(temp_even[index]),float(temp_odd[index])))

        index+=1
            
        
    data.new_block()
    dummy_power=np.linspace(i,i,len(flist))
    data.add_data_point(dummy_power,flist,magnitude_list,phase_list)
    spyview_process(data,start_frequency,stop_frequency,i)

    qt.msleep(0.1)

data.close_file()
qt.mend()


