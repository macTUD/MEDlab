from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

###########################
# Make instances available
###########################

import qt



ivvi = qt.instruments.get('ivvi')
gates = qt.instruments.get('gates')
keithley1 = qt.instruments.get('keithley1')
keithley2 = qt.instruments.get('keithley2')



def set_dacs_to_zero():
    print 'Set all dacs to zero...'
    for n in range(16):
        print 'dac%s....'%(n+1),
        print ivvi.set('dac%s'%(n+1),0)
        
def sweep_voltage_measure_current(vstart=-150,vend=50,vstep=1,dacNo=3,keithleyNo=1,Naverage=1,Nrepeat=1, R_feedback_QPC = 10e6, nplc=1, plotting=True,title=''):
    
    qt.mstart()
    filename = 'IV curve dac%s' %dacNo 
    filename=filename+title
    keithley1.set_nplc(nplc)
    keithley2.set_nplc(nplc)

    
    data = qt.Data(name=filename)
    if dacNo==3 or dacNo==4:
        data.add_coordinate('dac%s (muV)' % dacNo)
    else:
        data.add_coordinate('dac%s (mV)' % dacNo)
    data.add_coordinate('Repeat')
    if keithleyNo==2:
        data.add_value('QPC2 Current (pA)')
        data.add_value('QPC1 Current (pA)')
    elif keithleyNo==1:
        data.add_value('QPC1 Current (pA)')
        data.add_value('QPC2 Current (pA)')
    data.create_file()
    
    
    if plotting:
        plot2d = qt.Plot2D(data, name=filename)
    

    
    v_vec=arange(vstart,vend,vstep)
    
    for cnt in range(Nrepeat):
        for vcnt,v_sweep in enumerate(v_vec):
            if dacNo==3:
                ivvi.set_dac3(v_sweep)
                dacConv=1
            elif dacNo==4:
                ivvi.set_dac4(v_sweep)
                dacConv=1
            else:
                ivvi.set('dac%s'%dacNo,mncnt)
                dacConv=1e3
            
            result_QPC1 = 0.0
            result_QPC2 = 0.0
            for repeat in arange(0,Naverage,1): 
                # raw_input('key...')
                result_QPC2 = result_QPC2 + keithley2.get_readnextval()  
                result_QPC1 = result_QPC1 + keithley1.get_readnextval()            
                qt.msleep(0.02)
            
            current_QPC1 = result_QPC1*1e12/(Naverage*R_feedback_QPC) # picoampere
            current_QPC2 = result_QPC2*1e12/(Naverage*R_feedback_QPC) # picoampere
            
            
            
            
            if keithleyNo==2:
                data.add_data_point(v_sweep,cnt+1,current_QPC2,current_QPC1)
                if vcnt==0:
                    current_start=current_QPC2
            elif keithleyNo==1:
                data.add_data_point(v_sweep,cnt+1,current_QPC1,current_QPC2)
                if vcnt==0:
                    current_start=current_QPC1
            
    if keithleyNo==2:
        Res=(vend-vstart)*1e-6*dacConv/((current_QPC2-current_start)*1e-12)   #mV/picoAmp
        current_end=current_QPC2
    elif keithleyNo==1:
        Res=(vend-vstart)*1e-6*dacConv/((current_QPC1-current_start)*1e-12)
        current_end=current_QPC1
    
    print 'I1= %s  , I2=%s , I2-I1=%s ,deltaV=%s,Res=%s'%(current_start,current_end,(current_end-current_start),(vend-vstart),Res)    
    print 'Res=',Res/1e3,' KOhm'
    print 'Res=',Res/1e6,' MOhm'
        
    if plotting:
        plot2d.save_png()
    data._write_settings_file()

    data_array = data.get_data()

    data.close_file()
    qt.mend()    
def set_dacs(Value=0):
    print 'Set all dacs to %s...'%(Value)
    NotCoarseGates=[12 ,6,10,8,3,4]   #these are the dacs which I am not using for sweeping 
    for dacCnt in array(range(16))+1:
        print 'dac%s....'%(dacCnt),
        if dacCnt in NotCoarseGates:
            print 'False (becuase it is either Ohmic or fine gate) then set to 0...',
            print ivvi.set('dac%s'%(dacCnt),0)
        else:
            print ivvi.set('dac%s'%(dacCnt),Value)

def set_dacs_and_Measure_Current(Value=0,keithleyNo=1,biasCooling=False,nplc=1, R_feedback_QPC = 10e6,waittime=1,plotting=True,title=''):
    print 'Set all dacs to %s... and measure current'%(Value)
    NotCoarseGates=[12 ,6,10,8,3,4]
    
    qt.mstart()
    filename = 'IV curve as a function of time gates are at %s mV, SL,SR=200mV' %Value 
    filename=filename+title
    keithley1.set_nplc(nplc)
    keithley2.set_nplc(nplc)
    
    data = qt.Data(name=filename)
    data.add_coordinate('Time (s)' )
    
    data.add_coordinate('Repeat')
    if keithleyNo==2:
        data.add_value('QPC2 Current (pA)')
        data.add_value('QPC1 Current (pA)')
    elif keithleyNo==1:
        data.add_value('QPC1 Current (pA)')
        data.add_value('QPC2 Current (pA)')
    data.create_file()
    
    
    if plotting:
        plot2d = qt.Plot2D(data, name=filename)
    
    infinitLoop=True
    GatesAreNotSet=False
    cnt=0
    FinalValue=Value
    
    while infinitLoop:
        cnt=cnt+1
        if GatesAreNotSet:
            if biasCooling:
                if cnt<31:
                    Value=cnt*10
                    print Value
                if cnt==30:
                    GatesAreNotSet=False
            for dacCnt in array(range(16))+1:
                print 'dac%s....'%(dacCnt),
                if dacCnt in NotCoarseGates:
                    print 'False (becuase it is either Ohmic or fine gate) then set to 0...',
                    print ivvi.set('dac%s'%(dacCnt),0)
                elif dacCnt in [15,16]:
                    if Value>200:
                        print 'No change above 200mV'
                    else:
                        print ivvi.set('dac%s'%(dacCnt),Value)
                else:
                    print ivvi.set('dac%s'%(dacCnt),Value)
            
            
        qt.msleep(waittime)
        result_QPC2 = keithley2.get_readnextval()  
        result_QPC1 = keithley1.get_readnextval()            
        qt.msleep(0.02)
        
        current_QPC1 = result_QPC1*1e12/(R_feedback_QPC) # picoampere
        current_QPC2 = result_QPC2*1e12/(R_feedback_QPC) # picoampere
        
        if keithleyNo==2:
            data.add_data_point(waittime*cnt,1,current_QPC2,current_QPC1)
        elif keithleyNo==1:
            data.add_data_point(waittime*cnt,1,current_QPC1,current_QPC2)
        
        
        

            
if (__name__ == '__main__'):
    title='_LS_withoutBonding'
    Amp=1  #100V/V of M2m module
    sweep_voltage_measure_current(vstart=-50,vend=50,vstep=1,keithleyNo=2,Naverage=1,dacNo=11,R_feedback_QPC=Amp*10e6,title=title)
    ivvi.set_dac3(0)
    set_dacs_to_zero()
    