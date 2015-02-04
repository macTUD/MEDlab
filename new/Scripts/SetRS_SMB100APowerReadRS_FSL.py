from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
import copy


###########################
# Make instances available
###########################

print "Program is running"

import qt


instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')

if 'keithley1' not in instlist:
    keithley1 = qt.instruments.create('keithley1','Keithley_2700',address='GPIB0::16::INSTR')

if 'keithley2' not in instlist:    
    keithley2 = qt.instruments.create('keithley2','Keithley_2700',address='GPIB0::17::INSTR')

#if 'picowatt' not in instlist:    
    #picowatt = qt.instruments.create('picowatt','Picowatt_AVS47A',address='GPIB0::20::INSTR')

if 'specana' not in instlist:    
    specana = qt.instruments.create('specana','RS_FSL',address='GPIB0::22::INSTR')

if 'siggen' not in instlist:    
    siggen = qt.instruments.create('siggen','RS_SMB100A',address='GPIB0::29::INSTR')

ivvi.set_dac_multiplier(8,4)

keithley1.set('IVVI_gain',0.01)


def sweep_power_measure_trace(xstart=-100,xend=-60,Nx=10,drivefrequency=11,centerfrequency=11,span=2,Nrepeat=1, nplc=1, plotting=True,title=''):
#x = RF power of signal generator    
    qt.mstart()
    filename = 'test'

    Ny = specana.get_sweep_points()
        
    data = qt.Data(name=filename)
    data.add_coordinate('Frequency (MHz)',size=Ny)
    data.add_coordinate('RF Power (dBm)',size=Nx)
    data.add_value('Spectral power (dBm)')
    data.create_file()
    
   

    
   
    x_vec=linspace(xstart,xend,Nx)

    siggen.switch_on()
    siggen.set_frequency(drivefrequency)
    specana.set_center_frequency(centerfrequency)
    specana.set_span(span)

    
    
    for cnt in range(Nrepeat):
        for xcnt,x_sweep in enumerate(x_vec):
            print 'power #%s' % (xcnt+1)
            siggen.set_power(x_sweep)
            sleep(2)
            Vtrace = specana.get_trace() # value trace           
            xtrace = x_sweep*ones(len(Vtrace))
            ytrace = linspace(centerfrequency-span/2,centerfrequency+span/2,len(Vtrace)) # frequency trace
            
            data.new_block()            
            data.add_data_point(ytrace,xtrace,Vtrace)

    siggen.switch_off()
            
    print 'RFPower from %s dBm to %s dBm at %s MHz in %s steps' % (xstart,xend,drivefrequency,Nx)    

    if plotting:
        #plot2d = qt.Plot2D(data, name=filename)
        plot3d = qt.Plot3D(data, name=filename)
        
    if plotting:
        #plot2d.save_png()
        plot3d.save_png()

    data._write_settings_file()

    data_array = data.get_data()

    data.close_file()
    qt.mend()    

def sweep_dac_measure_keithley(channel =1, xstart=-100,xend=-60,Nx=100, Nrepeat=1, plotting=True,title='',returntozero=True):
#x = dac

    #where to add general measurement data

    
    qt.mstart()
    filename = 'test'
    multiplier = ivvi.get_dac_multiplier(channel)

    data = qt.Data(name=filename)
    if channel == 1:
        xname = 'Bias voltage (mV)'
    elif channel == 2:
        xname = 'Gate voltage (mV)'
    else:
        xname = 'dac%s'%channel
        
    data.add_coordinate(xname,size=Nx)

    a = keithley1.get_parameter_options('IVVI_gain')
    curryes=a['curryes']
    if curryes:  #is current measured or voltage?
        data.add_value('Current (pA)')
    else:
        data.add_value('Voltage (mV)')
        
    data.create_file()
    
   

    
   
    x_vec=linspace(xstart,xend,Nx)

      
    
    for cnt in range(Nrepeat):
        for xcnt,x_sweep in enumerate(x_vec):
            ivvi.set('dac%s'%channel,x_sweep)
            y_sweep = keithley1.get_readlastval()
            data.add_data_point(x_sweep,y_sweep)

                
    print xname + ' from %s mV to %s mV in %s steps' % (multiplier*xstart,multiplier*xend,Nx)    

    if plotting:
        plot2d = qt.Plot2D(data, name=filename)
        #plot3d = qt.Plot3D(data, name=filename)
        
    if plotting:
        plot2d.save_png()
        #plot3d.save_png()

    data._write_settings_file()

    data_array = data.get_data()

    data.close_file()
    qt.mend()    

    if returntozero:
        set_dacs_to_zero()

