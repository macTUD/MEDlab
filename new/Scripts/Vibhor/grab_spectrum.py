import numpy as np
import os
import qt

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'zvb' not in instlist:
    zvb = qt.instruments.create('zvb','RS_ZVB',address='TCPIP::192.168.100.23::INSTR')

qt.mstart()
data = qt.Data(name='grab_spectrum')
data.add_coordinate('frequency [MHz]')
data.add_value('magnitude [dB]')
data.create_file()
data.copy_file('grab_spectrum.py')

zvb.get_all()

zvb.set_trace_continuous(False)#mstart should do this, but...

trace=zvb.get_trace() #actual measurement

    
#convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:
span=zvb.get_span()
start_frequency=zvb.get_start_frequency()
stop_frequency=zvb.get_stop_frequency()

flist=np.linspace(start_frequency,stop_frequency,zvb.get_sweeppoints)

out=[flist,trace]

fsl.set_trace_continuous(True)#mend should do this, but...

plot2d = qt.Plot2D(data, name='measure2D')
data.add_data_point(out[0],out[1])
data.close_file()
qt.mend()

      
        

    
