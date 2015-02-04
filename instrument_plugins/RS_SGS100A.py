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


##################################
## QTlab driver written by Sal J Bosman
## Steelelab-MED-TNW-TU Delft
## contact: s.bosman@tudelft.nl or saljuabosman@mac.com
##################################

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

class RS_SGS100A(Instrument):
    '''
    This is a RS_SGS100A driver to control the R&S SGS 100A

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'universal_driver',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. any_device= qt.instruments.create('any_device','RS_SGS100A',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')
                                                                            address='TCPIP::192.168.100.21::INSTR'
    '''

    def __init__(self, name, address, reset=False):
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

        # Add parameters to wrapper

        #State parameters (turn on/off instrument states)
        self.add_parameter('RF_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        
        #Measurement parameters
        self.add_parameter('RF_frequency',
                            flags=Instrument.FLAG_GETSET,
                            units='MHz', minval=0.009, maxval=12750,
                            type=types.FloatType)
        self.add_parameter('RF_power',
                            flags=Instrument.FLAG_GETSET,
                            units='dBm', minval=-110, maxval=30,
                            type=types.FloatType)
        self.add_parameter('RF_phase',
                           flags=Instrument.FLAG_GETSET,
                           units='degrees',minval=-720,maxval=720,
                           type=types.FloatType)
        self.add_parameter('reference',
                           flags=Instrument.FLAG_GETSET,
                           type=types.StringType)


        # Add functions to wrapper

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        self.add_function('reset')
        #self.add_function('get_all')

        if reset:
            self.reset()
        else:
            self.get_all()
            
# --------------------------------------
#           functions
# --------------------------------------
    def reset(self):
        '''
        Reset device to factory settings
        '''
        self._visainstrument.write('*RST')

    def get_all(self):
        '''
        Read all implemented parameters
        '''
        
        self.get_RF_power()
        self.get_RF_phase()
        self.get_RF_state()
        self.get_RF_frequency()

    def do_get_RF_frequency(self):
        '''
        Read RF frequency in MHz
        '''
	return float(self._visainstrument.ask('FREQ?'))/1e6

    def do_set_RF_frequency(self,frequency):
        '''
        Set RF frequency in MHz
        '''
        return self._visainstrument.write('FREQ %sMHz' % frequency)

    def do_get_RF_power(self):
        '''
        Read RF power in dBm
        '''
	return self._visainstrument.ask('POW?') # in dBm

    def do_set_RF_power(self,power):
        '''
        Set RF power in dBm
        '''
        return self._visainstrument.write('POW %s' % power) # in dBm
	
    def do_get_RF_state(self):
        '''
        Read RF state (False=OFF & TRUE=ON)
        '''
	return bool(int(self._visainstrument.ask('OUTP?')))

    def do_set_RF_state(self, state):
        '''
        Turn ON/OFF RF output input a Bool
        '''
        state=bool_to_str(state)
        return self._visainstrument.write('OUTP %s' % state)

    def do_get_RF_phase(self):
        '''
        Read relative phase to reference clock
        '''
        return float(self._visainstrument.ask('PHAS?'))

    def do_set_RF_phase(self,phase):
        '''
        Set relative phase to reference clock
        '''
        return self._visainstrument.write('PHAS %s' % phase)


    def do_get_reference(self):
        return self._visainstrument.ask('ROSC:SOUR?')

    def do_set_reference(self,value): #kHz
        if value != 'INT' and value != 'EXT':
            print "Allowed values are: 'INT', 'EXT'"
        return self._visainstrument.write('ROSC:SOUR ' + value)


    
    def write(self,string):
        '''
        Write string to device
        '''
        self._visainstrument.write(string)
        
    def query(self,string):
        '''
        Query device something
        '''       
        return self._visainstrument.ask(string)
    

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
    
