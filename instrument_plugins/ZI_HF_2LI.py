# Keithley_2700.py driver for Keithley 2700 DMM
# Pieter de Groot <pieterdegroot@gmail.com>, 2008
# Martijn Schaafsma <qtlab@mcschaafsma.nl>, 2008
# Reinier Heeres <reinier@heeres.eu>, 2008
#
# Update december 2009:
# Michiel Jol <jelle@michieljol.nl>
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
        self.add_parameter('frequency',
            flags=Instrument.FLAG_GETSET,
            units='Hz', minval=1e-6, maxval=50e6, type=types.FloatType)
        self.add_parameter('timeconstant',
            flags=Instrument.FLAG_GETSET,
            units='s', minval=1e-6, maxval=500, type=types.FloatType)
        self.add_parameter('output_switch',
            flags=Instrument.FLAG_GETSET,
            units='boolean', minval=0, maxval=1, type=types.IntType)
        self.add_parameter('output_range',
            flags=Instrument.FLAG_GETSET,
            units='V', minval=0.01, maxval=10, type=types.FloatType)
        self.add_parameter('output_channel_fraction',
            flags=Instrument.FLAG_GETSET,
            units='V/V', minval=0, maxval=1, type=types.FloatType)
        self.add_parameter('output_channel_enables',
            flags=Instrument.FLAG_GETSET,
            units='boolean', minval=0, maxval=1, type=types.IntType)
        self.add_parameter('power',
            flags=Instrument.FLAG_GETSET,
            units='V', minval=0, maxval=10, type=types.FloatType)

        
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
        return float(sample['phase'])

    def get_amplitude(self,node=0):
        sample = self.get_sample(node)
        return numpy.sqrt(float(sample['x'])**2+float(sample['y'])**2)

    def do_get_frequency(self,node=0):
        sample = self.get_sample(node)
        return float(sample['frequency'])

    def do_set_frequency(self,value=10e6,node=0):
        self._daq.set([[['/'+self._device+'/oscs/'+str(node)+'/freq'],value]])

    def do_get_timeconstant(self,node=0):
        return self._daq.getDouble('/'+self._device+'/demods/'+str(node)+'/timeconstant')

    def do_set_timeconstant(self,value=0.01,node=0):
        self._daq.set([[['/'+self._device+'/demods/'+str(node)+'/timeconstant'],value]])

    def do_get_output_switch(self,node=0):
        return self._daq.getInt('/'+self._device+'/sigouts/'+str(node)+'/on')

    def do_set_output_switch(self,value,node=0):
        self._daq.set([[['/'+self._device+'/sigouts/'+str(node)+'/on'],value]])

    def do_get_output_range(self,node=0):
        return self._daq.getDouble('/'+self._device+'/sigouts/'+str(node)+'/range')

    def do_set_output_range(self,value,node=0):
        if value not in [0.01,0.1,1,10]:
            logging.warning('Allowed values for range are 0.01, 0.1, 1, 10 V. Range is not set.')
            #I would like it to return a False but I don't know how
        else:    
            self._daq.set([[['/'+self._device+'/sigouts/'+str(node)+'/range'],value]])

#from here, zi cannot find the nodes: use the program zicontrol and look at the bottom for the code of the nodes

    def do_get_output_channel_fraction(self,node=0,channel=6):
        return self._daq.getDouble('/'+self._device+'/sigouts/'+str(node)+'/amplitudes/'+str(channel))

    def do_set_output_channel_fraction(self,value,node=0,channel=6):
        self._daq.set([[['/'+self._device+'/sigouts/'+str(node)+'/amplitudes/'+str(channel)],value]])

    def do_get_output_channel_enables(self,node=0,channel=6):
        #return ('/'+self._device+'/sigouts/'+str(node)+'/enables/'+str(channel))
        return self._daq.getInt('/'+self._device+'/sigouts/'+str(node)+'/enables/'+str(channel))

    def do_set_output_channel_enables(self,value,node=0,channel=6):
        self._daq.set([[['/'+self._device+'/sigouts/'+str(node)+'/enables/'+str(channel)],value]])


    def do_get_power(self,node=0,channel=6):
        fraction = self.get_output_channel_fraction(node=node,channel=channel)
        chrange = self.get_output_range(node=node)
        return chrange*fraction

    def do_set_power(self,value,node=0,channel=6,safetyrange=0.8):
        
        if value < 0.01*safetyrange:
            chrange = 0.01
        elif value < 0.1*safetyrange:
            chrange = 0.1
        elif value < 1*safetyrange:
            chrange = 1
        else:
            chrange = 10

        fraction = value/chrange
        self.set_output_range(chrange, node=node)
        self._daq.set([[['/'+self._device+'/sigouts/'+str(node)+'/amplitudes/'+str(channel)],value/chrange]])


    def get_daq(self):
        return self._daq


       
    def write(self,string,value):
        self._daq.set([[[string],value]])

    def query(self,string):
        try:
            return self._daq.getDouble(string)
        except:
            return self._daq.getInt(string)
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
    
