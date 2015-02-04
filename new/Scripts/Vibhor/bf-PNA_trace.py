#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
#execfile('metagen3D_crazy.py')
execfile('metagen.py')

    
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')
if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('W6_NG_withDrum')
med.set_setup('BF')
med.set_user('Vibor, Ben, Sal, Gary')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'S21'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_value('S21 [abs]')
data.add_value('S21 [to be checked Phase]')
data.create_file()
data.copy_file('bf-PNA_trace.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature
# Gate = 0
#13 mK

pow_start=0
hanger_f0=7*GHz
hanger_span = 4000*MHz
f1_pts = 5001
f1_bw = 100 #HZ


f1_start= hanger_f0-hanger_span/2
f1_stop= hanger_f0+hanger_span/2


########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))

#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
# for speed turn off display 
# use 32bit data

####   EXPERIMENTAL AREA  ##########
print 'set experimental stuf, point averages, ...'
pna.set_averages_off()
#pna.set_averages(4)
#pna.w('SENS:AVER:MODE POIN') #for testing! set averaging mode to points (all chanals) sweep is the other option

#do a PNA testsweep
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
#pna.sweep()

######################################

########## Print settings ################

print 'step size: '+str((f1_stop-f1_start)/(f1_pts-1)) +' Hz'
print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec): '+str(sweep_time)

##################################################

print 'measurement loop:'

tstart = time()
prev_time=tstart
now_time=0
pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
pna.sweep()
qt.msleep(sweep_time+10)
trace= pna.fetch_data(polar=True)
data.add_data_point(f_list,trace[0],trace[1]) #for S21 vs power only     
spyview_process(data,f1_start,f1_stop,1)
qt.msleep(0.01)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
data.close_file()
qt.mend()
