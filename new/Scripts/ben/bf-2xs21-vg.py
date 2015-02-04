#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

'''
script uses the pna to measure the S21 within a frequency range
and uses the adwin to set the Gate voltage.
'''

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')
if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')
if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('Device with CNT JLCs')
med.set_setup('BF')
med.set_user('Ben and Sal')


#################################################
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'db-2xs21-vg'
data = qt.Data(name=filename)

data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Probe (Hz)')
data.add_coordinate('Gate [V]')

data.add_value('S21 (Mlog) [dBm]]')
data.add_value('S21 [Phase]')

data.create_file()
data.copy_file('bf-2xs21-vg.py')

########################################################
#Settings:
kHz = 1e3
MHz = 1e6
GHz = 1e9

#dim 1
start_f1= 5*GHz
stop_f1= 7*GHz
pts = 25001
power = -30 #-30dBm = 35uV
bw = (stop_f1-start_f1)/(pts-1) #500e3#1e9/180e3 #expected q factor

#dim 2
start_gate = -4         #gate setting x1
stop_gate = 4           #gate setting x1
gate_multi = 4
#points_gate = 4001
#gate_off= -0.033 #V 'last calibrated on 15-2-2013

#for max resolution:
'''
#optimized for +- 1V gate range unit has a different offset dep. on the mode
start_bit = int(float(start_gate)/float(gate_multi)*3290+32656)
stop_bit = int(float(stop_gate)/float(gate_multi)*3290+32656)
'''
#optimized for +- 4V gate range unit has a different offset dep. on the mode
start_bit = int(float(start_gate)/float(gate_multi)*3290+32741)
stop_bit = int(float(stop_gate)/float(gate_multi)*3290+32741)
points_gate = int((stop_bit-start_bit)/10)+1

#values to be measured
## pre processing of the input settings ##
#step_gate = (stop_gate - start_gate) / points_gate

gbit_list=np.linspace(float(start_bit),float(stop_bit),points_gate)
g_list=np.linspace(float(start_gate),float(stop_gate),points_gate)
f_list=np.linspace(float(start_f1),float(stop_f1),pts)


#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=start_f1,stop_frequency=stop_f1, sweeppoints=pts,bandwidth=bw,level=power)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
pna.sweep() #do one pre-sweep
qt.msleep(sweep_time+10)
# for speed turn off display 
# use 32bit data



#pna.setup_2tone__spectroscopy(cw_freq=cw_frequency, start_freq=start_probe_f, stop_freq=stop_probe_f,sweep_time=sweep_t)



####   EXPERIMENTAL AREA 51  ##########
print 'set experimental stuf set, point averages, ...'
pna.set_averages_off()
#pna.set_averages(25)
#pna.w('SENS:AVER:MODE POIN') #for testing! set averaging mode to points (all chanals) sweep is the other option
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
pna.sweep()
qt.msleep(sweep_time+10)

######################################

'''setup the adwin befor measurement(with a test sweep)'''
print 'prepare ADwin'
adwin.start_process()       #starts the DAC program
adwin.set_rampspeed(1)
adwin.set_DAC_2(0)

adwin.set_DAC_2(float(start_gate)/float(gate_multi))
qt.msleep(4)
########## Print settings ################

print 'Gate points:' + str(points_gate)
print 'step size: '+str((stop_f1-start_f1)/(pts-1)) +' Hz'
print 'bw:' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec):'+str(sweep_time)

##################################################

print 'measurement loop:'

tstart = time()
prev_time=tstart
now_time=0
exp_number = len(g_list)

i=0 #for gate values

for bit_gate in gbit_list:
    gate = g_list[i]
    i=i+1
    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60
    

    print gate, 'estimated ready at:', localtime(tstart+exp_time)[2],'-',localtime(tstart+exp_time)[1],'-',localtime(tstart+exp_time)[0],' ',localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]

    #print str(gate)
    adwin.set_bitwise_DAC_2(int(bit_gate))
    qt.msleep(0.1)
    pna.sweep()
    qt.msleep(sweep_time+0.1)
    trace= pna.fetch_data(polar=True)
    gate_list= list(gate*ones(len(f_list))) #make a list of the same length as the array to be placed into the data file
    data.add_data_point(f_list,gate_list,trace[0],trace[1])
    data.new_block()
    spyview_process(data,start_f1,stop_f1,gate)
    qt.msleep(0.01)
    sweep_time = float(pna.q("SENS1:SWE:TIME?"))
    
    
data.close_file()
qt.mend()

adwin.set_DAC_2(0)


#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2)
#
