import qt
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

recorddc=False

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vbias',lockin,'out2',100,0.0)

if ('vm' not in instlist) and recorddc:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')
    #smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::169.254.247.179')

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
med.set_current_gain(current_gain)

#set frequencies
RF_start=250 #MHz
RF_stop=500 #MHz
RF_step=.1 #MHz

#set voltages
#vbias_fixed=0.001 #V
vgate_start=3 #V
vgate_stop=5 #V
vgate_step=0.1 #V
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
returntozero = True



FM_frequency=1.0*0.6163 #kHz
RF_power=-10 #dBm (Currently with 20dB in attenuation)
FM_deviation=250 #kHz
LF_voltage=1.0 #V (Low to minimize crosstalk to signal channel (yes, it's a problem))
filename='31b2_FM_Vg_sweep'

qt.mstart()
#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the smb
smb.set_RF_state(False)
smb.set_AM_state(False)

smb.set_LF_frequency(FM_frequency)
smb.set_RF_power(RF_power)
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
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate('Gate Voltage (V)')
data.add_value('X (pA)')
data.add_value('Y (pA)')
data.add_value('DC (pA)')
data.create_file()
data.copy_file('FM_Vg_sweep.py')

spyview_process(reset=True)

#Actual sweep
lockin.get_X()
#ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
for vg in arange(vgate_start,vgate_stop+vgate_step,vgate_step):
    ramp(vi,'vgate',vg,sweepstep,sweeptime)
    smb.set_RF_frequency(RF_start)
    qt.msleep(.2)
    for f in arange(RF_start,RF_stop+RF_step,RF_step):
        smb.set_RF_frequency(f)
        qt.msleep(.05)
        if recorddc:
            dc=vm.read()
            dc*=-1e5
        else:
            dc=0
        #x=lockin.get_X() #or Y or R
        #y=lockin.get_Y()
        rawdat=lockin.query('SNAP?1,2')
        datlist=rawdat.split(',')
        x=1e12*float(datlist[0])
        y=1e12*float(datlist[1])
        data.add_data_point(f,vg,x,y,dc)

    print vg    
    data.new_block()
    spyview_process(data,RF_start,RF_stop,vg)
##    for f in arange(RF_stop,RF_start-RF_step,-RF_step):
##        smb.set_RF_frequency(f)
##        qt.msleep(.3)
##        x=lockin.get_X() #or Y or R
##        y=lockin.get_Y()
##        x*=-1e5
##        y*=-1e5
##        data.add_data_point(f,vg,x,y)
##    data.new_block()
##    spyview_process(data,RF_start,RF_stop,vg)

#ramp(vi,'vgate',0,sweepstep,sweeptime)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)
plot2dc = qt.Plot2D(data, name='dccomp', coorddim=0, valdim=4)
plot3Dc = qt.Plot3D(data, name='dc3d', coorddims=(0,1), valdim=4)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')
plot2dc.save_png(filepath=data.get_dir()+'\\'+'plot2dc.png')
plot3Dc.save_png(filepath=data.get_dir()+'\\'+'plot3Dc.png')

#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)

vi.get_vgate()

smb.set_RF_state(False)

data.close_file()

qt.mend()
