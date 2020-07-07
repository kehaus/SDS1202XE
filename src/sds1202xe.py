# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 23:26:20 2020

@author: Administrator
"""

import time

from visa_baseclass import VISABaseClass

# ===========================================================================
# SDS1202XE
# ===========================================================================
class SDS1202XEException(Exception):
    """ """
    pass


class SDS1202XE(VISABaseClass):
    """ """
    
    CHANNELS = [1,2]
    SARA_UNIT = {'G':1E9,'M':1E6,'k':1E3}
    TRIG_MODE = {'AUTO', 'NORM', 'SINGLE', 'STOP'}
    
    def _check_channel_value(self, channel):
        if not channel in self.CHANNELS:
            raise SDS1202XEException(
                'Given channel: {} is not a valid value'.format(channel) +
                'Try instead: {}'.format(self.CHANNELS)
            )
        return
    
    def _check_trigger_mode_value(self, mode):
        if not mode in self.TRIG_MODE:
            raise SDS1202XEException(
                'Given mode: {} is not a valid mode'.format(mode) + 
                'Try instead: {}'.format(self.TRIG_MODE)
            )
        
    def _parse_sara_value(self, sara, sara_unit=None):
        """convert the sara string returned from the DSO to a float value
        
        Can be used in combination with the `get_sara()` function.
        """
        if sara_unit == None:
            sara_unit = self.SARA_UNIT
        
        for unit in sara_unit.keys():
            if sara.find(unit)!=-1:
                sara = sara.split(unit)
                sara = float(sara[0])*sara_unit[unit]
                break
        sara = float(sara)
        return sara
    
    # =========
    # high-level functions
    # =========
    
    def get_operation_complete(self):
        scpi_cmd = '*opc?'
        return self.query(scpi_cmd) 
    
    def stop_acquisition(self):
        self.write('stop')

    def get_sample_status(self):
        """returns acquisition status of the scope"""
        scpi_cmd = 'SAST?'
        return self.query(scpi_cmd).lower()
    
    def get_voffset(self, channel):
        self._check_channel_value(channel)
        scpi_cmd = 'c{}:ofst?'.format(channel)
        return self.query(scpi_cmd)
    
    def get_vdiv(self, channel):
        self._check_channel_value(channel)
        scpi_cmd = 'c{}:vdiv?'.format(channel)
        return self.query(scpi_cmd)
    
    def get_tdiv(self):
        scpi_cmd = 'tdiv?'
        return self.query(scpi_cmd)
    
    def get_sara(self):
        """returns sample rate of the scope"""
        scpi_cmd = 'sara?'
        return self.query(scpi_cmd)
    
    def get_sample_rate(self):
        """returns sample rate as float value"""
        sara = self.get_sara()
        return self._parse_sara_value(sara)
    
    def get_internal_state_change_register(self):
        """returns and clears the internal state change register (INR)
        
        The INR register records the completion of various internal operations 
        and state transitions
        
        """
        scpi_cmd = 'INR?'
        return float(self.query(scpi_cmd))
    
    def get_trigger_mode(self):
        scpi_cmd = 'TRMD?'
        return self.query(scpi_cmd)
    
    def set_trigger_mode(self, mode):
        self._check_trigger_mode_value(mode)
        scpi_mode = 'TRMD {}'.format(mode)
        self.write(scpi_mode)
    
    def arm_acquisition(self):
        scpi_cmd = 'ARM'
        self.write(scpi_cmd)
    
    def get_both_waveform(self):
        self.stop_acquisition()
        t1, v1 = self.get_waveform(1)
        t2, v2 = self.get_waveform(2)
        return t1, v1, t2, v2
    
    def get_waveform(self, channel):
        """transfers measurement data from oscilloscope to computer"""
        self._check_channel_value(channel)
        
        # get measurement information
        self.write("chdr off")
        vdiv = self.get_vdiv(channel)
        ofst = self.get_voffset(channel)
        tdiv = self.get_tdiv()
        sara = self.get_sample_rate()

        # set communication settings
        self.inst.timeout = 30000  #default value is 2000(2s)
        self.inst.chunk_size = 20*1024*1024 #default value is 20*1024(20k bytes)
        
        # get data from DSO; remove unwated entries 
        scpi_cmd = 'c{}:wf? dat2'.format(channel)
        self.write(scpi_cmd)
        
        raw_values = list(self.read_raw())[15:]
        raw_values.pop()
        raw_values.pop()
    
        # shift data values
        volt_values = []
        for val in raw_values:
            if val > 127:
                val -= 255
            else:
                pass
            volt_values.append(val)

        # get time information
        time_values = []
        grid = 14 # DSO display divides the time axis into 14 division
        for idx in range(len(volt_values)):
            # convert to actual voltage values
            volt_values[idx] = volt_values[idx]*float(vdiv)/25-float(ofst)
            # reconstruct time steps
            time_val = -(float(tdiv)*grid/2)+idx*(1/sara)
            time_values.append(time_val)
    
        return time_values, volt_values
    
    def acquire_waveform(self, channel):
        
        self.set_trigger_mode('SINGLE')
        status = self.get_sample_status()
        while not status == 'stop':
            time.sleep(0.1)
            status = self.get_sample_status()
        
        t, v = self.get_waveform(channel)
        return t,v
    
    def acquire_both_waveform(self):
        
        self.set_trigger_mode('SINGLE')
        status = self.get_sample_status()
        while not status == 'stop':
            time.sleep(1)
            status = self.get_sample_status()

        t1, v1 = self.get_waveform(1)
        t2, v2 = self.get_waveform(2)
        return t1, v1, t2, v2



# ===========================================================================
# 
# ===========================================================================
if __name__ == "__main__":
    protocol = 'USB0'
    addr = '0xF4ED::0xEE3A::SDS1ECDX2R3290'
    sds = SDS1202XE(protocol, addr)
    
    
    
    