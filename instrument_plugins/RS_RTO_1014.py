# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import visa
import types
import logging
import numpy
import copy
import array
from struct import unpack

import qt

class RS_RTO_1014(Instrument):
    '''
    This is the driver for the Rigol DS1102E digital oscilloscope

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'RS_RTO_1014',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. HFoscil= qt.instruments.create('HFoscil','RS_RTO_1014',address='TCPIP0::169.254.22.230::inst0::INSTR')
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the Rigol_DS1102E, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
            change_display (bool)   : If True (default), automatically turn off
                                        display during measurements.
            change_autozero (bool)  : If True (default), automatically turn off
                                        autozero during measurements.
        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Rigol DM3058')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self._visainstrument.timeout=1
        print 'timeout = %s'% self._visainstrument.timeout
        # Add parameters to wrapper

        self.add_parameter('time_resolution',
                            flags=Instrument.FLAG_GETSET,
                            units='s', minval=1e-15, maxval=0.5,
                            type=types.FloatType)
        self.add_parameter('time_scale',
                            flags=Instrument.FLAG_GETSET,
                            units='s/div', minval=2e-9, maxval=50,
                            type=types.FloatType)
        self.add_parameter('record_length',
                            flags=Instrument.FLAG_GETSET,
                            units='', minval=1000, maxval=1e9,
                            type=types.IntType)
        self.add_parameter('time_position',
                            flags=Instrument.FLAG_GETSET,
                            units='s', minval=-500, maxval=500,
                            type=types.FloatType)
        self.add_parameter('time_offset',
                            flags=Instrument.FLAG_GETSET,
                            units='s', minval=-50, maxval=50,
                            type=types.FloatType)
        self.add_parameter('voltage_scale',
                            flags=Instrument.FLAG_GETSET,
                            units='V/div', channels=(1,4),minval=2e-3, maxval=10e3,
                            type=types.FloatType)
        self.add_parameter('voltage_position',
                            flags=Instrument.FLAG_GETSET,
                            units='div', channels=(1,4),minval=-5, maxval=5,
                            type=types.FloatType)        
        self.add_parameter('voltage_offset',
                            flags=Instrument.FLAG_GETSET,
                            units='V', channels=(1,4),minval=-40, maxval=40,
                            type=types.FloatType)
        self.add_parameter('memory_depth',
                            flags=Instrument.FLAG_GETSET, type=types.StringType)
        self.add_parameter('waveform_mode',
                            flags=Instrument.FLAG_GETSET, type=types.StringType)
        self.add_parameter('sampling_rate',
                            flags=Instrument.FLAG_GET,
                            units='Sa/s', channels=(1,4),type=types.FloatType)



        # Add functions to wrapper
        #self.add_function('set_mode_volt_ac')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        self._visainstrument.write('FORM REAL,32')
        self._visainstrument.write('EXP:WAV:INCX OFF')
        

        if reset:
           self._visainstrument.write('*RST')
           self._visainstrument.write('DISP OFF')
        #else:
           # self.get_all()
           # self.set_defaults()

        
        

# --------------------------------------
#           functions
# --------------------------------------

    def _get_trace_internal(self,source):
        #getting a comma-separated string of alternating time and amplitude values:
        #make a flat list of alternating floats for time and amplitude:
        #convert flat list into two arrays:
        datastring=self._visainstrument.ask('CHAN%s:WAV1:DATA?'%int(source))
        datalist = map(float,datastring.split(","))
        dataarray = numpy.transpose(zip(*[iter(datalist)]*2))
        return dataarray #timearray,amplitudearray        
        

    def get_trace_double(self,source):
        timearray,amplitudearray=self._get_trace_internal(source)
        return timearray,amplitudearray

    def get_ACQavai(self):
        return self._visainstrument.ask('ACQuire:AVAilable?')

    def get_rawtrace(self,source):
        '''
        just returns the bare output
        '''
        return self._visainstrument.ask('CHAN'+str(source)+':WAV1:DATA?')

    def separate(self,values):
        '''
        only works for an even number of values
        for b   array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        transpose(b.reshape(5,2))
        b  array([[0, 2, 4, 6, 8],[1, 3, 5, 7, 9]])
        '''
        reshaped=numpy.reshape(values,((len(values)/2),2))
        return numpy.transpose(reshaped)
        
    def decode_bit32(self,bit32):
        i = 0
        a = 0 #numpy.zeros(10)
        c = 0
        for i in bit32[1:]:
            c=c+1
            try:
                eval(i)
            except (KeyboardInterrupt, SystemExit):
                raise
            except: #catch errors
                a = c
                break
        if c == 1:
            print 'Error in bit32 format'
            #return bit32
        
        c = eval(bit32[2:a])/4 #eval(bit32[1]) #calc size and form of data
        c = int(c)
        datastring = unpack('f'*c,bit32[a:]) #decode the data
        return numpy.array(datastring)

        
    def get_trace(self,source,wave=1,npoints=1000):
        '''
        #can be used in contin. mode, clear_buffer command and averaging.
        #where the sleeping time determines how many averages it can do meanwhile...
        #i.e.
        #.run_continuous()
        #.clear_buffer()
        #msleep(5)
        
        '''
        bit32 = self._visainstrument.ask('CHAN'+str(source)+':WAV'+str(wave)+':DATA?')
        #if len(bit32) < npoints:
        #    qt.msleep(0.010)
        #    bit32 = self._visainstrument.ask('CHAN'+str(source)+':WAV1:DATA?')
        #return self.decode_bit32(bit32)
        #certainly works within limits:
        a=int(len(str(npoints*4))+2)
        datastring = unpack('f'*npoints,bit32[a:])
        return numpy.array(datastring)
    
    def set_decimation(self,channel,decimation='SAMP'):
        ''' select channel set decimation:
        ->       options are: SAMPle | PDETect | HRESolution | RMS
        SAMPle
        One of n samples in a sample interval of the ADC is recorded as
        waveform point.
        PDETect
        Peak Detect: the minimum and the maximum of n samples in a
        sample interval are recorded as waveform points.
        HRESolution
        High resolution: The average of n sample points is recorded as
        waveform point.
        RMS
        The waveform point is the root mean square of n sample values.
        '''
        self._visainstrument.write('CHAN'+str(channel)+':TYPE '+str(decimation)) 
    def set_ben_settings(self):
        #only displ final avg results
        #self._visainstrument.write('ACQuire:SEGMented:AUToreplay OFF') #not yet working as device needs to be updated...
        #self.w('EXPort:WAVeform:SCOPe WFM') #Defines the part of the waveform record to be stored
        #self.w('EXPort:WAVeform:MULTichannel OFF') #disable multichanel exports
        #self.w('EXPort:WAVeform:SOURce C2W1')
        #self.w('EXPort:WAVeform:SOURce C3W1')
        #tell it to only send Y-values only (time is known)
        self._visainstrument.write('EXPort:WAVeform:INCXvalues OFF')
        #turn digital filters off
        self._visainstrument.write('CHANnel1:DIGFilter:STATe OFF')
        self._visainstrument.write('CHANnel2:DIGFilter:STATe OFF')
        self._visainstrument.write('CHANnel3:DIGFilter:STATe OFF')
        self._visainstrument.write('CHANnel4:DIGFilter:STATe OFF')
        #set to High resolution average, Pdetect envelope and RMS aquisition waves:
        #enable channels and waveforms:
        #CHANnel<m>[:WAVeform<n>][:STATe] #ON /OFF
        self._visainstrument.write('CHAN2:WAV1:STAT ON')
        self._visainstrument.write('CHAN2:WAV2:STAT OFF')
        self._visainstrument.write('CHAN2:WAV3:STAT OFF')
        self._visainstrument.write('CHAN3:WAV1:STAT ON')
        self._visainstrument.write('CHAN3:WAV2:STAT OFF')
        self._visainstrument.write('CHAN3:WAV3:STAT OFF')
        #1 HRES
        #2 Envelope
        #3 RMS
        self._visainstrument.write('CHAN2:WAV1:TYPE HRES') #SAMPle | PDETect | HRESolution | RMS
        #self._visainstrument.write('CHAN2:WAV1:TYPE SAMP') #SAMPle | PDETect | HRESolution | RMS
        #self._visainstrument.write('CHAN2:WAV2:TYPE PDET') #SAMPle | PDETect | HRESolution | RMS
        #self._visainstrument.write('CHAN2:WAV3:TYPE RMS') #SAMPle | PDETect | HRESolution | RMS
        self._visainstrument.write('CHAN3:WAV1:TYPE HRES')
        #self._visainstrument.write('CHAN3:WAV1:TYPE SAMP')
        #self._visainstrument.write('CHAN3:WAV2:TYPE PDET')
        #self._visainstrument.write('CHAN3:WAV3:TYPE RMS')
        #set type of averages:
        #self.set_average(self,source,number,wave=1,parameter='AVER'):
        #<TrArith> OFF | ENVelope | AVERage
        self.set_average(2,5000,wave=1,parameter='AVER')
        self.set_average(3,5000,wave=1,parameter='AVER') #Aver HRES points.
        #self.set_average(2,5000,wave=2,parameter='ENV')
        #self.set_average(3,5000,wave=2,parameter='ENV') #envelope PDET
        #self.set_average(2,5000,wave=3,parameter='AVER') #use average RMS
        #self.set_average(3,5000,wave=3,parameter='AVER')

        
        #self.run_continuous()
        self.set_format('REAL,32') #set 32bit format
        self.clear_buffer() #clear buffer

       
        '''  Use with Care!
        Commands being send:
        EXPort:WAVeform:INCXvalues OFF #disable time axis only Voltage values
        FORM REAL,32 #set to 32bit data, 64bit default
        EXP:WAV:INCX OFF
        CHAN1:WAV1:DATA?

        R&S RTO1044 can work with double maximum realtime sample rate. This high sample rate is achieved by interleaving two channels:
        channel 1 and 2 are interleaved, and also channel 3 and 4. Interleaving assumes that
        only one of the paired channels can be used - either channel 1 or channel 2, and either
        channel 3 or 4.
        Using a channel on R&S RTO oscilloscopes is more than displaying it. In the background,
        without displaying the channel, it can serve as trigger source, as source of a math waveform,
        cursor or automatic measurement. As soon as the second channel of a pair is used
        in one way or another, the interleaving mode is disabled and the realtime sample rate is
        limited to the usual value of 10 GSa/s.
        
        '''
    def set_exttrigger(self):
        ''' optional sets the trigger to external
        trigger level
        trigger position
        '''
        self.w('TRIG:SOUR EXT') #external source
        self.w('TRIG:TYPE ANED') #analog edge
        self.w('TRIG:LEV5 -0.9') #set trig level to -0.9
        self.w('TRIG:EDGE:SLOP NEG') #set the slope to negative
        self.w('TRIGger:MODE NORM') #set trigger mode to normal
    def set_trigger_pos(self,number):
        '''
        sets the triger position in time [sec]
        Defines the trigger offset
        - the time interval between trigger point and reference
        point to analize the signal some
        time before or after the trigger event.
        number Range: -500 to 500
        Increment: 0.01
        *RST: 0
        Default unit: s
        '''
        #self._visainstrument.write('TIMebase:POSition ' +str(number))
        self._visainstrument.write('TIMebase:HORizontal:POSition ' +str(number))
        
    def clear_buffer(self):
        '''
        I am using 3 different command:
        1. clear status registers
        2. send a trigger command
        3 clear buffer and AQS numbers
        '''
        self._visainstrument.write('*CLS') #clear status registers (delete old data )
        #self._visainstrument.write('*TRG') #send a triger command
        self._visainstrument.write('ACQ:ARES:IMM')#clears the buffer and AQS number
        #qt.msleep(0.001)
        #self._visainstrument.write('ACQuire:ARESet:IMMediate') #clear buffer
        #self._visainstrument.write('ACQuire:COUNt ' +str(number))
        
    def get_avg_trace(self,source,wave=1,npoints=1000):
        '''
        to start a trace use
        run_single() before
        then run this command it waits until it is finished..
        this waits until the machine finised the given set of averages
        (Try OPC until it give 1)
        then it returns the values
        '''
        #check until machine sends a ready signal
        a = 0
        while a == 0:
            try:
                a = eval(self.a('*OPC?'))
                break
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                a = 0
        qt.msleep(0.003)
        return self.get_trace(source,wave,npoints) #catch data from the machine

    def trigger_average(self):
        self._visainstrument.write('ACQuire:ARESet:IMMediate')

    def set_average(self,source,number,wave=1,parameter='AVER'):
        '''
        For now to keep things simple I use
        waveform 1 for an average waveform,
        2 for the envelope (with PDET) and
        3 for RMS values with (sample)
        activates the averaging mode for a channel with a given number of averages:
        use: i.e. set_average(2,10,state='ON') #activates 10x averaging on channel 2
        set_average(2,1,state='OFF') #turns the averaging off again...
        '''
        self._visainstrument.write('ACQuire:COUNt ' +str(number))
        self._visainstrument.write('CHAN'+str(source)+'WAV'+str(wave)+':ARIT '+str(parameter))
        '''
        Parameters:
        <TrArith> OFF | ENVelope | AVERage
        OFF
        The data of the current acquisition is recorded according to the
        decimation settings.
        ENVelope
        Detects the minimum and maximum values in an sample interval
        over a number of acquisitions. To define the reset method, use ...
        AVERage
        Calculates the average from the data of the current acquisition and
        a number of acquisitions before. To define the number of acquisitions,
        use ACQuire: COUNt .
        '''
        #this stuff is for averaging FFT data
        #self._visainstrument.write('CHAN'+str(number)+':WAV'+str(number)+':ARIT AVER')
        #self._visainstrument.write('CALCulate:MATH'+str(source)+':STAT '+str('ON')) 
        #self._visainstrument.write('CALCulate:MATH%s:ARIThmetics AVER'%int(source))
                                        
        
    def set_format(self,FORMAT='REAL,32'):
        ''' ASCii is just lame!
        FORMat[:DATA] <Format>, [<Length>]
        <Format>,[<Length>] ASC,0=ASCii | REAL,32 | INT,8
        '''
        self._visainstrument.write('FORMat:DATA '+FORMAT)

    def get_format(self): 
        return self._visainstrument.ask('FORMat:DATA?')

    def get_header(self,source,wave=1):
        '''Position Meaning Example
        1 XStart in s -9.477E-008 = - 94,77 ns
        2 XStop in s 9.477E-008 = 94,77 ns
        3 Record length of the waveform in Samples 200000
        4 Number of values per sample interval. For most
        waveforms the result is 1, for peak detect and envelope
        waveforms it is 2. If the number is 2, the number
        of returned values is twice the number of samples
        (record length).'''
        return eval(self._visainstrument.ask('CHAN'+str(source)+':WAV'+str(wave)+':DATA:HEAD?'))
    
    def get_header_calc(self,source):
        '''Position Meaning Example
        1 XStart in s -9.477E-008 = - 94,77 ns
        2 XStop in s 9.477E-008 = 94,77 ns
        3 Record length of the waveform in Samples 200000
        4 Number of values per sample interval. For most
        waveforms the result is 1, for peak detect and envelope
        waveforms it is 2. If the number is 2, the number
        of returned values is twice the number of samples
        (record length).'''
        return  eval(self._visainstrument.ask('CALCulate:MATH3:DATA:HEADer?'))
    def set_autoscale(self,channel):
        ''' Calibrates the scaling fro one axis,
        offsets the channel position to 0
        '''
        header= self.get_header(channel)
        self._visainstrument.write('CHAN'+str(channel)+':POS '+str(0))
        self._visainstrument.write('CHAN'+str(channel)+':SCAL '+str(1))
        trace = self.get_trace(channel,header[2])
        min_v=trace.min()
        max_v=trace.max()
        range_v = abs(max_v - min_v)
        offset_v= min_v + (max_v - min_v)/2
        newscale = (range_v/10)*3 #set the scale to 25% of the display
        round(newscale,2)
        self._visainstrument.write('CHAN'+str(channel)+':SCAL '+str(newscale))
        #self.do_set_voltage_scale(offset_v,channel)
            
    def do_get_time_resolution(self):
        return self._visainstrument.ask('ACQ:RES?')

    def do_set_time_resolution(self,value):
        self._visainstrument.write('ACQuire:POINTS:AUTO RES') #allow setting of time resolution
        self._visainstrument.write('ACQ:RES %s' % value)

    def do_get_record_length(self):
        return self._visainstrument.ask('ACQ:POIN?')

    def do_set_record_length(self,value):
        self._visainstrument.write('ACQuire:POINTS:AUTO RECL') #allow setting of record length
        self._visainstrument.write('ACQuire:POINts %s' % value)

    def do_get_time_scale(self): #time range is 10*time_scale
        return self._visainstrument.ask('TIM:SCAL?')

    def do_set_time_scale(self,value):
        self._visainstrument.write('TIM:SCAL %s' % value)

    def do_get_time_position(self):
        return self._visainstrument.ask('TIM:POS?')

    def do_set_time_position(self,value):
        self._visainstrument.write('TIM:POS %s' % value)        

    def do_get_voltage_scale(self,channel):
        return self._visainstrument.ask('CHAN'+str(channel)+':SCAL?')

    def do_set_voltage_scale(self,value,channel):
        self._visainstrument.write('CHAN'+str(channel)+':SCAL '+str(value))

    def do_get_voltage_position(self,channel): 
        return self._visainstrument.ask('CHAN'+str(channel)+':POS?')

    def do_set_voltage_position(self,value,channel): #moves waveform up and down screen in divisions != voltage offset
        self._visainstrument.write('CHAN'+str(channel)+':POS '+str(value))

    def run_continuous(self):
            self._visainstrument.write('RUN')
    def run_single(self):
            self._visainstrument.write('RUNS')
    
    def stop(self):
            self._visainstrument.write('STOP')  

    def r(self):
        self._visainstrument.read()
    def w(self,string):
        self._visainstrument.write(string)
    def a(self,string):
        return self._visainstrument.ask(string)
#leftovers from Rigol scope:


    def do_get_voltage_offset(self,channel):
        return self._visainstrument.ask('CHAN'+str(channel)+':OFFS?')

    def do_set_voltage_offset(self,value,channel):
        self._visainstrument.write('CHAN'+str(channel)+':OFFS '+str(value))

    def do_get_time_offset(self):
        return self._visainstrument.ask('TIM:OFFS?')

    def do_set_time_offset(self,value):
        self._visainstrument.write(':TIM:OFFS '+ "%3.9f" % value)  

    def do_get_memory_depth(self):
        return self._visainstrument.ask(':ACQuire:MEMDepth?') #you cannot use the abbreviations for this command!

    def do_set_memory_depth(self,value):
        if value not in ['LONG','NORMAL']:
            print "memory depth not in ['LONG','NORMAL']"
        self._visainstrument.write(':ACQuire:MEMDepth '+value)

    def do_get_waveform_mode(self):
        return self._visainstrument.ask(':WAV:POIN:MODE?')

    def do_set_waveform_mode(self,value):
        if value not in ['NORMAL','MAXIMUM','RAW']:
            print "waveform mode not in ['NORMAL','MAXIMUM','RAW']"
        self._visainstrument.write(':WAV:POIN:MODE '+value)        

    def do_get_sampling_rate(self,channel):
        return self._visainstrument.ask(':ACQ:SAMP? CHAN'+str(channel))

       
        
    def set_disp_on(self):
        self._visainstrument.write('disp on')
    def set_disp_off(self):
        self._visainstrument.write('disp off')

        #it sends visa.instrument(adress).ask(string)     ben
    #def conf_volt_dc(self,number):
    #    return self._visainstrument.write('CONFigure:VOLTage:DC DEF, %s' % (number))
    #def conf_volt_ac(self,number):
    #    return self._visainstrument.write('CONFigure:VOLTage:AC DEF, %s' % (number))
    

# --------------------------------------
#           parameters
# --------------------------------------



# --------------------------------------
#           Internal Routines
# --------------------------------------
#
    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''
#        #set correct commandset
#        self._visainstrument.write('cmdset agilent')
#        return self._visainstrument.write('*IDN?')
##        if self._change_display:
##            self.set_display(False)
##            #Switch off display to get stable timing
##        if self._change_autozero:
##            self.set_autozero(False)
##            #Switch off autozero to speed up measurement

    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
##        if self._change_display:
##            self.set_display(True)
##        if self._change_autozero:
##            self.set_autozero(True)
    
