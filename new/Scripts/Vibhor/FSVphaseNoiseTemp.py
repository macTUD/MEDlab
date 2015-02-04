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
#      INSTRUMENTS
################################
instlist = qt.instruments.get_instrument_names()
if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.102::inst0::INSTR')
if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.1.50::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


# VARIABLES
power=3
loops=25
cw_freq=4.769472498*1000 #MHZ
BW = 5*1e-6       #MHz
SweepPt=20001
span=0.1# MHz
markersize=100
#markerlist=np.linspace(10,100000,SweepPt)
markerlist=np.logspace(1,4.5,markersize)

# DATA INITIALIZATION
qt.mstart()
spyview_process(reset=True) #clear old meta-settings
filename = 'phase_noise'
data = qt.Data(name=filename)
data.add_coordinate('Delta log [Hz]',size=len(markerlist))
data.add_coordinate('times [s]',size=loops)
data.add_value('Phase noise [dBc/Hz]')
data.create_file()
data.copy_file('FSVphaseNoiseTemp.py')

#Set freq, span, bw, points
smb.set_RF_power(power)
smb.set_RF_frequency(cw_freq)
smb.set_RF_state(True)
fsv.set_center_frequency(cw_freq)
fsv.set_span(span)
fsv.set_resolution_bandwidth(BW)
fsv.set_sweeppoints(SweepPt)
##fsv.write('AVER:STAT ON;*WAI')
##fsv.write('INIT:CONT OFF;*WAI') #activate averages...
##fsv.write('AVER:COUN 16;*WAI') #average 16 x
##fsv.write('AVER:TYPE LIN;*WAI') #aver lin then log

#measurement loop
i = 0
while i < loops:
    fsv.write('INIT:CONT ON')
    qt.msleep(3)
    fsv.write('INIT:CONT OFF')
    
    i=i+1
    timelist=list(i*ones(len(markerlist)))
    phaselist=[]
    for delt2 in markerlist:
        fsv.write('CALC:DELT2:X '+str(delt2)+';*WAI') #set delta position
        phase = float(fsv.query('CALC:DELT2:FUNC:PNO:RES?;*WAI')) # get phase value
        phaselist.append(phase)
    data.add_data_point(timelist,markerlist,phaselist)
    data.new_block()
    spyview_process(data,markerlist[0],delt2,i)

data.close_file()
qt.mend()


























#####################
#       PNA set up
#####################
#pna.setup()         #check this !!!!!!
#set CW frequency


#fsv.write('INIT:CONT ON')

##fsv.write('AVER OFF;*WAI')
##
##fsv.write('CALC:MARK1 ON;*WAI') #switch mar 1 on
##fsv.write('CALC:MARK1:X '+str(cw_freq*1e6)+';*WAI') #set mar 1
##print 'Setting WAIT'
##qt.msleep(5)
##
###fsv.write('CALC:MARK1:FUNC:REF;*WAI') #set the reference right
##fsv.write('CALC:MARK2 ON;*WAI') #switch mar 2 on
##fsv.write('CALC:MARK2:FUNC:NOIS ON;*WAI') #activate noise measurement

##
##fsv.write('INIT:CONT ON;*WAI') # setting continuous ON
##qt.msleep(fsv.get_sweeptime()+2)
##fsv.write('INIT:CONT OFF;*WAI') # seeting continuous OFF
##
##
####  NOW WE ARE READY TO GRAB DATA
##
###fsv.write('CALC:DELT:FUNC:PNO:AUTO ON')
##
###fsv.write('CALC:MARK2:X 0MHz;*WAI') #set mar 2
#fsv.write('CALC:DELT2:X 0MHz;*WAI') #set mar 2




