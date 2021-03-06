#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen3D_crazy.py')
#execfile('metagen.py')

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

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('Device with CNT JLCs')
med.set_setup('BF')
med.set_user('Vibor, Ben, Sal')


qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'S21_pow_Vg'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Hanger IDX')
data.add_coordinate('Power [dBm]')
data.add_value('S21 [abs]')
data.add_value('S21 [to be checked Phase]')
data.create_file()
data.copy_file('bf-s21-pow-fset_v3.py')


####Settings:
kHz = 1e3
MHz = 1e6
GHz = 1e9

#dim 3
#power in dBm first, adding a V option later
pow_start= -30
pow_stop= 20
pow_pts = 6

#dim 2
hanger_idx = np.array([4.472492,4.6162757,4.7694742,4.9326,5.1067165,5.29134,5.4936,5.71142,5.94614,6.20106,6.49,6.80174])*GHz #here you enter the center freqs.
#hanger_idx = np.array([6.80174])*GHz #here you enter the center freqs.
hanger_span = 1*MHz #this is the span for each cent. freq.
f1_pts = 2000
f1_bw = 50          #float(f1_stop-f1_start)/float(f1_pts) #500e3#1e9/180e3 #expected q factor

#dim 1

f1_start= hanger_idx[0]-hanger_span/2
f1_stop= hanger_idx[0]+hanger_span/2


########### making lists of values to be measured ###########
#f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
f_list=np.linspace(float(-hanger_span/2),float(hanger_span/2),(f1_pts))
pow_list=np.linspace(float(pow_start),float(pow_stop),(pow_pts))


#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
#pna.sweep() #do one pre-sweep
#qt.msleep(sweep_time+10)
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
exp_number = len(g_list)
f1_power = -30
j = 0
for f1_power in pow_list:
    power_list= list(f1_power*ones(len(f_list))) #make a list of the same length as the array to be placed into the data file
    pna.set_power(f1_power)
    qt.msleep(0.1)
    j = j +1

    for f_idx in hanger_idx:
        f1_start= f_idx -hanger_span/2
        f1_stop= f_idx+hanger_span/2
        pna.set_start_frequency(f1_start)
        pna.set_stop_frequency(f1_stop)
        
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time
        exp_time = exp_number*time_int*(len(pow_list)-j)
        if exp_time<0:
            exp_time = 60

        print f1_power,'Pow [dBm] ',f_idx, 'Freq idx', localtime(tstart+exp_time)[2],'-',localtime(tstart+exp_time)[1],'-',localtime(tstart+exp_time)[0],' ',localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]

        qt.msleep(0.1)
        pna.sweep()
        qt.msleep(sweep_time+0.1)
        trace= pna.fetch_data(polar=True)
        fidx_list= list(f_idx*ones(len(f_list))) 
        data.add_data_point(power_list,fidx_list,f_list,trace[0],trace[1]) #for S21 vs power only
        data.new_block()
        
        spyview_process(data,-hanger_span/2,hanger_span/2,hanger_idx[0],f_idx,f1_power)
        qt.msleep(0.01)
        sweep_time = float(pna.q("SENS1:SWE:TIME?"))
        
data.close_file()
qt.mend()



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
