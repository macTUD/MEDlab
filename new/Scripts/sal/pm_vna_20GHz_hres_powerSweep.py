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

rf_power = -25
exp_run=1


start_frequency= 3000
stop_frequency= 3100
sweep_points = 500
sweep_sections = 2

KHz =0.001
zvm_bandwidth = 10*KHz

#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points*sweep_sections)
sweep_section_list = np.linspace(start_frequency,stop_frequency,sweep_sections)

power_start=-20
power_stop= -20
power_points=1


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
#zvm.get_all() #get all the settings and store it in the settingsfile
#zvm.set_trace_continuous(False)  


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'pm_vna_20GHz_hres_powerSweep'
data = qt.Data(name=filename)
data.add_coordinate('Frequency [MHz]',size=sweep_points)
data.add_coordinate('Power [dBm]',size=power_points)
data.add_value('S21 [Real]')
#data.add_value('S21 [Imag]')
#data.add_value('S21 []')
#data.add_value('Summed trace ')

data.create_file()
data.copy_file('pm_vna_20GHz_hres_powerSweep.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables

#tstart = time()


for i in power_list:
    zvm.set_source_power(i)
    run_index=0
    while (run_index<exp_run):
        trace=[]
        sweep_section_index=0

        while(sweep_section_index<sweep_sections):
            print sweep_section_index

            zvm.set_start_frequency(flist[sweep_section_index*sweep_points])
            zvm.set_stop_frequency(flist[(sweep_section_index+1)*sweep_points-1])
            
            temp=zvm.get_trace()
            real= temp[1::2]
            imag= temp[::2]
            
            trace.extend(real)
            #trace2.extend(imag)

            sweep_section_index+=1
        
        data.new_block()
        dummy_power=np.linspace(i,i,len(flist))
        data.add_data_point(flist,dummy_power,trace)
        spyview_process(data,start_frequency,stop_frequency,i)
        run_index+=1
        qt.msleep(0.001)


    
data.close_file()
qt.mend()
#end of normalization routine
