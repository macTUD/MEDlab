
import numpy as np
import os
import qt

def full_measure2d(coordinate,value,measure_fn,measure_args):
    #set up data object and plot:
    qt.mstart()
    out = measure_fn(*measure_args) #actual measurement
    data = qt.Data(name=measure_args[5])
    data.add_coordinate('frequency [MHz]')
    data.add_value('magnitude [dBm]')
    data.create_file()
    plot2d = qt.Plot2D(data, name='measure2D')
    data.add_data_point(out[0],out[1])
    data.close_file()
    qt.mend()
    return out

def fsl_basic_measure(fsl, start_frequency=2000, stop_frequency=3000,
                      tracking=False, full_measure=True, filename='fsl_basic_measure'):
    '''
    This function takes a measurement on the FSL.

    Required argument:
    fsl -- the name of the spectrum analyzer. If the spectrum analyzer was created by:
                FSL01 = qt.instruments.create('FSL01','RS_FSL',address='TCPIP::169.254.174.176::INSTR')
                then the name is FSL01 (no quotes). 
    
    Optional arguments:
    filename -- Sets base filename
    start_frequency -- Start frequency in MHz
    stop_frequency -- Stop frequency in MHz``
    '''

    if full_measure:
        return full_measure2d('frequency [MHz]','magnitude [dBm]',fsl_basic_measure,
                       [fsl,start_frequency,stop_frequency,tracking,False,filename])
    else:
        fsl.set_trace_continuous(False)#mstart should do this, but...
        #set all of the parameters:
        fsl.set_start_frequency(start_frequency)
        fsl.set_stop_frequency(stop_frequency)
        fsl.set_tracking(tracking)
        span=stop_frequency-start_frequency
        fsl.get_all()

        trace=fsl.get_trace() #actual measurement
    
        #convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:
        fstep=span/(len(trace)-1.0)
        flist=np.arange(start_frequency,stop_frequency+fstep,fstep)
        output=[flist,trace]
    
        fsl.set_trace_continuous(True)#mend should do this, but...

        return output
                       
def fsl_smb_sweep(fsl,smb,fsl_start_frequency=2000, fsl_stop_frequency=3000,
                  smb_start_frequency=2000,smb_stop_frequency=3000,smb_step_frequency=10,smb_power=-30,
                  filename='fsl_smb_sweep', ):
    '''
    This script sweeps the SMB (signal generator) frequency and takes an FSL measurement at each frequency,
    producing a 2D plot with drive frequency and measuremnt frequency as independent parameters.

    Required arguments:
    fsl -- name of the fsl (see fsl_basic_measure() for more detail)
    smb -- name of smb

    FSL arguments:
    fsl_start_frequency: lowest measurement frequency (MHz)
    fsl_stop_frequency: highest measurement frequency (MHz))

    SMB arguments:
    smb_start_frequency: lowest drive frequency (MHz)
    smb_stop_frequency: highest drive frequency (MHz)
    smb_step_frequency: increment of drive frequency (MHz)
    smb_power: power at the SMB RF output (dBm)
    '''
    qt.mstart()

    #set SMB parameters:
    smb.set_RF_state(False)#Turn off output while changing settings to be safe
    smb.set_RF_frequency(smb_start_frequency)
    smb.set_RF_power(smb_power)
    smb.set_RF_state(True)
    smb.get_all()

    #set up data object and plot:
    data = qt.Data(name=filename)
    data.add_coordinate('measurement frequency [MHz]')
    data.add_coordinate('drive frequency [MHz]')
    data.add_value('magnitude [dBm]')
    data.create_file()

    plot2d = qt.Plot2D(data, name='measure2D')
    plot3D = qt.Plot3D(data, name='measure3D')

    #Actual measuremnt
    for drive_frequency in np.arange(smb_start_frequency,smb_stop_frequency,smb_step_frequency):
        smb.set_RF_frequency(drive_frequency)
        qt.msleep(0.1) #Allow transients to settle for 100ms.
        out=fsl_basic_measure(fsl,fsl_start_frequency,fsl_stop_frequency,False,False,filename)
        data.add_data_point(out[0],[drive_frequency]*len(out[0]),out[1])
        data.new_block()
    data.close_file()
    fsl.set_trace_continuous(True)#mend should do this, but...
    qt.mend()
        
        
        
        

    
