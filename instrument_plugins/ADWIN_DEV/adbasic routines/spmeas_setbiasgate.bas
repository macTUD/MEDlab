****************************************
*	 Prozeßnummer = 2
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
' spmeas_setbiasgate.bas: ramps voltage on DAC1 and DAC2.

'Inputs:
'PAR_1 = start bias voltage, native units
'PAR_2 = end bias voltage, native units
'PAR_11 = start gate voltage, native units
'PAR_12 = end gate voltage, native units

'Outputs:
'PAR_3 = counter
'PAR_13 = counter

DIM mulbias, mulgate AS LONG
DIM outbias, outgate AS LONG
DIM flag AS INTEGER

LOWINIT:
PAR_3 = 0
PAR_13 = 0
flag = 0

IF(PAR_1>PAR_2) THEN
	mulbias = -1
ELSE
	mulbias = 1
ENDIF

IF(PAR_11>PAR_12) THEN
	mulgate = -1
ELSE
	mulgate = 1
ENDIF

EVENT:
SELECTCASE flag
	CASE 0
		outbias = PAR_1+mulbias*PAR_3
		DAC(1,outbias)
	
		IF(mulbias*(PAR_2-outbias) < 0) THEN
			flag = 1
		ENDIF
	
		PAR_3 = PAR_3 + 1
	CASE 1
		outgate = PAR_11+mulgate*PAR_13
		DAC(2,outgate)
	
		IF(mulgate*(PAR_12-outgate) < 0) THEN
			ACTIVATE_PC
			END
		ENDIF
	
		PAR_13 = PAR_13 + 1
ENDSELECT