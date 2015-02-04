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

class flux_bias_control(Instrument):
    '''
    This is a virtual instrument to control the flux bias (magnet) of a transmon/DC squid

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'universal_driver',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. any_device= qt.instruments.create('any_device','universal_driver',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')
                                                                             address='TCPIP::192.168.100.21::INSTR'
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
        Instrument.__init__(self, name, tags=['virtual'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)

        # Add parameters to wrapper

        self.add_parameter('start_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz', minval=10e6, maxval=13500e6)





         
        # Add functions to wrapper
        self.add_function('set_mode_volt_ac')

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
##    def m_volt_ac(self):
##        return self._visainstrument.ask('MEASure:VOLTage:AC?')


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
    
