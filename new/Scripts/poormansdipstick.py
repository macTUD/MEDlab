#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

#Check and load instrument plugins
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
med.set_user('Ben and Sal')


print rigol.query('*IDN?')

# 'start measurement'
#def measure_temp_fsl(start_frequency, stop_frequency, runtime):

start_frequency= 1000
stop_frequency= 2000
bandwidth = 0.1 #MHz
runtime = 10 #sec

qt.mstart()
spyview_process(reset=True) #clear old meta-settings
filename = 'fsl_temp_sec'

print 'prepare datafile'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)',size=fsl.get_sweeppoints())
data.add_coordinate('time [s]')
data.add_value('RF Power (dBm)')
data.add_value('Temp (K)')
#data.add_value(rigol.get_function()[1:-1]+ ' ') #whatever rigol is set to
#data.add_coordinate('temp [K]')
data.create_file()
data.copy_file('poormansdipstick.py')

print 'prepare FSL'
#required preperation stuff (FSL)
fsl.reset()
fsl.set_start_frequency(start_frequency)
fsl.set_stop_frequency(stop_frequency)
span=stop_frequency-start_frequency
fsl.set_resolution_bandwidth(bandwidth)
#fsl.set_averages(100)
fsl.get_all() #get all the settings and store it in the settingsfile

#time variable
x_time = 0
    
print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2)

print 'Measure with Rigol: ' + rigol.get_function()[1:-1]
sleep(1.00)
rigol.set_disp_off()
fsl.set_trace_continuous(False)    
tstart = time()

print 'measurement loop:'
while x_time < runtime:
    x_time = time()- tstart
    y_temp = (float(rigol.value()[13:])-221.47)/0.23377+4.2 #temperature converted to [K] (cal by Vibhor)
    trace=fsl.get_trace() #FSL measurement
    time_list = x_time*ones(len(trace))   #make list
    temp_list = y_temp*ones(len(trace))   #make list

    fstep=span/(len(trace)-1.0) #calc correct freq. step
    flist=np.arange(start_frequency,stop_frequency+fstep,fstep) #create freq. list
    data.new_block()
    data.add_data_point(flist,time_list,trace,temp_list) #store data
    spyview_process(data,start_frequency,stop_frequency,x_time) 
    qt.msleep(0.01) #wait 10 usec so save etc

    print x_time,y_temp

data.close_file()
qt.mend()

fsl.set_trace_continuous(True)
rigol.set_disp_on()
