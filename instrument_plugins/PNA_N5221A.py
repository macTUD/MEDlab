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
## QTlab driver written by Ben S. & Sal Jua Bosman
## Steelelab-MED-TNW-TU Delft
## contact: b.h.schneider@tudelft.nl
## contact: saljuabosman@mac.com
##################################


from instrument import Instrument
import visa
import types
import logging
import numpy as np
import cmath as cm

import qt

##class pna_measurement():
##    def __init(self):
##
##        trace_list=[]
##    

class PNA_N5221A(Instrument):
    '''
    This is a qtlab driver for the Agilent PNA_N5221A VNA.

    This driver by calling the function setup standard sets up a measurement (trace) S12, from 1GHz, to 10GHz, 2000sweeppoints &.1MHz bandwidth
    by changing the parameters one can change this default setting. On top of this one can also add secondary
    traces. The traces are listed in the private list self._trace_list, wich parameters aren't stored through the standard
    qtlab parameter book keeping, if this is used more often we can decide to make each trace as an individual QTlab VI

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'PNA_N5221A',
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


        #private list to bookkeep secondary traces traces inside format is:
        #    [trace1, trace2, ..., tracen] name is the index of this list plus one
        #    trace1 = [channel_nr, trace_nr, name, measurement_type, window_nr, format]
        
        self._secondary_trace_list = []
        self._window_count = 0

        # Add parameters to wrapper

        self.add_parameter('start_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz', minval=10e6, maxval=13500e6)
        self.add_parameter('stop_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz', minval=10e6, maxval=13500e6)
        self.add_parameter('sweeppoints',
                           flags=Instrument.FLAG_GETSET,
                           units=' ', minval=1, maxval=32001,
                           type=types.FloatType)
        self.add_parameter('sweeptime',
                           flags=Instrument.FLAG_GETSET,
                           units='sec',
                           type=types.FloatType)
        self.add_parameter('resolution_bandwidth', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz')
        self.add_parameter('averages', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='',minval=0, maxval=32767)
        self.add_parameter('power', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='dBm',minval=-30, maxval=30)
        self.add_parameter('dac1', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',minval=-10.0, maxval=10.0)
        self.add_parameter('dac2', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',minval=-10.0, maxval=10.0)

        self.add_parameter('measurement_type', type=types.StringType, flags=Instrument.FLAG_GETSET, units='')
        self.add_parameter('measurement_format', type=types.StringType, flags=Instrument.FLAG_GETSET, units='')
        

        # Add functions to wrapper
        self.add_function('abort')
        self.add_function('read')
        self.add_function('w')
        self.add_function('q')
        self.add_function('reset')
        self.add_function('get_all')
        self.add_function('setup')
        self.add_function('reset_averaging')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

# --------------------------------------
#           functions
# --------------------------------------

    def setup(self,measurement_type='S21', measurement_format = 'MLOG', start_frequency=1.5e9,
              stop_frequency=8.5e9, sweeppoints=2000,bandwidth=1e6,level=-10,continuous=False):
        '''
        Standard function to call everytime to setup a measurement.
        for the measurement type one can select S11,S12,S21, S22, A, B, A/R1,2 ,
        AI1,2 , etc

        for more information see:
        #options can be found here: http://na.tm.agilent.com/pna/help/latest/Programming/GP-IB_Command_Finder/Calculate/Parameter.htm#cpd


        It starts to continuously sweep from here, when fetching data set continuously OFF
        '''

        if(len(self._secondary_trace_list)>0):
            print 'Only call setup when no traces active yet.'
        
        self.set_measurement_type(measurement_type)         #first a new measurement should be defined before one can set other settings
        self.set_start_frequency(start_frequency)
        self.set_stop_frequency(stop_frequency)
        self.set_sweeppoints(sweeppoints)
        self.set_resolution_bandwidth(bandwidth)
        self.set_power(level)
        
        self.set_measurement_format(measurement_format)
        self._window_count =self._window_count+1

        if(continuous==False):
            self._visainstrument.write("INITiate:CONTinuous OFF")
        if(continuous==True):
            self._visainstrument.write("INITiate:CONTinuous ON")
        
    def sweep(self, continuous=False):
        '''
        Function runs a single or multiple sweeps
        '''
        #Turn continuous sweep off
        self._visainstrument.write("INITiate:CONTinuous OFF")
        if(continuous==True):
            self._visainstrument.write("INITiate:CONTinuous ON")
        self._visainstrument.write("INITiate:IMMediate;*wai")

    def print_trace_list(self, display=True ):

        if(display==True):
            print 'window_count' + str(self._window_count)

            print 'format trace_list= [trace1, trace2, ..., tracen] name is the index of this list plus one'
            print 'trace1 = [channel_nr, trace_nr, name, measurement_type, window_nr, format]'
        return self._secondary_trace_list

    def add_trace(self, measurement_type='S11', measurement_format='MLOG',new_channel=False, display=True, new_window=False):
        '''
        This function adds a new trace to the VNA, like the setup method, one can chose
        if it is made in the same channel, and thus sharing all kinds of triggering properties (?),
        and whether it is diplayed or not in a new window.
        '''
        
        index = len(self._secondary_trace_list)+1         #number of active channels
        channel_nr=1
        trace_nr=1
        if(new_channel==True):
            #find the last empty channel
            channel = self.list_channel(index+1)
            if(channel=='NO CATALOG'):
                channel_nr=index+1
                trace_nr=1
            else:
                print 'OEPS, something went wrong with tracebook keeping!'
                return 0
        else:
            #dump trace in channel 1
            channel_nr=1
            trace_nr = int(float(len(self.list_channel(channel_nr).split(','))/2)+1)

        name = str(index+1)
        self._visainstrument.write("CALC" + str(channel_nr) + ":PAR:DEF:EXT '" + name + "', " + measurement_type)
        
        window_nr=1

        if(display==True):
            #Display trace somewhere
            
            if(new_window==True):
                #get the window_count
                window_nr =self._window_count+1
                self._window_count = self._window_count+1
                self._visainstrument.write("DISP:WIND" + str(window_nr) + ":STATE ON")
                self._visainstrument.write("DISP:WIND" + str(window_nr) + ":TRAC1" + ":FEED '" + name +"'")
                #make new window
            else:
                #dump trace in first window
                self._visainstrument.write("DISP:WIND1:TRAC" + name + ":FEED '" + name + "'")
        else:
            print 'Do not display'
            #don't bother to draw the trace
        print 'chann' + str(channel_nr) + 'trace_nr' + str(trace_nr)
        self.set_format(measurement_format, channel=channel_nr, trace_number=trace_nr)
           
        self._secondary_trace_list.append([channel_nr,trace_nr,name,measurement_type, window_nr,measurement_format])
        print self._secondary_trace_list

    def fetch_data(self, channel=1, trace_number=1, polar=False):
        '''Reads the data from Channel 1 (default) and its first tracce,
        assumes ASCII, if IQ is False it returns R,\phi
        '''
        a=0
        while a==0:
            qt.msleep(0.05)
            try:
                a=eval(self.q('*OPC?;'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                a=0

        
        #now select correct channel and tracename
        #print "CALC" + str(channel) + ":PAR:SEL " + trace_name
        self._visainstrument.write("CALC" + str(channel) + ":PAR:SEL '" + self._get_trace_name(channel,trace_number) +"'")

        trace = self._visainstrument.ask("CALC" + str(channel) + ":DATA? SDATA")
        tr= map(float,trace.split(','))

        if(polar==False):
            return self.parse_trace(tr,complex_rep=False)
        else:
            trace = self.parse_trace(tr,complex_rep=True) #get list as complex numbers
            tr=[]
            for i in trace:
                tr.append(cm.polar(i))
            radius=[]
            angle=[]
            for i in tr:
                radius.append(i[0])
                angle.append(i[1])
                              
            tr=[]
            tr.append(radius)
            tr.append(angle)
            return tr

    def _get_trace_name(self,channel,trace_number):
        '''private function that retrieves the measurement name given a channel and trace_number (nth experiment in the channel)'''
  
        catalog = self.list_channel(channel)
        catalog=catalog.split(',')

        if(len(catalog)<=(trace_number-1)*2):
           print 'error trace doesnt exist'
           return None
        trace_name=catalog[(trace_number-1)*2]
        return trace_name
    
    def set_format(self, measurement_format, channel=1, trace_number=1, auto_scale_Y=True):
        '''Sets the fromat of the Trace recorded
    
        options are: MLIN, MLOG, PHAS, UPH, IMAG, REAL, POL, SMIT, SADM, SWR, GDEL, KELV, FAHR, CELS
        '''

        #select the correct trace
        self._visainstrument.write("CALC" + str(channel) + ":PAR:SEL '" + self._get_trace_name(channel,trace_number) +"'")

        #sets the format
        self._visainstrument.write("CALC" + str(channel) + ":FORM " + measurement_format)

        #display titles and stuff
        self._visainstrument.write("DISP:WIND1:TRAC:STAT ON")
        self._visainstrument.write("DISP:WIND1:TITL:STAT ON")
        #self._visainstrument.write("CALC1:FORM DBM")
        if(auto_scale_Y==True):
            self._visainstrument.write("DISP:WIND1:TRAC1:Y:SCAL:AUTO")
    def auto_scale(self):
        self._visainstrument.write("DISP:WIND1:TRAC1:Y:SCAL:AUTO")

    def setup_2tone_spectroscopy(self, cw_freq=3e9, start_freq=1e9, stop_freq=10e9, sweep_time=10):
        '''Function to setup the PNA to do a twotone qubit spectroscopy experiment, where the
        PNA's receiver is measuring the response at cw_freq, which is \delta detuned from the w_cav, another external
        source is set @w_cav, such that the cavity is readout.

        The source of the PNA is now the probe_tone, spectroscopically measuring the qubit frequency!

        This function assumes you first setup a measurement. Subsequently it selects this measurement and modifies it
        to the required R2, 1 position (measuring absolute power at port 2, while sending a stimulus via port 1) with the commands
        pna.w("CALC1:PAR:SEL '1'")
        pna.w("CALC1:PAR:MOD:EXT 'R2,1'")
        '''

        #Range numbers Primary=1, Source=2, Receivers=3

        #list available ranges
        print 'available ranges in channel 1'
        print self._visainstrument.ask("SENS1:FOM:CAT?")

        #numbers of specific ranges
        print 'number of Receivers range' + self._visainstrument.ask("SENS1:FOM:RNUM? 'Receivers'")
        print 'number of Source range' + self._visainstrument.ask("SENS1:FOM:RNUM? 'Source'")


        #coupledness of the receiver
        print 'is receiver coupled?'
        print self._visainstrument.ask("SENS1:FOM:RANG3:COUP?")

        ############################
        #General settings
        ############################

        
        self._visainstrument.write("SENS1:FOM:STAT 1")
        print 'freq offset is ' + self._visainstrument.ask("SENS1:FOM:STAT?")
        
        #####################
        #PNA source settings
        #####################
        #uncoupled

        self._visainstrument.write("SENS1:FOM:RANG2:COUP 0")
        print 'source coupling is ' + self._visainstrument.ask("SENS1:FOM:RANG2:COUP?")
        

        #sweeptype: linear
        self._visainstrument.write("SENS1:FOM:RANG2:SWE:TYPE LIN")
        print 'source sweep type is set to ' + self._visainstrument.ask("SENS1:FOM:RANG2:SWE:TYPE?")

        #start frequency -> start_freq
        self._visainstrument.write("SENS1:FOM:RANG2:FREQ:STAR " + str(start_freq))
        qt.msleep(0.01)
        print 'source start frequency is ' + self._visainstrument.ask("SENS1:FOM:RANG2:FREQ:STAR?")


        #stop frequency -> stop_freq
        self._visainstrument.write("SENS1:FOM:RANG2:FREQ:STOP " + str(stop_freq))
        print 'source stop frequency is ' + self._visainstrument.ask("SENS1:FOM:RANG2:FREQ:STOP?")


        #####################
        #PNA receiver setting
        #####################

        #uncoupled

        self._visainstrument.write("SENS1:FOM:RANG3:COUP 0")
        print 'receiver coupling is ' + self._visainstrument.ask("SENS1:FOM:RANG3:COUP?")

        #sweeptype: CW time -> sweep_time (?)

        self._visainstrument.write("SENS1:FOM:RANG3:SWE:TYPE CW")
        print 'receiver sweeptype is set to ' + self._visainstrument.ask("SENS1:FOM:RANG3:SWE:TYPE?")

        #frequency: CW frequency -> cw_freq

        self._visainstrument.write("SENS1:FOM:RANG3:FREQ:CW " + str(cw_freq))
        print 'receiver CW freq is set to ' + self._visainstrument.ask("SENS1:FOM:RANG3:FREQ:CW?") 


        #set the X-axis scale to source 1:
        self._visainstrument.write("SENS1:FOM:DISPlay:SELect " + '"source1"')
        print 'x-axis scaled to' + self._visainstrument.ask("SENS1:FOM:DISP:SEL?")

        #print 'keep S12 to MLOG, now create an extra trace of the phase'

        #self.add_trace(new_channel=False,new_window=False,measurement_type='S12', measurement_format='PHAS')
        #set the sweeptime to 10seconds
        self._visainstrument.write("SENS1:SWE:TIME 10")

        #now at last we modify the measurement to absolute measurement at port 2, while keeping sending signals from port 1
        self._visainstrument.write("CALC1:PAR:SEL '1'")
        self._visainstrument.write("CALC1:PAR:MOD:EXT 'R2,1'")
        #self._visainstrument.write("CALC1:PAR:MOD:EXT 'R1,0'")

        return 0
    
    def parse_trace(self,trace,complex_rep=False):

        tr=[]
        real=trace[::2]
        img=trace[1::2]
        if(complex_rep==False):
            tr.append(real)
            tr.append(img)
            return tr
        else:
            index=0
            for i in real:
                tr.append(complex(i,img[index]))
                index = index+1
            return tr


    def ID(self):
        return self._visainstrument.ask('*IDN?')

    def value(self):
        return self._visainstrument.ask('READ?')
    def read(self):
        self._visainstrument.read()
    def w(self,string):
        self._visainstrument.write(string)
    def q(self,string):
        return self._visainstrument.ask(string)
    def reset(self):
        self._visainstrument.write('SYST:FPReset')
        self._secondary_trace_list=[]
        self._window_count=0
        #Preset the analyzer
    def reset_full(self):
        self._visainstrument.write('*RST')      #stop any OPCs and go to preset (same as 'Preset' button) (overkill) (better)
        self._visainstrument.write('SYST:FPR')  #do reset with all windows and traces deleted
    def abort(self):
        self._visainstrument.write('ABORT')

    def get_all(self):
        self.get_sweeppoints()
        self.get_start_frequency()
        self.get_stop_frequency()
        self.get_averages()
        self.get_resolution_bandwidth()
        self.get_sweeptime()

    def data_ascii(self):
        self._visainstrument.write("format:data ascii")
    def data_32bit(self):
        self._visainstrument.write("FORM REAL,32")
    def data_64bit(self):
        self._visainstrument.write("FORM REAL,64")
    def data_s(self):
        '''
        Fetch command from RAM, to retrieve data from PNA returns 2 numbers per data point (I, Q) 
        '''
        #still to implement, check what format is currently used, and parse the data accordingly
        
        trace = self._visainstrument.ask("CALCulate:DATA? SDATA") # 'Corrected, Complex Meas
        return trace.split(',')
        
    def data_f(self):
        '''
        Fetch command from RAM, to retrieve data from PNA return 2 numbers per data point for Polar (r, \theta) and Smith
        chart format, returns one point for all other formats
        '''

        #still to implement, check what format is currently used, and parse the data accordingly
        
        trace= self._visainstrument.ask("CALCulate:DATA? FDATA") #'Formatted Meas

        tr= map(float,trace.split(','))
        return tr
    
    def data_fmem(self):
        '''
        Fetch command from Memory, same like data_f
        '''
        return self._visainstrument.ask("CALCulate:DATA? FMEM") #'Formatted Memory

    def data_smem(self):
        '''
        Fetch command from Memory, same like data_s
        '''
        return self._visainstrument.ask("CALCulate:DATA? SMEM") #'Formatted Memory

    def set_averages_on(self):
        self._visainstrument.write('SENS:AVER 1')
    def set_averages_off(self):
        self._visainstrument.write('SENS:AVER 0')

    def cont_off(self):
        #Turn continuous sweep off
        self._visainstrument.write("INITiate:CONTinuous OFF")
        
    def convert_data(self,data):
        data = data.split(',')
        newdata=[]
        for i in data:
            newdata.append(float(i))
        return newdata
   
    def list_channel(self, channel=1):
        '''
        Returns a list of all measurements (traces) active on this channel.
        '''
        channel_list = self._visainstrument.ask("CALC" + str(channel) + ":PAR:CAT?")
        return channel_list[1:-1]

    def delete_channel(self, channel=1):
        '''
        Deletes all measurement definitions for specified channel
        '''
        return self._visainstrument.write("CALC" + str(channel) + ":PAR:DEL:ALL")

    def save_settings(self,settingsname):
        '''This function saves the current settings on the PNA harddrive (C:\bin\settingsname.sta)
        '''
        string = 'MMEM:STOR:STAT ' + "'" + settingsname + "'"
        self._visainstrument.write(string)

    def reset_averaging(self):
        '''Resets the averaging!'''
        self._visainstrument.write('SENS:AVER:CLE')
        
       

# --------------------------------------
#           parameters
# --------------------------------------

    def do_get_sweeppoints(self):
        return self._visainstrument.ask("SENSe1:SWEep:POIN?")
    def do_get_start_frequency(self): #in MHz
        return float(self._visainstrument.ask('SENS:FREQ:START?'))
    def do_get_stop_frequency(self): #in MHz
        return float(self._visainstrument.ask('SENS:FREQ:STOP?'))
##    def do_get_sweeptime(self): #in MHz
##        return float(self._visainstrument.ask('SENS1:SWE:TIME?'))
    def do_get_resolution_bandwidth(self):
        return float(self._visainstrument.ask('SENS:BWID?'))
    def do_get_averages(self):
        return float(self._visainstrument.ask('SENS:AVER:COUN?'))
    def do_get_power(self,channel=1):
        return float(self._visainstrument.ask('SOUR:POW'+str(channel)+'?'))

    def do_set_sweeppoints(self,number):
        return self._visainstrument.write('SENSe1:SWEep:POINts %s' % (number))
    def do_set_start_frequency(self,number): #in MHz
        return self._visainstrument.write('SENS:FREQ:START %s' % (number)) 
    def do_set_stop_frequency(self,number): #in MHz
        return self._visainstrument.write('SENS:FREQ:STOP %s' % (number))
    def do_set_resolution_bandwidth(self,number):
        return self._visainstrument.write('SENS:BWID %s' % (number))
    def do_set_averages(self,number):
        return self._visainstrument.write('SENS:AVER:COUN %s' % (number))
    def do_set_power(self,level = -30,channel=1):
        return self._visainstrument.write('SOUR:POW'+str(channel)+' ' +str(level))

    def do_set_measurement_type(self,measure_type):
        '''Sets the measurement type of the main measurement'''

        #delete all traces in channel 1
        self._visainstrument.write("CALC1:PAR:DEL:ALL")  #empty channel 1
      
        self._visainstrument.write("DISP:WIND1:STATE ON") #switches window1 on
        self._visainstrument.write("CALC1:PAR:DEF:EXT '1', " + measure_type)

        self._visainstrument.write("DISP:WIND1:TRACE1:FEED '1'") #connects the standard measurement setup to the display

    def do_get_measurement_type(self):
        '''Gets the measurement type of the main measurement'''
        channel1 = self.list_channel(1)

        if channel1=='"NO CATALOG"':
            return 'NO CATATALOG'
            
        channel1 = channel1.split(',')
        channel1 = channel1[1]
        channel1 = channel1[:-1]
        return channel1

    def do_set_measurement_format(self, measurement_format):
        '''Sets the measurement format of the main measurement

        Options are: MLIN, MLOG, PHAS, UPH, IMAG, REAL, POL, SMIT, SADM, SWR, GDEL, KELV, FAHR, CELS
        '''

        #select the correct trace for main measurement
        self._visainstrument.write("CALC1:PAR:SEL '" + self._get_trace_name(1,1) +"'")

        #sets the format
        self._visainstrument.write("CALC1:FORM " + measurement_format)
        
    def do_get_measurement_format(self):
        '''Gets the measurement format of the main measurement'''

        #select the correct trace for main measurement
        self._visainstrument.write("CALC1:PAR:SEL '" + self._get_trace_name(1,1) +"'")

        #sets the format
        print self._visainstrument.ask("CALC1:FORM?")
        return self._visainstrument.ask("CALC1:FORM?")
             
    def do_get_sweeptime(self):
        '''Gets the sweeptime in ms, the PNA automatically sets it to the fastest possible value, but it
        is very useful to query how long qtlab has to sleep before a sweep is performed
        '''
        return self._visainstrument.ask("SENS1:SWE:TIME?")

    def do_set_sweeptime(self,sweeptime):
        '''Sets the sweeptime, not very useful inless measuring in CW-mode'''
        return self._visainstrument.write("SENS1:SWE:TIME " + str(sweeptime))


    def do_set_dac1(self,number):
        self._visainstrument.write('CONT:AUX:OUTP1:VOLT %s' % (number))

    def do_set_dac2(self,number):
        self._visainstrument.write('CONT:AUX:OUTP2:VOLT %s' % (number))

    def do_get_dac1(self):
        return eval(self._visainstrument.ask('CONT:AUX:OUTP1:VOLT?'))

    def do_get_dac2(self):
        return eval(self._visainstrument.ask('CONT:AUX:OUTP2:VOLT?'))


##    def set_sweeptime_auto(self,auto=True):
##        print "SENS1:SWE:TIME:AUTO " + auto
##        return self._visinstrument.write("SENS1:SWE:TIME:AUTO " + auto)
        


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
    
