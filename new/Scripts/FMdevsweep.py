import qt
from time import time
import numpy as np
execfile('ramp.py')

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

##if 'smb' not in instlist:
##    #smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::30::INSTR')
##    smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::169.254.247.179')
##    
##if 'lockin' not in instlist:
##    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')
##
##if 'vi' not in instlist:
##    vi = qt.instruments.create('vi','virtual_composite')
##    vi.add_variable_scaled('vgate',lockin,'out1',0.25,0.0)

###Measurement
RF_start=320 #MHz
RF_stop=340 #MHz
RF_step=.2 #MHz

FM_dev_start=500 #kHz
FM_dev_stop=0 #kHz
FM_dev_step=-20

vg=4 #V
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

FM_frequency=.6163 #kHz
RF_power=17 #dBm (-30dB atten)
LF_voltage=0.3 #V (Low to minimize crosstalk to signal channel (yes, it's a problem))
filename='23-A3_FM_dev_sweep'

qt.mstart()
#ready the lockin
lockin.get_all()
ramp(vi,'vgate',vg,sweepstep,sweeptime)
vi.get_vgate()

#ready the smb
smb.set_RF_state(False)
smb.set_AM_state(False)

smb.set_LF_frequency(FM_frequency)
smb.set_RF_power(RF_power)
smb.set_FM_deviation(FM_dev_start)
smb.set_RF_frequency(RF_start)
smb.set_LF_output_voltage(LF_voltage)

smb.set_LF_output_state(True)
smb.set_FM_state(True)
smb.set_Modulation_state(True)
smb.set_RF_state(True)

smb.get_all()

#Set up datafile

data = qt.Data(name=filename)
data.add_coordinate('RF frequency [MHz]')
data.add_coordinate('FM Deviation [kHz]')
data.add_value('X [pA]')
data.add_value('Y [pA]')
data.create_file()
data.copy_file('FMdevsweep.py')

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
#plot2dy = qt.Plot2D(data, name='ycomp', coorddim=0, valdim=3)
plot3D = qt.Plot3D(data, name='xcomp over deviation', coorddims=(0,1), valdim=2)

#Actual sweep
spyview_process(reset=True)
for dev in arange(FM_dev_start,FM_dev_stop+FM_dev_step,FM_dev_step):
    smb.set_FM_deviation(dev)
    qt.msleep(1)
    for f in arange(RF_start,RF_stop+RF_step,RF_step):
        smb.set_RF_frequency(f)
        qt.msleep(.3)
        x=lockin.get_X() #or Y or R
        y=lockin.get_Y()
        x*=-1e5
        y*=-1e5
        data.add_data_point(f,dev,x,y)
    data.new_block()
    spyview_process(data,RF_start,RF_stop,dev)

#ramp(vi,'vgate',0,sweepstep,sweeptime)

data.close_file()

qt.mend()

