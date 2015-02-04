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

# This driver is written by Sal Jua Bosman, Steelelab TU Delft, Kavli institute of Nanoscience, Februari 2013

from instrument import Instrument
import visa
import types
import logging
import numpy

import qt

class Agilent_L4532A(Instrument):
    '''
    This is a driver to Agilent_L4532A digitizer

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'universal_driver',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. any_device= qt.instruments.create('any_device','Agilent_L4532A',address='TCPIP::192.168.1.51::INSTR')
    '''

    def __init__(self, name, address):
        '''
        Initializes the any_device, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
           
        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)

        self.add_parameter('Config_channel_1', flags=Instrument.FLAG_GETSET,units='',
                           type=types.StringType)

        self.add_parameter('Config_channel_2', flags=Instrument.FLAG_GETSET,units='',
                           type=types.StringType)

        self.add_parameter('Rate', flags=Instrument.FLAG_GETSET, units='kS',
                           type=types.FloatType)

        self.add_parameter('Records', flags=Instrument.FLAG_GETSET, units='',minval=1,maxval=1024,
                           type=types.FloatType)

        self.add_parameter('Samples_per_Record', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

        self.add_parameter('Pretrig_Samples_per_Record', flags=Instrument.FLAG_GETSET, units='',
                           type=types.IntType)

        self.add_parameter('Trig_holdoff', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

        self.add_parameter('Trig_delay', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)
        
        self.add_parameter('Trig_arm', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

        self.add_parameter('Trig_source', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

        self.add_parameter('Trig_in_slope', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

        self.add_parameter('Trig_out_event', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

        self.add_parameter('Trig_out_mode', flags=Instrument.FLAG_GETSET, units='',
                           type=types.StringType)

  
        # Add functions to wrapper
        self.add_function('read_voltages')
        self.add_function('fetch_voltages')

        self.add_function('read_records')
        self.add_function('fetch_records')

        self.add_function('read_records_averaged')
     #   self.add_function('fetch_records_averaged')
        
        self.add_function('read_voltages_averaged')
      #  self.add_function('fetch_voltages_averaged')

        self.add_function('abort')

        self.add_function('calculate_acquisition_time')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

# --------------------------------------
#           functions
# --------------------------------------
# going to use Agilent command set
    def startup(self):
        self._visainstrument.write('cmdset agilent')
    def get_function(self):
        return (self._visainstrument.ask('FUNCtion?'))

    def value(self):
        return self._visainstrument.ask('READ?')

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


    def calculate_acquisition_time(self):
        '''Calculates the time to take a record in seconds'''
        rate = self.get_Rate()
        samples_per_record = self.get_Samples_per_Record()
        #records = self.get_Records()

        return float(samples_per_record)/float(rate*1000)
        
    def read_voltages(self, channel):
        '''Retrieves the voltages of the first record, and erases memory'''
        #self._visainstrument.write('INIT')
        trace= self._visainstrument.ask('FETC:WAV:VOLT? (@%s)' %(channel))
        return trace.split(',')

    def read_records(self, channel):
        '''Retrieves the voltages of all the records, and erases memory, stored as a list of records'''
        records = str(int(self.get_Records()))
        #print records
        samples_per_record = int(self.get_Samples_per_Record())
        #print samples_per_record
        #self._visainstrument.write('INIT')
        string = 'FETC:WAV:VOLT? (@' + str(channel) + '), 0, ' + str(samples_per_record) + ', (@1:' + str(records) +')'
        #print string
        trace = self._visainstrument.ask(string)
        trace=trace.split(',')
        rec_list=[]
        rec=[]
        index=0
        for i in trace:
            i = float(i)                
            if(index<samples_per_record):
                rec.append(i)
                index+=1
            else:
                rec_list.append(rec)
                rec=[]
                #now add the current reading to the next record
                rec.append(i)
                index=1
        #add last record to the list
        rec_list.append(rec)
        return rec_list

    def read_voltages_averaged(self,channel):

        return 0

    def read_records_averaged(self, channel):
        '''Retrieves the average of each record, erases the memory, and returns a list of the averages'''
        records=str(int(self.get_Records()))
        samples_per_record = int(self.get_Samples_per_Record())
        #self._visainstrument.write('INIT')
        string = 'FETC:WAV:VOLT? (@' +str(channel) + '),0, ' + str(samples_per_record) + ', (@1:' +str(records) + '),AVER, ' + str(samples_per_record)
        print string
        trace = self._visainstrument.ask(string)
        trace=trace.split(',')
        for i in trace:
            i = float(i)
        return trace
        

    def fetch_voltages(self,channel):

        return 0

    def fetch_records(self,channel):
        return 0  

    def get_average_voltage(self,channel):
        return 0

    def abort(self):
        self._visainstrument.write('ABORT')
        

##    def configure_channel(self,channel, voltage_range, coupling, filter):
##        return self._visainstrument.write

# --------------------------------------
#           parameters
# --------------------------------------

    def do_set_Rate(self,rate):
        '''Sets the rate of the digitizer in kilo-samples per second, allowed values are
        1kS,2kS,5kS,10kS,20kS,50kS,100kS,200kS,500kS,1Ms,2MS,5MS,10MS,20Ms'''
        return self._visainstrument.write('CONF:ACQ:SRAT %s' %(float(rate)*1000))

    def do_get_Rate(self):
        return float(self._visainstrument.ask('CONF:ACQ:SRAT?'))/1000

    def do_set_Records(self,records):
        return self._visainstrument.write('CONF:ACQ:REC %s' %records)

    def do_get_Records(self):
        return self._visainstrument.ask('CONF:ACQ:REC?')

    def do_set_Samples_per_Record(self,samples_per_record):
        return self._visainstrument.write('CONF:ACQ:SCO %s' %samples_per_record)

    def do_get_Samples_per_Record(self):
        return self._visainstrument.ask('CONF:ACQ:SCO?')

    def do_set_Pretrig_Samples_per_Record(self,pretrig_samples):
        '''Can be set to 0 or samples_per_record -4'''
        return self._visainstrument.write('CONF:ACQ:SPR %s' %pretrig_samples)

    def do_get_Pretrig_Samples_per_Record(self):
        return self._visainstrument.ask('CONF:ACQ:SPR?')
    

    def do_get_Config_channel_1(self):
        return self._visainstrument.ask('CONF:CHAN? (@1)')

    def do_set_Config_channel_1(self, settings):
        '''This configures the channel configuration,
        the device supports the following voltage ranges: .25,.5,1,2,4,8,16,32,64,128,256V plus/minus

        the coupling is AC or DC

        the lowpass filters are: LP_200_KHZ, LP_2_MHZ, LP_20_MHZ

        required format: '2.0, AC, LP_200_KHZ

        '''
        return self._visainstrument.write('CONF:CHAN (@1), %s' %settings)

    def do_get_Config_channel_2(self):
        return self._visainstrument.ask('CONF:CHAN? (@1)')

    def do_set_Config_channel_2(self, settings):
        '''This configures the channel configuration,
        the device supports the following voltage ranges: .25,.5,1,2,4,8,16,32,64,128,256V plus/minus

        the coupling is AC or DC

        the lowpass filters are: LP_200_KHZ, LP_2_MHZ, LP_20_MHZ

        required format: '2.0, AC, LP_200_KHZ

        '''
        return self._visainstrument.write('CONF:CHAN (@1), %s' %settings)

    def do_set_Trig_arm(self, trig_arm):
        '''Options are IMMediate, SOFTware, EXTernal, TIMing'''

        return self._visainstrument.write('CONF:ARM:SOUR %s' %trig_arm)


    def do_get_Trig_arm(self):

        return self._visainstrument.ask('CONF:ARM:SOUR?')

    def do_set_Trig_source(self, trig_source):
        '''Options are IMMediate, CHANnel, SOFT, EXT'''

        return self._visainstrument.write('CONF:TRIG:SOUR %s' %trig_source)

    def do_get_Trig_source(self):

        return self._visainstrument.ask('CONF:TRIG:SOUR?')

    def do_set_Trig_in_slope(self,slope):
        '''Options are 'POS' and 'NEG'
        '''
        return self._visainstrument.write('CONF:EXT:INP %s' %slope)

    def do_get_Trig_in_slope(self):

        return self._visainstrument.ask('CONF:EXT:INP?')

##    def do_set_Trig_out_event(self,trig_out):
##
##        return self._visainstrument.write()
##
##    def do_get_Trig_out_vent(self):
##
##        return self._visainstrument.ask()
##
##    def do_set_Trig_out_mode(self,trig_out_mode):
##
##        return self._visainstrument.write()
##
##    def do_get_Trig_out_mode(self):
##
##        return self._visainstrument.ask()
    



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
    
