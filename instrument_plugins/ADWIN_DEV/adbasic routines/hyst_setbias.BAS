****************************************
*	 Prozeßnummer = 2
*	 Delay = 1000
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorität = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 4000001
*	 ATSRAM = 0
*	 OPT_LEVEL = 1
*	 SAVECOMPIL = 0
****************************************
'SET BIAS TO DESIRED VALUE OR SET BIAS DOWN TO ZERO
'

DIM dacinput, dacdown,action AS long

INIT:
	dacinput = 32768
	dacdown=PAR_10
	action=PAR_7

SET_MUX(0)

EVENT:
SELECTCASE action
	CASE 0	'sweep to start value
		PAR_11=10
		IF (PAR_10 > 32768) THEN
			INC(dacinput)
		ELSE
			DEC(dacinput)
		ENDIF
		DAC(1,dacinput)
		PAR_9=dacinput
		IF(dacinput = PAR_10) THEN 
			ACTIVATE_PC
			END
		ENDIF
	CASE 1 'Sweep down to Zero
		PAR_11=20
		IF (PAR_10>32768) THEN
			DEC(dacdown)
		ELSE
			INC(dacdown)
		ENDIF
		DAC(1,dacdown)
		PAR_9=dacdown
		IF(dacdown = 32768) THEN
			ACTIVATE_PC
			END
		ENDIF
ENDSELECT