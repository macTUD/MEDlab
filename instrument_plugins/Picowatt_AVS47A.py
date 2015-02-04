# Picowatt_AVS47A.py driver for Picowatt AVS-47A resistance bridge
# Harold Meerwaldt <H.B.Meerwaldt@tudelft.nl>, 2012
#
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

class Picowatt_AVS47A(Instrument):
    '''
    This is the driver for the Picowatt AVS-47A resistance bridge

    Physically flip the 'start/print' switch in case writing fails

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Picowatt_AVS47A',
        address='<GBIP address>',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the Picowatt_AVS47A, and communicates with the wrapper.

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
        logging.info('Initializing instrument Picowatt_AVS47A')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)

        # Add parameters to wrapper
        #self.add_parameter('range',
        #    flags=Instrument.FLAG_GETSET,
        #    units='', minval=0.1, maxval=1000, type=types.FloatType)
        
        # Add functions to wrapper
##        self.add_function('set_mode_volt_ac')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        #if reset:
           # self.reset()
        #else:
           # self.get_all()
           # self.set_defaults()

        self._visainstrument.write('ADC')
        

# --------------------------------------
#           functions
# --------------------------------------

    def get_resistance(self):
        return self._visainstrument.ask('RES?')
        
    def write(self,string):
        self._visainstrument.write(string)

    def query(self,string):
        return self._visainstrument.ask(string)

# --------------------------------------
#           parameters
# --------------------------------------



# --------------------------------------
#           Internal Routines
# --------------------------------------

    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''
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
    