def stability_diagram(channel1 =1, xstart=-100,xend=-60,Nx=10, channel2=2, ystart=-100,yend=-60,Ny=10, Nrepeat=1, plotting=True,title='',returntozero=True):
    #x = dac channel1 (sweep)
    #y = dac channel2 (loop1)

    #where to add general measurement data?

    
    qt.mstart()
    filename = 'test'
    multiplier1 = ivvi.get_dac_multiplier(channel1)
    multiplier2 = ivvi.get_dac_multiplier(channel2)

    data = qt.Data(name=filename)
    if channel1 == 1:
        xname = 'Bias voltage (mV)'
    elif channel1 == 2:
        xname = 'Gate voltage (mV)'
    else:
        xname = 'dac%s'%channel1
        
    data.add_coordinate(xname,size=Nx)


    if channel2 == 1:
        yname = 'Bias voltage (mV)'
    elif channel2 == 2:
        yname = 'Gate voltage (mV)'
    else:
        yname = 'dac%s'%channel2
        
    data.add_coordinate(yname,size=Ny)


    a = keithley1.get_parameter_options('IVVI_gain')
    curryes=a['curryes']
    if curryes:  #is current measured or voltage?
        data.add_value('Current (pA)')
    else:
        data.add_value('Voltage (mV)')
        
    data.create_file()
    
   

    
   
    x_vec=linspace(xstart,xend,Nx)
    y_vec=linspace(ystart,yend,Ny)
      
    
    for cnt in range(Nrepeat):
        for ycnt,y_sweep in enumerate(y_vec):
            print ycnt
            ivvi.set('dac%s'%channel2,y_sweep)
            
            for xcnt,x_sweep in enumerate(x_vec):
                ivvi.set('dac%s'%channel1,x_sweep)
                z_sweep = keithley1.get_readlastval()
                data.add_data_point(y_sweep,x_sweep,z_sweep)

            data.new_block()
                            
    print xname + ' from %s mV to %s mV in %s steps' % (multiplier1*xstart,multiplier1*xend,Nx)
    print yname + ' from %s mV to %s mV in %s steps' % (multiplier2*ystart,multiplier2*yend,Ny)    

    if plotting:
        #plot2d = qt.Plot2D(data, name=filename)
        plot3d = qt.Plot3D(data, name=filename)
        
        
    if plotting:
        #plot2d.save_png()
        plot3d.save_png()

    data._write_settings_file()

    data_array = data.get_data()
    print data_array
    cnt2=0
    deltax=(float(xend)-xstart)/(Nx-1)

    datastabdiag = qt.Data(name='test2')
    if channel1 == 1:
        xname = 'Bias voltage (mV)'
    elif channel1 == 2:
        xname = 'Gate voltage (mV)'
    else:
        xname = 'dac%s'%channel1
        
    datastabdiag.add_coordinate(xname,size=Nx)


    if channel2 == 1:
        yname = 'Bias voltage (mV)'
    elif channel2 == 2:
        yname = 'Gate voltage (mV)'
    else:
        yname = 'dac%s'%channel2
       
    datastabdiag.add_coordinate(yname,size=Ny)
    datastabdiag.add_value('dI/dV (pA/mV)')

    datastabdiag.create_file()


    #datastabdiag_array=zeros(data_array.shape)+1.5

    print type(data)
    print type(datastabdiag)

    cnt2=0
    print deltax
    for cnt in range(Nrepeat):
        for ycnt,y_sweep in enumerate(y_vec):
            for xcnt,x_sweep in enumerate(x_vec):
                
                if xcnt != Nx-1:   #stability diagram has same size as original data, with last line double, gnuplot doesn't plot last/first line anyway
                    z_sweep=(data_array[cnt2+1][2]-data_array[cnt2][2])/deltax
                print xcnt, z_sweep, type(z_sweep)
                datastabdiag.add_data_point(y_sweep,x_sweep,z_sweep)
                cnt2=cnt2+1
            datastabdiag.new_block()
            
 

    plotstabdiag = qt.Plot3D(datastabdiag, name='test')

    print datastabdiag.get_data()
    
    data.close_file()
    qt.mend()    

    if returntozero:
        set_dacs_to_zero()
