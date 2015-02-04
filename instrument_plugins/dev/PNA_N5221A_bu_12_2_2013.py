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
## QTlab driver written by Ben S.
## Steelelab-MED-TNW-TU Delft
## contact: b.h.schneider@tudelft.nl
##################################


from instrument import Instrument
import visa
import types
import logging
import numpy

import qt

class PNA_N5221A(Instrument):
    '''
    This is a general multi purpose driver to write & read queries with a VISA machine

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
        logging.info('Initializing instrument Agilent PNA_N5221A')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)

        # Add parameters to wrapper

        self.add_parameter('start_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz', minval=10e6, maxval=13500e6)
        self.add_parameter('stop_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz', minval=10e6, maxval=13500e6)
        self.add_parameter('sweeppoints',
                           flags=Instrument.FLAG_GETSET,
                           units=' ', minval=0, maxval=25000,
                           type=types.FloatType)
        self.add_parameter('sweeptime',
                           flags=Instrument.FLAG_GET,
                           units='sec',
                           type=types.FloatType)
        self.add_parameter('resolution_bandwidth', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='MHz')
        self.add_parameter('averages', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',minval=0, maxval=32767)
        

        # Add functions to wrapper
        self.add_function('abort')
        self.add_function('read')
        self.add_function('write')
        self.add_function('query')
        self.add_function('reset')
        self.add_function('get_all')
        

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

# --------------------------------------
#           functions
# --------------------------------------

    def value(self):
        return self._visainstrument.ask('READ?')
    def read(self):
        self._visainstrument.read()
    def write(self,string):
        self._visainstrument.write(string)
    def query(self,string):
        return self._visainstrument.ask(string)
    def reset(self):
        self._visainstrument.write('SYST:FPReset')
        #Preset the analyzer

    def abort(self):
        self._visainstrument.write('ABORT')

    def get_all(self):
        self.get_sweeppoints()
        self.get_start_frequency()
        self.get_stop_frequency()
        self.get_averages()
        self.get_resolution_bandwidth()
        #self.get_resolution_bandwidth_auto()
        #self.get_filter_type()
        self.get_sweeptime()
        #self.get_tracking()
        #self.get_source_power()
        #self.get_trace_continuous()



    def data_ascii(self):
        self._visainstrument.write("format:data ascii")
    def data_32bit(self):
        self._visainstrument.write("FORM REAL,32")
    def data_64bit(self):
        self._visainstrument.write("FORM REAL,64")
    def data_s(self):
        return self._visainstrument.ask("CALCulate:DATA? SDATA") # 'Corrected, Complex Meas
    def data_f(self):
        return self._visainstrument.ask("CALCulate:DATA? FDATA") #'Formatted Meas
    def data_fmem(self):
        return self._visainstrument.ask("CALCulate:DATA? FMEM") #'Formatted Memory

    def set_averages_on(self):
        self._visainstrument.write('SENS:AVER 1')
    def set_averages_off(self):
        self._visainstrument.write('SENS:AVER 0')

    def cont_off(self):
        #Turn continuous sweep off
        self._visainstrument.write("INITiate:CONTinuous OFF")
    def sweep(self):
        self._visainstrument.write("INITiate:IMMediate;*wai")

   
    def set_ch1(self,number,Sxx):
        self._visainstrument.write("CALC1:PAR:DEF:EXT '%s',%s" % (Sxx)) #make measuement

    def test_run(self):
        '''
        This function sets the PNA to 2 windows and measures S21, first trace is put in
        the first window, second trace is put in the second window.
        '''
        self._visainstrument.write("DISPlay:WINDow1:STATE ON")
        #Create and turn on window/channel 1
        self._visainstrument.write("CALCulate1:PARameter:DEFine:EXT 'MyMeas1',S21")
        #Define a measurement name, parameter
        self._visainstrument.write("DISPlay:WINDow1:TRACe1:FEED 'MyMeas1'")
        #Associate ("FEED") the measurement name ('MyMeas') to WINDow (1)
        self._visainstrument.write("DISPlay:WINDow2:STATE ON")
        #Create and turn on window/channel 2
        self._visainstrument.write("CALCulate2:PARameter:DEFine:EXT 'MyMeas2',S21")
        #Define a measurement name, parameter
        self._visainstrument.write("DISPlay:WINDow2:TRACe2:FEED 'MyMeas2'")
        #Associate ("FEED") the measurement name ('MyMeas') to WINDow (2)
        #
        #Set slow sweep so we can see
        self._visainstrument.write("SENS1:SWE:TIME 2") 
        self._visainstrument.write("SENS2:SWE:TIME 2")
        #set number of points to 10
        self._visainstrument.write("SENS1:SWE:POIN 2001")
        self._visainstrument.write("SENS2:SWE:POIN 2001")
    def test_hold(self):
        #Put both channels in Hold
        self._visainstrument.write("SENS1:SWE:MODE HOLD")
        self._visainstrument.write("SENS2:SWE:MODE HOLD")

# --------------------------------------
#           parameters
# --------------------------------------

    def do_get_sweeppoints(self):
        return self._visainstrument.ask("SENSe1:SWEep:POIN?")
    def do_get_start_frequency(self): #in MHz
        return float(self._visainstrument.ask('SENS:FREQ:START?'))/1e6
    def do_get_stop_frequency(self): #in MHz
        return float(self._visainstrument.ask('SENS:FREQ:STOP?'))/1e6
    def do_get_sweeptime(self): #in MHz
        return float(self._visainstrument.ask('SENS1:SWE:TIME?'))
    def do_get_resolution_bandwidth(self):
        return float(self._visainstrument.ask('SENS:BWID?'))/1e6
    def do_get_averages(self):
        return float(self._visainstrument.ask('SENS:AVER:COUN?'))
    
    def do_set_sweeppoints(self,number):
        self._visainstrument.write('SENSe1:SWEep:POINts %s' % (number))
    def do_set_start_frequency(self,number): #in MHz
        self._visainstrument.write('SENS:FREQ:START %s' % (number)) 
    def do_set_stop_frequency(self,number): #in MHz
        self._visainstrument.write('SENS:FREQ:STOP %s' % (number))
    def do_set_resolution_bandwidth(self,number):
        self._visainstrument.write('SENS:BWID %s' % (number))
    def do_set_averages(self,number):
        self._visainstrument.write('SENS:AVER:COUN %s' % (number))
 


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
    
