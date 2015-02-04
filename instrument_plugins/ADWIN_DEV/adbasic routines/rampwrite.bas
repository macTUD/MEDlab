****************************************
*	 Prozeßnummer = 2
*	 Delay = 4000
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorität = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 4000001
*	 ATSRAM = 0
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
' rampwrite.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.
' When resistance drops below FPAR_1% of previous value, reset output to 10mV and start 
' ramp again. Once target resistance is reached, exit program

' This version expects a diode in series with the electromigration sample.
' The curve for current voltage dependence is calculated independently

'Inputs:
'FPAR_1 = percentage threshold for ramp
'FPAR_2 = target resistance (in ohms)

'Ouputs:
'PAR_1 = output voltage in ADC units
'PAR_2 = measured voltage in ADC units
'FPAR_3 = resistance of sample
'FPAR_4 = voltage across sample
'FPAR_5 = current through sample

'Internal variables:
'PAR_3 = flag for read
'PAR_4 = flag for write
'PAR_5 = flag for delay
'PAR_6 = time since begin of program

DIM time,delayflag,delay AS INTEGER

LOWINIT:
	PAR_3 = 0
	PAR_4 = 0
	time = 0
	PAR_5 = 0
	delay = 4000 'in units of 25 ns
	FPAR_3 = 10

EVENT:

	IF (PAR_4 = 1) THEN	
		'continue ramp
		PAR_1 = PAR_1+1
		DAC(1,PAR_1+32768)
		time = 0
		PAR_4 = 0
		PAR_5 = 1
	ENDIF
	
	'increment time in units of 25ns
	IF(PAR_5 = 1) THEN
		time = time+GLOBALDELAY
		IF(time>delay) THEN
			PAR_5 = 0
			PAR_3 = 1
		ENDIF
	ENDIF	
	
	IF(FPAR_3>FPAR_2) THEN
		DAC(1,32768)
		END
	ENDIF
	