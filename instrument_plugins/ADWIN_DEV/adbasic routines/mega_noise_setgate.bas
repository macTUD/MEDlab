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
' mega_setgate.bas: ramps voltage on DAC2.

'Inputs:
'PAR_11 = start voltage, native units
'PAR_12 = end voltage, native units
'PAR_16 = SLEEP time between DAC output and read, in 0.1us units

'Outputs:
'PAR_13 = counter

DIM mul AS LONG
DIM out AS LONG

LOWINIT:
PAR_13 = 0
IF(PAR_11>PAR_12) THEN
	mul = -1
ELSE
	mul = 1
ENDIF

EVENT:
	out = PAR_11+mul*PAR_13
	DAC(2,out)
	
	REM Wait 3 µs for the settling of the multiplexer

	SLEEP(PAR_16)

	IF(mul*(PAR_12-out) < 0) THEN
		ACTIVATE_PC
		END
	ENDIF
	
	PAR_13 = PAR_13 + 1
