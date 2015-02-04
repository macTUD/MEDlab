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

from time import sleep,time

import qt
import ADwin

def Bit32(voltage):
    '''Function that converts a Voltage to a byte fed into the ADwin Gold.
    '''
    return int(voltage*3277+32768)

def Volt(bit32):
    '''
    Function that converts a bit into a voltage.
    '''
    return float((bit32-32768))/float(3277)

class ADwin_DAC_sal(Instrument):
    '''
    This is the driver for the Adwin Gold that rudimentary implements the ADwin as
    four DACs.
    
    Usage:
    Initialize with
    <name> = qt.instruments.create('<name>', 'ADwin_DAC', address='device no')

    device number can be found with ADconfig usually it is 0x255
    '''

    def __init__(self, name, address):
        '''
        Initializes the any_device, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
   TU         address (string)        : GPIB address
            reset (bool)            : resets to default values
           
        Output:
            None
        '''

        # Initialize wrapper functions
        logging.info('Initializing instrument ADwin Gold')
        Instrument.__init__(self, name, tags=['virtual'])

        # Add some global constants
        self._address = address

        self.ADwin = ADwin.ADwin(self._address,1)

        self.ADwin.Boot('C:\ADwin\ADwin9.btl')
        sleep(0.01)

        #For now we just implemented a single fixed program that can be loaded
        self.ADwin.Load_Process('C:\qtlab\instrument_plugins\ADwin_DACinout.T91')
        #('C:\ADwin\dev\ADwin_DACinout.T91')C:\qtlab\instrument_plugins\ADwin_DACinout.T91
        #('C:\qtlab\instrument_plugins\ADwin_DACinout.T91')
                                
                                
        self.add_parameter('DAC_1',
                            flags=Instrument.FLAG_GETSET,
                            units='V', minval=-10.0, maxval=10.0,
                            type=types.FloatType)
        self.add_parameter('DAC_2',
                            flags=Instrument.FLAG_GETSET,
                            units='V', minval=-10.0, maxval=10.0,
                            type=types.FloatType)
        self.add_parameter('DAC_3',
                            flags=Instrument.FLAG_GETSET,
                            units='V', minval=-10.0, maxval=10.0,
                            type=types.FloatType)
        self.add_parameter('DAC_4',
                            flags=Instrument.FLAG_GETSET,
                            units='V', minval=-10.0, maxval=10.0,
                            type=types.FloatType)
        self.add_parameter('rampsteps',
                           flags=Instrument.FLAG_GETSET,
                           units='V/s', minval=1, maxval=100, type=types.FloatType)
        self.add_parameter('clockcycle',
                           flags=Instrument.FLAG_GETSET,
                           units='MHz', type=types.FloatType)

        #self.add_function('
        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        self.add_function('start_process')
        self.add_function('load_process')
##        self.add_function('sDAC_1')
##        self.add_function('gDAC_1')
        
        #General functions to access the registers of the ADwin
