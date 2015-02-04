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

class rigol_dm3058(Instrument):
    '''
    This is the driver for the Rigol DM3058

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'rigol_dm3058',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. rigol= qt.instruments.create('rigol','rigol_dm3058',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the rigol_dm3058, and communicates with the wrapper.

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

        # Add parameters to wrapper
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
# going to use Agilent command set
    def startup(self):
        self._visainstrument.write('cmdset agilent')
    def get_function(self):
        return (self._visainstrument.ask('FUNCtion?'))
    def m_volt_ac(self):
        return self._visainstrument.ask('MEASure:VOLTage:AC?')
    def m_volt_dc(self):
        return self._visainstrument.ask('MEASure:VOLTage:DC?')
    def m_current_ac(self):
        return self._visainstrument.ask('MEASure:CURRent:AC?')
    def m_current_dc(self):
        return self._visainstrument.ask('MEASure:CURRent:DC?')
    def m_2wr(self):
        return self._visainstrument.ask('MEASure:RESistance?')
    def m_4wr(self):
        return self._visainstrument.ask('MEASure:FRESistance?')
    def m_capacitance(self):
        return self._visainstrument.ask('MEASure:CAP?')
    def m_freq(self):
        return self._visainstrument.ask('MEASure:FREQuency?')

    def value(self):
        return self._visainstrument.ask('READ?')

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
    
