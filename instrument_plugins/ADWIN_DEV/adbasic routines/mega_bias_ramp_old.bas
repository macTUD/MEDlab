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
' mega_bias_ramp.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.

'Inputs:
'PAR_1 = start voltage
'PAR_2 = end voltage
'PAR_6 = SLEEP time between DAC output and read, in 0.1us units

'Outputs:
'DATA_1 = voltage array
'DATA_2 = current array
'PAR_3 = length of data array
'PAR_4 = start time in native units
'PAR_5 = end time in native units

#DEFINE PI 3.14159265 
DIM DATA_1[50000] as integer 
DIM DATA_2[50000] as integer
DIM counter as integer

LOWINIT:
PAR_3 = 0
SET_MUX(0)

EVENT:

	DATA_1[PAR_3] = PAR_1+PAR_3
	DAC(1,DATA_1[PAR_3])
	
	REM Wait 3 µs for the settling of the multiplexer
	IF( PAR_3=0 ) THEN
		SLEEP(2000)
		PAR_4 = READ_TIMER()
	ENDIF

	SLEEP(PAR_6)

	START_CONV(1)
	WAIT_EOC(1)
	DATA_2[PAR_3] = READADC(1)

	IF( ((PAR_1+PAR_3)>PAR_2) OR (PAR_3>49999)) THEN
		PAR_5 = READ_TIMER()
		ACTIVATE_PC
		DAC(1,32768)
		END
	ENDIF
	
	PAR_3 = PAR_3 + 1
