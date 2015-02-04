#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
#execfile('metagen3D.py')
execfile('metagen.py')

'''
script uses the pna to measure the S21 within a frequency range
and uses the adwin to set the Gate voltage.
'''

#def dBm_W(dBm):
#    return math.pow(10,float((dBm-30))/float(10)) #Convert dBm to W
#def W_V(W):
#    return math.sqrt(W*50)     #asuming 50 Ohm stripline W=I*V I=V*R > W= R*V*V 
#def dBm_V(dBm,R):
#    return math.sqrt(math.pow(10,float((dBm-30))/float(10))*R)
    
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
med.set_user('Vibor, Ben ')


qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'S21_pow_Vg'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
#data.add_coordinate('Gate [V]')
data.add_coordinate('Power [dBm]')
data.add_value('S21 (Mlog) [dBm]]')
data.add_value('S21 [Phase]')
data.create_file()
data.copy_file('bf-s21-vg.py')


####Settings:
kHz = 1e3
MHz = 1e6
GHz = 1e9

#dim 1
f1_start= 6.198*GHz
f1_stop= 6.204*GHz
f1_pts = 25000
f1_bw = float(f1_stop-f1_start)/float(f1_pts) #500e3#1e9/180e3 #expected q factor

#dim 2
gate_start = 0         #gate setting x1
gate_stop = 0           #gate setting x1
gate_multi = 4          #enter here the S1d multiplier(1 or 4)
gate_bitstep = 1      #number of bits to jump per step 1bit = 0.304mV * (S1d multiplier)

#optimized for +- 4V gate range unit has a different offset dep. on the mode
start_bit = int(float(gate_start)/float(gate_multi)*3290+32741)
stop_bit = int(float(gate_stop)/float(gate_multi)*3290+32741)
gate_pts = int((stop_bit-start_bit)/gate_bitstep) #telling to step by chaning the bit value
'''
#optimized for +- 1V gate range unit has a different offset dep. on the mode
start_bit = int(float(gate_start)/float(gate_multi)*3290+32656)
stop_bit = int(float(gate_stop)/float(gate_multi)*3290+32656)
'''

#dim 3
#power in dBm first, adding a V option later
pow_start= -30
pow_stop= -30
pow_pts = 1


########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts+1))
gbit_list=np.linspace(float(start_bit),float(stop_bit),(gate_pts+1)) # is used to step the gate voltage bitwise
g_list=np.linspace(float(gate_start),float(gate_stop),(gate_pts+1)) # is now used to map the correct voltage value in the data file
pow_list=np.linspace(float(pow_start),float(pow_stop),(pow_pts+1))

#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts+1),bandwidth=f1_bw,level=pow_start)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
pna.sweep() #do one pre-sweep
qt.msleep(sweep_time+10)
# for speed turn off display 
# use 32bit data

####   EXPERIMENTAL AREA 51  ##########
print 'set experimental stuf, point averages, ...'
pna.set_averages_off()
#pna.set_averages(1)
#pna.w('SENS:AVER:MODE POIN') #for testing! set averaging mode to points (all chanals) sweep is the other option

#do a PNA testsweep
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
pna.sweep()
qt.msleep(sweep_time+3)

######################################

'''setup the adwin befor measurement(with a test sweep)'''
print 'prepare ADwin'
adwin.start_process()       #starts the DAC program
adwin.set_rampspeed(1)
#adwin.set_DAC_2(0)
#adwin.set_DAC_2(float(gate_start)/float(gate_multi)) #set adwin to start value
qt.msleep(2) #wait for adwin and equilibrium
########## Print settings ################

print 'Gate points:' + str(gate_pts+1)
print 'step size: '+str((f1_stop-f1_start)/(f1_pts)) +' Hz'
print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec): '+str(sweep_time)

##################################################

print 'measurement loop:'

tstart = time()
prev_time=tstart
now_time=0
exp_number = len(g_list)
f1_power = -30
j = 0
for f1_power in pow_list:
    power_list= list(f1_power*ones(len(f_list))) #make a list of the same length as the array to be placed into the data file
    pna.set_power(f1_power)
    qt.msleep(0.1)
    j = j +1
    i=0 #for gate values

    for bit_gate in gbit_list:
        gate = g_list[i]
        i=i+1

        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time
        exp_time = exp_number*time_int*(len(pow_list)-j)
        if exp_time<0:
            exp_time = 60

        print f1_power,'Pow [dBm] ', gate,'Vg [V] estimated ready at:', localtime(tstart+exp_time)[2],'-',localtime(tstart+exp_time)[1],'-',localtime(tstart+exp_time)[0],' ',localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
        #adwin.set_bitwise_DAC_2(int(bit_gate))
        qt.msleep(0.1)
        pna.sweep()
        qt.msleep(sweep_time+0.1)
        trace= pna.fetch_data(polar=True)
        gate_list= list(gate*ones(len(f_list))) #make a list of the same length as the array to be placed into the data file
        #data.add_data_point(f_list,gate_list,power_list,trace[0],trace[1])
        data.add_data_point(f_list,power_list,trace[0],trace[1]) #for S21 vs power only
        data.new_block()
        #spyview_process(data,f1_start,f1_stop,gate_start,gate_stop,pow_start,f1_power)
        spyview_process(data,f1_start,f1_stop,int(f1_power))
        qt.msleep(0.01)
        sweep_time = float(pna.q("SENS1:SWE:TIME?"))
        
data.close_file()
qt.mend()
#adwin.set_DAC_2(0) #set dac_2 back to 0


#Metavalues, a quite simplified script to replace this buggy meta file maker...
'''
'#loop1'
len(f_list)
f1_start
f1_stop
Frequency (Hz) #better get name from coordinate...
'#loop2'
len(g_list)
gate_start
gate_stop
Gate [V]
'#loop3'
len(pow_list)
pow_start
f1_power
Power [dBm]
#values
4
S21 (Mlog) [dBm]]
'''
