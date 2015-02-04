'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = TUD203410  DASTUD\TUD203410
'<Header End>
'ADBasic program corresponding to the ADwin_DAC.py driver
'Sal J. Bosman 2013, s.bosman@tudelft.nl, saljuabosman@mac.com  

'OUTPUT PARAMETERS
'PAR_1      OUT 1
'PAR_2      OUT 2
'PAR_3      OUT 3
'PAR_4      OUT 4

'PAR_21     TARGET OUT 1
'PAR_22     TARGET OUT 2
'PAR_23     TARGET OUT 3
'PAR_24     TARGET OUT 4

'PAR_11     external on-off button
'PAR_10     UNIVERSAL GLOBAL DELAY
'PAR_12     rampstep

'After calibration we found that 1Volt is equal to 3277 something



INIT:
  PAR_10 = 10000
  
  PAR_12 = 1           '1.2V/S
  'set all DACs to (nearly) zero
  PAR_1 = 32768
  PAR_2 = 32768
  PAR_3 = 32768
  PAR_4 = 32768
  
  PAR_21 = 32768
  PAR_22 = 32768
  PAR_23 = 32768
  PAR_24 = 32768
    

EVENT:
  GLOBALDELAY = PAR_10   'every PAR_10*25ns a sample is taken 4kHz
  
  'RAMP DAC 1
  If (Absi(PAR_21-PAR_1)>PAR_12) Then 'the target Voltage is 
    'is too far from the current voltage to set it in once
    'step voltage
    If(PAR_1 > PAR_21) Then
      PAR_1 = PAR_1-PAR_12 'step lower
    Else
      PAR_1 = PAR_1 +PAR_12 'step higher
    EndIf
    
  Else
    PAR_1=PAR_21 
  EndIf
  
  'RAMP DAC 2
  If (Absi(PAR_22-PAR_2)>PAR_12) Then 'the target Voltage is 
    'is too far from the current voltage to set it in once
    'step voltage
    If(PAR_2 > PAR_22) Then
      PAR_2 = PAR_2-PAR_12 'step lower
    Else
      PAR_2 = PAR_2 +PAR_12 'step higher
    EndIf
    
  Else
    PAR_2=PAR_22 
  EndIf
  
  'RAMP DAC 3
  If (Absi(PAR_23-PAR_3)>PAR_12) Then 'the target Voltage is 
    'is too far from the current voltage to set it in once
    'step voltage
    If(PAR_3 > PAR_23) Then
      PAR_3 = PAR_3-PAR_12 'step lower
    Else
      PAR_3 = PAR_3 +PAR_12 'step higher
    EndIf
    
  Else
    PAR_3=PAR_23 
  EndIf
  
  'RAMP DAC 4
  If (Absi(PAR_24-PAR_4)>PAR_12) Then 'the target Voltage is 
    'is too far from the current voltage to set it in once
    'step voltage
    If(PAR_4 > PAR_24) Then
      PAR_4 = PAR_4-PAR_12 'step lower
    Else
      PAR_4 = PAR_4 +PAR_12 'step higher
    EndIf
    
  Else
    PAR_4=PAR_24 
  EndIf
  
  'SET DACS
     
  DAC(1, PAR_1)
  DAC(2, PAR_2)
  DAC(3, PAR_3)
  DAC(4, PAR_4)
  
