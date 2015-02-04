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


rf_power = -25
exp_run=50


start_frequency= 3190
stop_frequency= 3290
sweep_points = 1001
sweep_sections = 1

KHz =0.001
zvb_bandwidth = 0.005*KHz

#Dependent Variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points*sweep_sections)
sweep_section_list = np.linspace(start_frequency,stop_frequency,sweep_sections)

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
zvb.set_source_power(rf_power)
zvb.set_resolution_bandwidth(zvb_bandwidth)
zvb.set_sweeppoints(sweep_points)
#zvb.get_all() #get all the settings and store it in the settingsfile
#zvb.set_trace_continuous(False)  


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_vna_hres'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=sweep_points)
data.add_value('S12 [dB]')
#data.add_value('Summed trace ')

data.create_file()
data.copy_file('bf_vna_hres.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
#tstart = time()


while (run_index<exp_run):
    trace=[]
    sweep_section_index=0
    print exp_run

    while(sweep_section_index<sweep_sections):
        print sweep_section_index

        zvb.set_start_frequency(flist[sweep_section_index*sweep_points])
        zvb.set_stop_frequency(flist[(sweep_section_index+1)*sweep_points-1])
        trace.extend(zvb.get_trace())

        sweep_section_index+=1
    
    data.new_block()

    data.add_data_point(flist,trace)
    spyview_process(data,start_frequency,stop_frequency) 
    run_index+=1
    qt.msleep(0.01)


    
data.close_file()
qt.mend()
#end of normalization routine
