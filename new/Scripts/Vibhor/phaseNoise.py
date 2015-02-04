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
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables

NumOfLoop=100
rf_power = -10
cw_freq=4.769472498e9
BW = 100000 #Hz
SweepPt=10001
timespan=0.1 # in secs

timedummy=np.linspace(0,timespan,SweepPt)


################################
#      INSTRUMENTS
################################
instlist = qt.instruments.get_instrument_names()
if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)



#measurement information stored in manual in MED instrument
med.set_device('Vibhor ')
med.set_setup('300um device for noise')
med.set_user('Vibhor,')


#####################
#       PNA set up
#####################
#pna.setup()         #check this !!!!!!
#set CW frequency

pna.w('SENS:FOM:RANG:FREQ:CW '+str(cw_freq))
#set power
pna.set_power(rf_power)
#set number of points and sweeptime
pna.set_sweeptime(timespan)
pna.set_sweeppoints(SweepPt)
pna.set_resolution_bandwidth(BW)   #set bandwidth



################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'phaseNoiseOnReso'
data = qt.Data(name=filename)
data.add_coordinate('times',size=NumOfLoop)
data.add_coordinate('time [ms]',size=SweepPt)
data.add_value('Re S21')
data.add_value('Im S21')
data.create_file()
data.copy_file('phaseNoise.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables

#tstart = time()
run_index=0
while (run_index<NumOfLoop):
    trace=[]
    qt.msleep(timespan*3)
    print run_index
    trace=pna.fetch_data(polar=True)
    loopdummy=list(run_index*ones(SweepPt))
    data.add_data_point(loopdummy,timedummy,trace[0],trace[1])

    data.new_block()

    spyview_process(data,0,timespan,run_index)
    run_index+=1
    

data.close_file()
qt.mend()
#end of normalization routine