##        self.add_function('do_get_Par')
##        self.add_function('do_set_Par')
##        self.add_function('do_get_FPar')
##        self.add_function('do_set_FPar')
# --------------------------------------
#           functions
# --------------------------------------

    def start_process(self):
        self.ADwin.Start_Process(1)
        return None
        
    def load_process(self, proces_file):
        print 'something'
        return None

    def do_set_rampsteps(self,rampsteps):
        '''The larger the faster'''
        self.ADwin.Set_Par(12, int(rampsteps))
        return int(rampsteps)
        

    def do_get_rampsteps(self):
        return float(self.ADwin.Get_Par(12))

    def do_set_clockcycle(self,clockcycle):
        self.ADwin.Set_Par(10,int(clockcycle))
        return clockcycle

    def do_get_clockcycle(self):
        globaldelay=self.ADwin.Get_Par(10)
        return globaldelay

    #DAC 1
    def do_set_DAC_1(self, voltage):
        self.ADwin.Set_Par(21,Bit32(voltage))
        return voltage

    def do_get_DAC_1(self):        
        bit32=self.ADwin.Get_Par(1)
        return Volt(bit32)

    #DAC 2
    def do_set_DAC_2(self, voltage):
        self.ADwin.Set_Par(22,Bit32(voltage))
        return voltage

    def do_get_DAC_2(self):        
        bit32=self.ADwin.Get_Par(2)
        #print bit32
        return Volt(bit32)

    def set_bitwise_DAC_2(self, voltage):
        self.ADwin.Set_Par(22,voltage)
        return voltage

    #DAC 3
    def do_set_DAC_3(self, voltage):
        self.ADwin.Set_Par(23,Bit32(voltage))
        return voltage

    def do_get_DAC_3(self):        
        bit32=self.ADwin.Get_Par(3)
        return Volt(bit32)

    #DAC 4
    def do_set_DAC_4(self, voltage):
        self.ADwin.Set_Par(24,Bit32(voltage))
        return voltage

    def do_get_DAC_4(self):        
        bit32=self.ADwin.Get_Par(4)
        return Volt(bit32)

   
    def set_sec_DAC_1(self, voltage):
        '''
        secure sweeps (it waits until the dac reaches the given values )
        set dac and return when finished
        This prevents artifacts from a unfinished process
        '''
        self.do_set_DAC_1(voltage)
        qt.msleep(0.002)
        while abs(self.do_get_DAC_1()-voltage)>0.1:
            #self.do_set_DAC_1(voltage)
            qt.msleep(0.010)
    def set_sec_DAC_2(self, voltage):
        self.do_set_DAC_2(voltage)
        qt.msleep(0.002)
        while abs(self.do_get_DAC_2()-voltage)>0.1:
            #self.do_set_DAC_2(voltage)
            qt.msleep(0.010)
        self.do_set_DAC_2(voltage)
        
    def set_sec_DAC_3(self, voltage):
        self.do_set_DAC_3(voltage)
        qt.msleep(0.002)
        while abs(self.do_get_DAC_3()-voltage)>0.1:
            #self.do_set_DAC_3(voltage)
            qt.msleep(0.010)
        self.do_set_DAC_3(voltage)
        
    def set_sec_DAC_4(self, voltage):
        self.do_set_DAC_4(voltage)
        qt.msleep(0.002)
        while abs(self.do_get_DAC_4()-voltage)>0.1:
            #self.do_set_DAC_4(voltage)
            qt.msleep(0.010)
        self.do_set_DAC_4(voltage)


    def get_ADC(self,averages = 1000):
        self.ADwin.Set_Par(9,averages) #set averages
        self.ADwin.Set_Par(13,1) #initiate measurement
        #qt.msleep(averages*0.0001) no need
        adc1 = Volt(float(self.ADwin.Get_Par(5)))/float(4)
        adc2 = Volt(float(self.ADwin.Get_Par(6)))/float(4)
        #adc3 = Volt(self.ADwin.Get_Par(7))/float(8)
        #adc4 = Volt(self.ADwin.Get_Par(8))/float(8)
        return adc1,adc2 #,adc3,adc4

    
##        def do_get_Par(self, par):
##            '''
##            Get the value of par inside the ADwin Par register
##            '''
##            return self.ADwin.Get_Par(par)
##
##        def do_set_Par(self, par, value):
##            '''
##            Set the value of par inside the ADwin Par register
##            '''
##            self.ADwin.Set_Par(par,value)
##        
##        def do_get_FPar(self, par):
##            '''
##            Get the value of par inside the ADwin FPar register
##            '''
##            return self.ADwin.Get_FPar(par)
##
##        def do_set_FPar(self, par, value):
##            '''
##            Set the value of par inside the ADwin FPar register
##            '''
##            self.ADwin.Set_FPar(par,value)


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
        self.set_DAC_1(0)
        self.set_DAC_2(0)
        self.set_DAC_3(0)
        self.set_DAC_4(0)

    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
        self.set_DAC_1(0)
        self.set_DAC_2(0)
        self.set_DAC_3(0)
        self.set_DAC_4(0)
  
