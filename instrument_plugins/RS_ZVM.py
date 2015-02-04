# This driver is incomplete, some of the commands are missing. 


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

import qt

def bool_to_str(val):
    '''
    Function to convert boolean to 'ON' or 'OFF'
    '''
    if val == True:
        return "ON"
    else:
        return "OFF"

class RS_ZVM(Instrument):
    '''
    This is the driver for the Rohde & Schwarz FSL spectrum analyzer

    Usage:
    Initialize with
    <name> = qt.instruments.create('<name>', 'RS_ZVB',
        address='TCPIP::<IP-address>::INSTR',
        reset=<bool>,)

    For GPIB the address is: 'GPIB::<gpib-address>'
    '''
        
    
    def __init__(self, name, address, reset=False):
        '''
        Initializes a R&S FSL, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Rohde & Schwarz FSL spectrum analyzer')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)

        # Add parameters to wrapper

        self.add_parameter('start_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz', minval=0.009, maxval=20000)
        self.add_parameter('stop_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz', minval=0.009, maxval=20000)
        self.add_parameter('sweeppoints', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='', minval=101, maxval=10000)
        self.add_parameter('averages', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',minval=0, maxval=32767)
        self.add_parameter('resolution_bandwidth', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz')
        self.add_parameter('sweeptime', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='s')
        self.add_parameter('source_power', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='dBm')
        self.add_parameter('trace_continuous', type=types.BooleanType,
                          flags=Instrument.FLAG_GETSET,
                          units='')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        self.add_function('reset')
        #self.add_function('get_all')
        
        if reset:
            self.reset()


# --------------------------------------
#           functions
# --------------------------------------

    def reset(self):
        return self._visainstrument.write('*RST') #reset to default settings

    #def get_all(self):

    def get_trace(self):
        self._visainstrument.write('INIT;*WAI')
        return eval('[' + self._visainstrument.ask('TRAC? CH1DATA') + ']')

    def grab_trace(self):
        #self._visainstrument.write('INIT;*WAI')
        return eval('[' + self._visainstrument.ask('TRAC? CH1DATA') + ']')
      
    def do_get_start_frequency(self): #in MHz
        '''
        Start of sweep (MHz)
        '''
        logging.debug('Reading start frequency')
        return float(self._visainstrument.ask('SENS:FREQ:STAR?'))/1e6

    def do_get_stop_frequency(self): #in MHz
        '''
        End of sweep (MHz)
        '''
        logging.debug('Reading stop frequency')
        return float(self._visainstrument.ask('SENS:FREQ:STOP?'))/1e6

    def do_get_sweeppoints(self):
        '''
        Number of points in frequency
        '''
        logging.debug('Reading sweep points')
        return int(self._visainstrument.ask('SENS:SWE:POIN?'))


    def get_flist(self):
        self._visainstrument.write('INIT;*WAI')
        return eval('[' + self._visainstrument.ask('TRAC:STIM? CH1DATA') + ']')

    

    def do_get_averages(self):
        '''
        Number of averages per sweep. 0 is default and 32767 is max.
        '''
        logging.debug('Reading number of averages')
        return int(self._visainstrument.ask('AVER:COUN?'))

    def do_get_resolution_bandwidth(self): #in MHz
        logging.debug('Reading resolution bandwidth')
        return float(self._visainstrument.ask('BAND?'))/1e6

    def do_get_sweeptime(self):
        logging.debug('reading sweeptime')
        return float(self._visainstrument.ask('SWE:TIME?'))


    def do_get_source_power(self):
        logging.debug('Reading Source power')
        return float(self._visainstrument.ask('SOUR:POW?'))


    def do_set_start_frequency(self, start): #in MHz
        logging.debug('Setting start freq to %s' % start)
        return self._visainstrument.write('FREQ:STAR %s MHz' % start)

    def do_set_stop_frequency(self, stop): #in MHz
        logging.debug('Setting stop freq to %s' % stop)
        return self._visainstrument.write('FREQ:STOP %s MHz' % stop)

    def do_set_sweeppoints(self,sweeppoints):
        logging.debug('Setting sweep points to %s' % sweeppoints)
        return self._visainstrument.write('SWE:POIN %s' % sweeppoints)

    def do_set_averages(self, averages):
        logging.debug('Setting number of averages to %s' % averages)
        return self._visainstrument.write('AVER:COUN %s' % averages)

    def do_set_resolution_bandwidth(self,resolution_bandwidth): #in MHz
        '''
        Don't set too low (see FSL). Can be manually set up to 10MHz.
        Note that video BW is automatically kept at 3x reolution BW
        It can be change manually on the FSL or using 'BAND:VID %sMHz'
        '''
        logging.debug('Setting Resolution BW to %s' % resolution_bandwidth)
        return self._visainstrument.write('BAND %sMHz' % resolution_bandwidth)
    

    def do_set_sweeptime(self, sweeptime): #in seconds
        logging.debug('Setting sweeptime to %s' % sweeptime)
        return self._visainstrument.write('SWE:TIME %ss' % sweeptime)

    def do_set_source_power(self, source_power): #in dBm
        '''
        Can be set to 0,-10,-20,-30 dBm. on 18GHz FSL
        For 3GHz FSL 1 dBm increments between 0 and -20dBm
        Default is -20dBm
        

        Note: calibration should be done at instrument.
        Details such as power offset can also be adjusted at instrument (op manual p. 294)
        '''
        logging.debug('Setting tracking generator power to %s' % source_power)
    #    if self.get_tracking()==False:
     #       print 'Source off since not in tracking mode. Will be at %sdBm.' % source_power
        return self._visainstrument.write('SOUR:POW %s dBm' % source_power)
    
    def do_get_trace_continuous(self):
        logging.debug('Getting trace_continuous state')
        return bool(int(self._visainstrument.ask('INIT:CONT?')))

    def do_set_trace_continuous(self, state):
        logging.debug('setting trace_continuous to %s' % state)
        state=bool_to_str(state)
        return self._visainstrument.write('INIT:CONT %s' % state)


    
        
    def write(self,string):
        self._visainstrument.write(string)

    def query(self,string):
        return self._visainstrument.ask(string)






# --------------------------------------
#           Internal Routines
# --------------------------------------

    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''
        #self.set_trace_continuous(False) #switch to single trace mode
        #self.get_all()

    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
        #self.set_trace_continuous(True) #turn continuous back on
    
