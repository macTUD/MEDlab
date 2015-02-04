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
RF_start=161 #MHz
RF_stop=171 #MHz
RF_step=.05 #MHz

RF_power_stop=-24
RF_power_start=4.2#dBm (Currently actually 30dBm less due to attenuation)
RF_power_step=-.1

vg=3.6 #V
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

FM_frequency=.6163 #kHz
FM_deviation=125 #kHz
LF_voltage=1.0 #V (Low to minimize crosstalk to signal channel (yes, it's a problem))
filename='33-C1_4K_FM_Power_sweep_bidirectional'

qt.mstart()
#ready the lockin
lockin.get_all()
ramp(vi,'vgate',vg,sweepstep,sweeptime)
vi.get_vgate()

#ready the smb
smb.set_RF_state(False)
smb.set_AM_state(False)

smb.set_LF_frequency(FM_frequency)
smb.set_RF_power(RF_power_start)
smb.set_FM_deviation(FM_deviation)
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
data.add_coordinate('RF Power [dBm]')
data.add_value('X [pA]')
data.add_value('Y [pA]')
data.add_coordinate('direction (bool)')
data.create_file()
data.copy_file('FMpowersweep.py')

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
#plot2dy = qt.Plot2D(data, name='ycomp', coorddim=0, valdim=3)
plot3D = qt.Plot3D(data, name='measure3D', coorddims=(0,1), valdim=2)
spyview_process(reset=True)
#Actual sweep

for db in arange(RF_power_start,RF_power_stop+RF_power_step,RF_power_step):
    smb.set_RF_power(db)
    qt.msleep(1)
    lockin.get_X()
    lockin.get_X()
    for f in arange(RF_start,RF_stop+RF_step,RF_step):
        smb.set_RF_frequency(f)
        qt.msleep(.3)
        x=lockin.get_X() #or Y or R
        y=lockin.get_Y()
        x*=-1e5
        y*=-1e5
        data.add_data_point(f,db,x,y,0)
    data.new_block()
    spyview_process(data,RF_start,RF_stop,db)
    for f in arange(RF_stop,RF_start-RF_step,-RF_step):
        smb.set_RF_frequency(f)
        qt.msleep(.3)
        x=lockin.get_X() #or Y or R
        y=lockin.get_Y()
        x*=-1e5
        y*=-1e5
        data.add_data_point(f,db,x,y,1)
    data.new_block()
    spyview_process(data,RF_start,RF_stop,db)

#ramp(vi,'vgate',0,sweepstep,sweeptime)

data.close_file()

qt.mend()

