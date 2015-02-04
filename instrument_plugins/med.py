from instrument import Instrument
import types
import logging

class med(Instrument):

    def __init__(self, name, address=None, reset=False):
        Instrument.__init__(self, name, tags=['measure', 'med'])

        # minimum
        self.add_parameter('temperature', type=types.FloatType,
                flags=Instrument.FLAG_GETSET,Units='K')

        self.add_parameter('device', type=types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('setup', type=types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('user', type=types.StringType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('current_gain', type=types.FloatType,
                flags=Instrument.FLAG_GETSET,Units='GV/A=mV/pA')

        self.add_parameter('measurement_time', type=types.StringType,
                flags=Instrument.FLAG_GETSET,Units='h:m:s')

        self.add_parameter('sweep_time', type=types.StringType,
                flags=Instrument.FLAG_GETSET,Units='h:m:s')

        self.add_parameter('frame_time', type=types.StringType,
                flags=Instrument.FLAG_GETSET,Units='h:m:s')

        self.add_function('get_all')

        if reset:
            self.reset()

    def reset(self):
        self._temperature = 0
        self._device = ''
        self._setup = ''
        self._user = ''
        self._current_gain = 0
        self._measurement_time = ''

    def get_all(self):

        self.get_temperature()
        self.get_device()
        self.get_setup()
        
        return True

    def do_get_temperature(self):
        return self._temperature

    def do_get_device(self):
        return self._device

    def do_get_setup(self):
        return self._setup

    def do_get_user(self):
        return self._user

    def do_get_current_gain(self):
        return self._current_gain

    def do_get_measurement_time(self):
        return self._measurement_time

    def do_set_temperature(self, val):
        self._temperature = val

    def do_set_device(self, val):
        self._device = val

    def do_set_setup(self, val):
        self._setup = val

    def do_set_user(self, val):
        self._user = val

    def do_set_current_gain(self, val):
        self._current_gain = val

    def do_set_measurement_time(self, val):
        self._measurement_time = val

    def do_set_frame_time(self,val):
        self._frame_time =val

    def do_set_sweep_time(self,val):
        self._sweep_time =val

    def do_get_frame_time(self):
        return self._frame_time

    def do_get_sweep_time(self):
        return self._sweep_time
