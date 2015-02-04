from instrument import Instrument
import types
import logging
import time
import numpy as np


#written by Sal Bosman


class mw_line(Instrument):

    def __init__(self, name, address=None, reset=False):
        Instrument.__init__(self, name, tags=['measure', 'med'])

        # minimum
        self.add_parameter('warm_attenuation', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='dB')

        self.add_parameter('cold_attenuation', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='dB')

        self.add_parameter('4K_amplifier', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='dB')

        self.add_parameter('RT_amplifier', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='dB')

        self.add_parameter('warm_attenuation',type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='dB')


        self.add_parameter('f_cav', type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='Hz')

        self.add_parameter('kappa_cav',type=types.FloatType,
                flags=Instrument.FLAG_GETSET, Units='Hz')


        self.add_parameter('start_time', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('stop_time', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('measurement_time', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('ave_trace_time', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('elapsed_time', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('elapsed_traces', types=types.IntType,
                flags=Instrument.FLAG_GET)


        self.add_parameter('ave_frame_time', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('trace_index', type=types.IntType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('frame_index', type=types.IntType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('trace_fraction', type=types.FloatType,
                flags=Instrument.FLAG_GET)

        self.add_parameter('est_ready', type=types.FloatType,
                flags=Instrument.FLAG_GET)




        self._start_time=self._stop_time=self._measurement_time=0
        self._ave_trace_time=self._ave_frame_time=0
        self._elapsed_time=0

        self._trace_index=self._frame_index=0

        self._current_frame_start_time=0
        self._current_trace_start_time=0
        self._interval=0

        self._YZ_fraction =0
        self._YZ_total=0

        self._trace_time=[]
        self._frame_time=[]

        self._total_frame_time=0
        self._total_trace_time=0

        self._elapsed_traces=0
        self._trace_fraction=0

        self.add_function('start')
        self.add_function('stop')
        self.add_function('start_frame')
        self.add_function('start_trace')
        self.add_function('interval')


    def do_get_Y_name(self):
        return self._Y_name

    def do_get_Z_name(self):
        return self._Z_name

    def do_set_Y_name(self,val):
        self._Y_name=val

    def do_set_Z_name(self,val):
        self._Z_name=val
    
    def do_get_X_points(self):
        return self._X_points

    def do_get_Y_points(self):
        return self._Y_points

    def do_get_Z_points(self):
        return self._Z_points

    def do_set_X_points(self, val):
        self._X_points = val

    def do_set_Y_points(self, val):
        self._Y_points = val

    def do_set_Z_points(self, val):
        self._Z_points = val


    def do_get_start_time(self):
        return self._start_time

    def do_get_stop_time(self):
        return self._stop_time

    def do_get_measurement_time(self):
        return self._measurement_time

    def do_get_trace_index(self):
        return self._trace_index

    def do_get_frame_index(self):
        return self._frame_index

    def do_get_ave_trace_time(self):
        self._ave_trace_time = self._total_trace_time/float(self._trace_index*self._frame_index)
        return self._ave_trace_time

    def do_get_ave_frame_time(self):
        self._ave_frame_time = self._total_frame_time/float(self._frame_index)
        return self._ave_frame_time

    def do_get_elapsed_time(self):
        self._elapsed_time = time.time()-self._start_time
        return self._elapsed_time

    def do_get_elapsed_traces(self):
        self._elapsed_traces = self._frame_index*self._trace_index
        return self._elapsed_traces

    def do_get_trace_fraction(self):
        self._trace_fraction = self._elapsed_traces/ float(self._Y_points*self._Z_points)
        return self._trace_fraction

    def do_get_est_ready(self):
        if(self.get_trace_fraction()==0):
            return 0
        else:
            self._est_ready = self.get_elapsed_time()*(1/self.get_trace_fraction())+self.get_start_time()
        
        return self._est_ready

    def start(self):

    
        self._start_time=self._stop_time=self._measurement_time=0
        self._ave_trace_time=self._ave_frame_time=0
        self._elapsed_time=0

        self._trace_index=self._frame_index=0

        self._current_frame_start_time=0
        self._current_trace_start_time=0
        self._interval=0
        self._elapsed_traces=0

        self._trace_time=[]
        self._frame_time=[]

        self._total_frame_time=0
        self._total_trace_time=0

        
        self._start_time=time.time()
        self._interval=time.time()
    

    def stop(self, publish=False):
        self._stop_time=time.time()

        prev_time = self._current_trace_start_time
        self._current_trace_start_time=time.time()
        self._total_trace_time+=self._current_trace_start_time - prev_time

        prev_time = self._current_frame_start_time
        self._current_frame_start_time=time.time()
        self._total_frame_time+=self._current_frame_start_time - prev_time
        
        self._measurement_time = self._stop_time -self._start_time
        self._ave_trace_time = self._total_trace_time/float(self._trace_index)
        self._ave_frame_time = self._total_frame_time/float(self._frame_index)

        if(publish):
            print 'Measurement timing report'
            print 'Measurement start: \t', time.ctime(self._start_time)
            print 'Measurement stop: \t', time.ctime(self._stop_time)
            print '\n'
            print 'Total measurement time \t', self._elapsed_time, 's'
            print 'Average trace time \t', self._ave_trace_time, 's'
            print 'Average frame time \t', self._ave_frame_time, 's'

    def start_frame(self,Z_value=0, publish=False):
        if(self._frame_index!=0):
            prev_time = self._current_frame_start_time
            self._current_frame_start_time=time.time()
            self._total_frame_time+=self._current_frame_start_time - prev_time
        else:
            self._current_frame_start_time=time.time()

        self._frame_index+=1
        self._trace_index=0

        if(publish):
            output = ['Frame:', self.get_frame_index(),'/',self.get_Z_points(),self.get_Z_name(),':', format(Z_value,'.2f'), format(100*self.get_trace_fraction(),'.2f'),'%','t:',format(self.get_elapsed_time(),'.2f'),'s','done at:', time.ctime(self.get_est_ready())]
            print '\n'
            print("{:>10}{:>3}{:>1}{:>1}{:>15}{:>1}{:>8}{:>10}{:>1}{:>10}{:>3}{:>2}{:>15}{:>27}".format(*output))
            print '\n'
            #print 'Frame: ', self.get_frame_index(), '/', self.get_Z_points(), '%\t t:', self.get_elapsed_time(), '(s)\t done at: ', time.ctime(self.get_start_time()+self.get_est_ready()) 
        
        
    def start_trace(self, Y_value=0,Z_value=0,publish=False):
        if(self._trace_index!=0):
            prev_time = self._current_trace_start_time
            self._current_trace_start_time=time.time()
            self._total_trace_time+=self._current_trace_start_time - prev_time
        else:
            self._current_trace_start_time=time.time()
        self._trace_index+=1
        self._elapsed_traces+=1

        if(publish):
            output = ['Frame:', self.get_frame_index(),'/',self.get_Z_points(),self.get_Z_name(),':', format(Z_value,'.2f'),'Trace:', self.get_trace_index(),'/',self.get_Y_points(), self.get_Y_name(),':',format(Y_value,'.2f'),format(100*self.get_trace_fraction(),'.2f'),'%','t:',format(self.get_elapsed_time(),'.2f'),'s','done at:', time.ctime(self.get_est_ready())]
            print("{:>10}{:>3}{:>1}{:>1}{:>15}{:>1}{:>4}{:>10}{:>1}{:>1}{:>1}{:>15}{:>1}{:>5}{:>10}{:>1}{:>10}{:>2}{:>2}{:>15}{:>25}".format(*output))
            #print 'Trace:  \t', self.get_trace_index(), '/', self.get_Y_points(), '\t', round(100*self.get_trace_fraction(),4), '%\t t:', self.get_elapsed_time(), '(s)\t done at: ', time.ctime(self.get_start_time()+self.get_est_ready()) 
    

    def interval(self):
        prev_time = self._interval
        self._interval=time.time()
        return self._interval - prev_time
    
