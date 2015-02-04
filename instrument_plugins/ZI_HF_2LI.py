# ZI_HF_2LI.py driver for Zurich Instruments 50 MHz HF2LI lockin amplifier
# Harold Meerwaldt <H.B.Meerwaldt@tudelft.nl>, 2012
# Scott Johnston <jot@mit.edu>, 2012
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

#Install the Zurich instrument library from www.zhinst.com or the MED bulk drive at:
#L:\Python\Installers\ziPython-11.08.0.9230.win32-py2.7
#into Python at:
#C:\Python27\Lib\site-packages\
#
#more info at: http://www.zhinst.com/blogs/schwizer/2011/05/controlling-the-hf2-li-lock-in-with-python/
#and chapter 10: Node definitions of the manual for setting and getting parameters

import zhinst
from zhinst import utils
from zhinst import ziPython

class ZI_HF_2LI(Instrument):
    '''
    This is the driver for the Zurich Instruments HF-2LI 50MHz lock-in amplifier

    Usage:
    Initialize with e.g.:
    lockin = qt.instruments.create('lockin', 'ZI_HF_2LI',
        host='localhost',port=8005
        reset=False
        )
    '''

    def __init__(self, name, host='localhost',port=8005, reset=False):
        '''
        Initializes the Zurich Instruments lock-in, and communicates with the wrapper.

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
        logging.info('Initializing instrument Zurich Instruments HF-2LI 50MHz lock-in amplifier')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        #self._address = address
        #self._visainstrument = visa.instrument(self._address)

        self._daq = zhinst.ziPython.ziDAQServer(host, port)
        self._device = zhinst.utils.autoDetect()

        # Add parameters to wrapper
        # you need a funtion with do_get_parameter and do_set_parameter, which
        # will generate functions get_parameter and set_parameter
        # the channels option will generate functions set_parameter1() e.g.
        # and needs to be called without the "protected" options self and channel
        self.add_parameter('frequency',
            flags=Instrument.FLAG_GETSET,
            units='Hz', channels=(0,1), minval=1e-6, maxval=50e6, type=types.FloatType)
        self.add_parameter('timeconstant',
            flags=Instrument.FLAG_GETSET,
            units='s', channels=(0,1),minval=780e-9, maxval=500, type=types.FloatType)
        self.add_parameter('filter_order',
            flags=Instrument.FLAG_GETSET,
            units='s', channels=(0,1),minval=1, maxval=8, type=types.IntType)
        self.add_parameter('output_switch',
            flags=Instrument.FLAG_GETSET,
            units='boolean', channels=(0,1),type=types.BooleanType)
        self.add_parameter('output_range',
            flags=Instrument.FLAG_GETSET,
            units='V', channels=(0,1), minval=0.01, maxval=10, type=types.FloatType)
        self.add_parameter('input_range',
            flags=Instrument.FLAG_GETSET,
            units='V', channels=(0,1), minval=0.001, maxval=2, type=types.FloatType)
        self.add_parameter('output_channel_fraction',
            flags=Instrument.FLAG_GETSET,
            units='V/V', channels=(0,1), minval=0, maxval=1, type=types.FloatType)
        self.add_parameter('output_channel_enables',
            flags=Instrument.FLAG_GETSET,
            units='boolean', channels=(0,1), minval=0, maxval=1, type=types.IntType)
        self.add_parameter('power',
            flags=Instrument.FLAG_GETSET,
            units='V', channels=(0,1), minval=0, maxval=10, type=types.FloatType)
        self.add_parameter('reference',
            flags=Instrument.FLAG_GETSET,type=types.StringType)
        self.add_parameter('impedance50Ohm',
            flags=Instrument.FLAG_GETSET,channels=(0,1),type=types.BooleanType)
        self.add_parameter('external_clock',
            flags=Instrument.FLAG_GETSET,type=types.BooleanType)
        self.add_parameter('auxoffset', type=types.FloatType, channels=(0,1,2,3),
            flags=Instrument.FLAG_GETSET,
            minval=-10.5, maxval=10.5, units='V', format='%.3f')
        
        # Add functions to wrapper
##        self.add_function('set_mode_volt_ac')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

  #      if reset:
 #          self._visainstrument.write('*RST')
 #       #else:
           # self.get_all()
           # self.set_defaults()

        
        

# --------------------------------------
#           functions
# --------------------------------------

#only the default node and channel are stored in the parameter

    def get_sample(self,node=0):
        return self._daq.getSample('/'+self._device+'/demods/'+str(node)+'/sample')

    def get_x(self,node=0):
        sample = self.get_sample(node)
        return float(sample['x'])

    def get_y(self,node=0):
        sample = self.get_sample(node)
        return float(sample['y'])

    def get_phase(self,node=0):
        sample = self.get_sample(node)
        return numpy.arctan(float(sample['y'])/float(sample['x']))
        #return float(sample['phase'])

    def get_amplitude(self,node=0):
        sample = self.get_sample(node)
        return numpy.sqrt(float(sample['x'])**2+float(sample['y'])**2)

    def do_get_frequency(self,channel):
        sample = self.get_sample(channel)
        return float(sample['frequency'])

    def do_set_frequency(self,value,channel):
        print('/'+self._device+'/oscs/'+str(channel)+'/freq')
        self._daq.set([[['/'+self._device+'/oscs/'+str(channel)+'/freq'],value]])

    def do_get_timeconstant(self,channel):
        return self._daq.getDouble('/'+self._device+'/demods/'+str(channel)+'/timeconstant')

    def do_set_timeconstant(self,value,channel):
        self._daq.set([[['/'+self._device+'/demods/'+str(channel)+'/timeconstant'],value]])

    def do_get_filter_order(self,channel):
        return self._daq.getDouble('/'+self._device+'/demods/'+str(channel)+'/order')

    def do_set_filter_order(self,value,channel):
        self._daq.set([[['/'+self._device+'/demods/'+str(channel)+'/order'],value]])

    def do_get_output_switch(self,channel):
        return self._daq.getInt('/'+self._device+'/sigouts/'+str(channel)+'/on')

    def do_set_output_switch(self,value,channel):
        self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/on'],value]])

    def do_get_output_range(self,channel):
        return self._daq.getDouble('/'+self._device+'/sigouts/'+str(channel)+'/range')

    def do_set_output_range(self,value,channel):
        if value not in [0.01,0.1,1,10]:
            logging.warning('Allowed values for range are 0.01, 0.1, 1, 10 V. Range is not set.')
            #I would like it to return a False but I don't know how
        else:    
            self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/range'],value]])

    def do_get_input_range(self,channel):
        return self._daq.getDouble('/'+self._device+'/sigins/'+str(channel)+'/range')

    def do_set_input_range(self,value,channel):
        self._daq.set([[['/'+self._device+'/sigins/'+str(channel)+'/range'],value]])

    def set_input_range_auto(self,channel):
        self._daq.set([[['/'+self._device+'/sigins/'+str(channel)+'/range']]])


#from here, zi cannot find the nodes: use the program zicontrol and look at the bottom for the code of the nodes

    def do_get_output_channel_fraction(self,channel):
        return self._daq.getDouble('/'+self._device+'/sigouts/'+str(channel)+'/amplitudes/'+str(6))

    def do_set_output_channel_fraction(self,value,channel):
        self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/amplitudes/'+str(6)],value]])

    def do_get_output_channel_enables(self,channel):
        #return ('/'+self._device+'/sigouts/'+str(node)+'/enables/'+str(channel))
        return self._daq.getInt('/'+self._device+'/sigouts/'+str(channel)+'/enables/'+str(6))

    def do_set_output_channel_enables(self,value,channel):
        self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/enables/'+str(6)],value]])


    def do_get_power(self,channel):
        fraction = self.get_output_channel_fraction(channel)
        chrange = self.get_output_range(channel)
        return chrange*fraction

    def set_power000(self,value,chrange,channel=0):
        
        self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/amplitudes/'+str(6)],value/chrange]])

    def do_set_power(self,value,channel,safetyrange=0.8):
        
        if value < 0.01*safetyrange:
            chrange = 0.01
        elif value < 0.1*safetyrange:
            chrange = 0.1
        elif value < 1*safetyrange:
            chrange = 1
        else:
            chrange = 10

        fraction = value/chrange
        if chrange not in [0.01,0.1,1,10]:
            logging.warning('Allowed values for range are 0.01, 0.1, 1, 10 V. Range is not set.')
            print 'error wrong range'
            #I would like it to return a False but I don't know how
        else:    
            self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/range'],chrange]])
        
        self._daq.set([[['/'+self._device+'/sigouts/'+str(channel)+'/amplitudes/'+str(6)],value/chrange]])


    def do_get_reference(self):
        enable = self._daq.getInt('/'+self._device+'/plls/0/enable')
        adcselect = self._daq.getInt('/'+self._device+'/plls/0/adcselect')
        if enable == 0:
            string = 'Internal'
        elif enable ==1:
            if adcselect == 0:
                string = 'Signal Input 1'
            elif adcselect == 1:
                string = 'Signal Input 2'

        return string

    def do_set_reference(self,value):
        if value == 'Internal':
            self._daq.set([[['/'+self._device+'/plls/0/enable'],0]])
        elif value == 'Signal Input 1':
            self._daq.set([[['/'+self._device+'/plls/0/adcselect'],0]])
            self._daq.set([[['/'+self._device+'/plls/0/enable'],1]])
        elif value == 'Signal Input 2':
            self._daq.set([[['/'+self._device+'/plls/0/adcselect'],1]])
            self._daq.set([[['/'+self._device+'/plls/0/enable'],1]])
        else:
            print "Allowed values are: 'Internal', 'Signal Input 1', 'Signal Input 2'"

  
    def do_get_impedance50Ohm(self,channel):
        return self._daq.getInt('/'+self._device+'/sigins/'+str(channel)+'/imp50')

    def do_set_impedance50Ohm(self,value,channel):
        self._daq.set([[['/'+self._device+'/sigins/'+str(channel)+'/imp50'],value]])

    def do_get_external_clock(self):
        return self._daq.getInt('/'+self._device+'/system/extclk')

    def do_set_external_clock(self,value):
        self._daq.set([[['/'+self._device+'/system/extclk'],value]])
        

    def set_auxmode(self,channel,value):
        '''
        example:
                    .set_auxmode(3,-1)
                    ->set aux3 to manual mode
        
        #select channel and integer value (see list below)
        Signal to be given out.
        Write Integer Number
        Read Integer Number
        Setting Yes
        Values -1 Manual
        /DEV0...n/AUXOUTS/0...n/DEMODSELECT
        HF2 User Manual Revision 7921 Zurich Instruments 232
        0 X
        1 Y
        2 R
        3 Theta
        4 PLL 0 (with installed PLL option))
        4 PLL 1 (with installed PLL option))
        #if channel = 1 aux 1 is selected not 0 anymore when using (channel -1)
        '''
        self._daq.set([[['/'+self._device+'/AUXOUTS/'+str(channel)+'/OUTPUTSELECT'],value]])
    def do_set_auxoffset(self, value, channel):
        '''
        example:
                    .set_auxmode(4,-5)
                    ->set aux4 offset to -5V

        set an offset value on the aux
        channel = aux
        value is in Volts
        '''
        self._daq.set([[['/'+self._device+'/AUXOUTS/'+str(channel)+'/OFFSET'],value]])

    def do_get_auxoffset(self,channel):
        #self._daq.get([[['/'+self._device+'/AUXOUTS/'+str(channel)+'/OFFSET'],value]])
        return self._daq.getInt('/'+self._device+'/auxouts/'+str(channel)+'/OFFSET/')

    def set_auxscale(self,channel,value):
        self._daq.set([[['/'+self._device+'/AUXOUTS/'+str(channel)+'/SCALE'],value]])


    def get_daq(self):
        return self._daq

    def write(self,string,value):
        self._daq.set([[['/'+self._device+'/'+string],value]])
        #eg: string='oscs/0/freq' value=3000

    def query(self,string):
        try:
            return self._daq.getDouble('/'+self._device+'/'+string)
        except:
            return self._daq.getInt('/'+self._device+'/'+string)
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
    
