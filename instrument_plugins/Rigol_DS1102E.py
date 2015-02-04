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

import qt

class Rigol_DS1102E(Instrument):
    '''
    This is the driver for the Rigol DS1102E digital oscilloscope

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Rigol_DS1102E',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. rigol= qt.instruments.create('rigol','Rigol_DS1102E',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')
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
        self._visainstrument.timeout=10.0
        print 'timeout = %s'% self._visainstrument.timeout
        # Add parameters to wrapper
        self.add_parameter('time_scale',
                            flags=Instrument.FLAG_GETSET,
                            units='s/div', minval=2e-9, maxval=50,
                            type=types.FloatType)
        self.add_parameter('time_offset',
                            flags=Instrument.FLAG_GETSET,
                            units='s', minval=-50, maxval=50,
                            type=types.FloatType)
        self.add_parameter('voltage_scale',
                            flags=Instrument.FLAG_GETSET,
                            units='V/div', channels=(1,2),minval=2e-3, maxval=10e3,
                            type=types.FloatType)
        self.add_parameter('voltage_offset',
                            flags=Instrument.FLAG_GETSET,
                            units='V', channels=(1,2),minval=-40, maxval=40,
                            type=types.FloatType)
        self.add_parameter('memory_depth',
                            flags=Instrument.FLAG_GETSET, type=types.StringType)
        self.add_parameter('waveform_mode',
                            flags=Instrument.FLAG_GETSET, type=types.StringType)
        self.add_parameter('sampling_rate',
                            flags=Instrument.FLAG_GET,
                            units='Sa/s', channels=(1,2),type=types.FloatType)



        # Add functions to wrapper
        #self.add_function('set_mode_volt_ac')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        if reset:
           self._visainstrument.write('*RST')
           self._visainstrument.write('DISP OFF')
        #else:
           # self.get_all()
           # self.set_defaults()

        
        

# --------------------------------------
#           functions
# --------------------------------------


    def get_trace(self,source):
        if source not in ['CHAN1','CHAN2','DIG','MATH','FFT']:
            print "Source not in ['CHAN1','CHAN2','DIG','MATH','FFT']"



        timeoutoccurred=True #tends to timeout at times, just try again
        while timeoutoccurred:
            try:

                timescale = self.get_time_scale()
                timeoffset = self.get_time_offset()
                if source == 'CHAN1':
                    voltagescale =self.get_voltage_scale1()
                    voltageoffset=self.get_voltage_offset1()
                    samplingrate = self.get_sampling_rate1()
                elif source == 'CHAN2':
                    voltagescale =self.get_voltage_scale2()
                    voltageoffset=self.get_voltage_offset2()
                    samplingrate = self.get_sampling_rate2()
                    
                memorydepth = self.get_memory_depth() 
                waveformmode = self.get_waveform_mode()
                #waveformsource = self.get_waveform_source()

                #stringdata =self._visainstrument.read()
                stringdata =self._visainstrument.ask(':WAV:DATA? '+source)
                timeoutoccurred=False
            except visa.VisaIOError:
                print 'Timeout occurred, try again'
                

        stringdatalength=len(stringdata)
        print 1, stringdatalength

        if stringdatalength <= 610:
            if (waveformmode == 'RAW') & (source in ['CHAN1','CHAN2','DIG']):
                databig=True
                print 'heri'
                #The first time you request a 'big' trace, you will get a small one anyway. This repeats the query.
                
                timeoutoccurred=True
                while timeoutoccurred:
                    try:
                        #stringdata =self._visainstrument.read()
                        #self.run()
                        qt.msleep(1)
                        print 'bla'
                        stringdata =self._visainstrument.ask(':WAV:DATA? '+source)
                        timeoutoccurred = False
                    except visa.VisaIOError:
                        print 'Timeout occurred, try again'
                    
                print 2, len(stringdata)
                bytedata=bytearray(stringdata)[10:]
            else:
                databig=False
                #The first 10 points need to be removed.
                bytedata=bytearray(stringdata)[10:]
        else:
            databig=True
            bytedata=bytearray(stringdata)[10:]    
        print bytedata[0:100]
        print 3, len(bytedata)
        

        numberdata = array.array('l',bytedata)

        
        datalength=len(numberdata)
        print 4, datalength
        indexdata = numpy.linspace(1,datalength,datalength)

        amplitude = [(240 - nd) * (voltagescale / 25) - (voltageoffset + voltagescale * 4.6) for nd in numberdata]
        if databig:
            time = [(ind-1)/samplingrate for ind in indexdata]
        else:
            time = [(ind - 1) * (timescale / 50) - ((timescale * 6) -0* timeoffset) for ind in indexdata]

        
        
        return time,amplitude


    def do_get_time_scale(self):
        return self._visainstrument.ask(':TIM:SCAL?')

    def do_set_time_scale(self,value):
        self._visainstrument.write(':TIM:SCAL '+ "%3.9f" % value)

    def do_get_time_offset(self):
        return self._visainstrument.ask(':TIM:OFFS?')

    def do_set_time_offset(self,value):
        self._visainstrument.write(':TIM:OFFS '+ "%3.9f" % value)


    def do_get_voltage_scale(self,channel):
        return self._visainstrument.ask(':CHAN'+str(channel)+':SCAL?')

    def do_set_voltage_scale(self,value,channel):
        self._visainstrument.write(':CHAN'+str(channel)+':SCAL '+str(value))

    def do_get_voltage_offset(self,channel):
        return self._visainstrument.ask(':CHAN'+str(channel)+':OFFS?')

    def do_set_voltage_offset(self,value,channel):
        self._visainstrument.write(':CHAN'+str(channel)+':OFFS '+str(value))

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

    def run(self):
            self._visainstrument.write(':RUN')
    def stop(self):
            self._visainstrument.write(':STOP')         
        
    def set_disp_on(self):
        self._visainstrument.write('disp on')
    def set_disp_off(self):
        self._visainstrument.write('disp off')
    def read(self):
        self._visainstrument.read()
    def write(self,string):
        self._visainstrument.write(string)
    def query(self,string):
        return self._visainstrument.ask(string)
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
    
