import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

# Cavity drive at 5.525 GHz @ -20dBm at source
start_frequency= 11
stop_frequency= 101
sweep_points = 501
rf_power=18

fsv_center_frequency=5525 # Unit is MHZ here
fsv_span= 200 #MHz Wait tim emay have to adjusted if this number is changed
fsv_sweep_points = 2001
fsv_BW=30e-6

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.102::inst0::INSTR')
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.1.25::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('W6NG')
med.set_setup('BF,fsv,smb')
med.set_user('Vibhor,Ben')

print smb.query('*IDN?')
print fsv.query('*IDN?')


#SMB 100A instrument
#smb.reset()
smb.set_RF_power(rf_power)
smb.set_RF_frequency(start_frequency)
smb.set_RF_state(True)

#fsv.reset()
fsv.set_center_frequency(fsv_center_frequency)
fsv.set_span(fsv_span)
fsv.set_resolution_bandwidth(fsv_BW)
fsv.set_sweeppoints(fsv_sweep_points)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_smb-fsv-1'
data = qt.Data(name=filename)
data.add_coordinate('smb freq',size=sweep_points)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')

data.create_file()
data.copy_file('bf_smb-fsv-1.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)

fsv_start=float(fsv_center_frequency)-float(fsv_span)
fsv_stop=float(fsv_center_frequency)+float(fsv_span)
fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)

print 'Start Experiments'

waittime=fsv.get_sweeptime()


for freq in flist:
    freq_dummy=list(freq*ones(fsv_sweep_points))
    smb.set_RF_frequency(freq)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current drive frequency ',freq
    qt.msleep(waittime+2)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(freq_dummy,fsv_list,tr)
    spyview_process(data,fsv_start,fsv_stop,freq)


data.close_file()
qt.mend()
#end
