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
' Info_Last_Save                 = TUD202834  TUD202834\LocalAdmin
'<Header End>
'ADBasic program corresponding to the ADwin_DAC.py driver
'Sal J. Bosman 2013, s.bosman@tudelft.nl, saljuabosman@mac.com
'Ben H. Schneider 2013, b.h.schneider@tudelft.nl

'OUTPUT PARAMETERS
'PAR_1      OUT 1
'PAR_2      OUT 2
'PAR_3      OUT 3
'PAR_4      OUT 4
'PAR_21     TARGET OUT 1
'PAR_22     TARGET OUT 2
'PAR_23     TARGET OUT 3
'PAR_24     TARGET OUT 4

'INPUT PARAMETERS
'PAR_5      IN 1
'PAR_6      IN 2
'PAR 9      sets the average factor
'dimensions and variables:
DIM avg_1 As LONG                
DIM avg_2 As LONG
DIM val,var AS INTEGER

'GENERAL PARAMETERS
'PAR_11     external on-off button
'PAR_10     UNIVERSAL GLOBAL DELAY
'PAR_12     rampstep
'PAR 13     selection: READ ADC INPUT (1), SET DAC OUTPUT (2)
'After calibration we found that 1Volt is equal to 3277 something
'DIM totalcurrent AS LONG

INIT:
  PAR_13 = 1 'start with setting dacs to 0 (after reading the dacs)
  PAR_10 = 5000 'set the Processdelay speed
  PAR_12 = 1           '1.2V/Sec
  
  'Output parameters
  'set all DACs to (nearly) zero
  PAR_1 = 32768
  PAR_2 = 32768
  PAR_3 = 32768
  PAR_4 = 32768
  
  PAR_21 = 32768
  PAR_22 = 32768
  PAR_23 = 32768
  PAR_24 = 32768

  
  'Input parameters
  PAR_9 = 10034 
  PAR_14 = 0 
  avg_1 = 0
  avg_2 = 0
  'Processdelay = 250 'is the minimum
EVENT:
  'READ ADC INPUT (1)
  IF (PAR_13 = 1) THEN
    Processdelay = 250
    avg_1 = 0
    avg_2 = 0
    'Set_Mux(10 10 000 000b) 'Set multiplexer (s.a.)
    'START_CONV(2)                      'Start AD-conversion ADC1
    'WAIT_EOC(2)                         'Wait for end of conversion of ADC1
    FOR  var = 1 TO PAR_9 'do Par 9 times an average
      START_CONV(2)
      WAIT_EOC(2)
      'avg_1 = avg_1 + ReadADC(1)
      avg_2 = avg_2 + ReadADC(2)
    NEXT var
    'finishing (prepare results and clear parameters)
    PAR_5 = avg_1/PAR_9 
    PAR_6 = avg_2/PAR_9
    PAR_13 = 2 'finish the reading and go back to setting the DACs
  ENDIF
  
  'SET DAC OUTPUT (2)
  IF (PAR_13 = 2) THEN
    Processdelay = PAR_10   'every PAR_10*25ns a sample is taken 4kHz
  
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
  ENDIF
