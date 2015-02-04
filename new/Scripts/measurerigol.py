###########################

print "Program is running"

#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

#Check and install Rigol Multimeter
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'rigol' not in instlist:
    rigol= qt.instruments.create('rigol','rigol_dm3058',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')

print rigol.query('*IDN?')

#start measurement
def mstart(runtime):
    qt.mstart()
    #filename = 'values1_test'
    data = qt.Data(name='test_file1')
    data.add_coordinate('time [s]')
    data.add_value(rigol.get_function()[1:-1]+ ' e-12')
    data.create_file()
    x_vec = 0
    #runtime = 5
    plot=qt.Plot2D(data, name='test_file1', coorddim=0, valdim=1)
    print 'Measure ' + rigol.get_function()[1:-1]
    sleep(2.00)
    rigol.set_disp_off()
    tstart = time()
    while x_vec < runtime:
        x_vec = time()- tstart
        y_vec = float(rigol.value()[13:])*1e12
        data.add_data_point(x_vec,y_vec)
        sleep(0.01) #wait 10 usec
        print x_vec,y_vec
        
    data.close_file()
    qt.mend()
    rigol.set_disp_on()
    print 'finished'
