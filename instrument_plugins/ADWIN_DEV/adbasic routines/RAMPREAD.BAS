****************************************
*	 Prozeßnummer = 1
*	 Delay = 40000
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
' rampread.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.
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

DIM startvol,time,starttime AS INTEGER
DIM V_out, V_meas, lastres AS FLOAT
#DEFINE PI 3.14159265 

LOWINIT:
	'make startvol 500mV
	startvol = 1638
	PAR_1 = startvol
	lastres = 10 'make it 10 ohms to begin with
	PAR_3 = 0
	PAR_4 = 0
	PAR_5 = 0
	FPAR_3 = 10
	starttime = READ_TIMER()

EVENT:
	IF(PAR_3 = 1) THEN
	
		V_out = 10.0*PAR_1/32768
		SET_MUX(0)
		START_CONV(1)
		WAIT_EOC(1)
		PAR_2 = READADC(1)-32768

		V_meas = 10.0*PAR_2/32768
		FPAR_4 = 10.0*(PAR_1-PAR_2)/32768
		FPAR_5 = EXP(-19.49284+21.31082*V_meas-1.1237*V_meas^2)
		FPAR_3 = FPAR_4/FPAR_5
		PAR_6 = READ_TIMER()-starttime
	
		ACTIVATE_PC
		PAR_3 = 0
	ELSE
		IF (PAR_5 = 0) THEN
			PAR_4 = 1
		ENDIF
	ENDIF

	IF(FPAR_3>1.0+(FPAR_1*lastres)/100)THEN
		PAR_1 = startvol
		lastres = FPAR_3
	ENDIF
	IF(FPAR_3>FPAR_2) THEN
		END
	ENDIF
