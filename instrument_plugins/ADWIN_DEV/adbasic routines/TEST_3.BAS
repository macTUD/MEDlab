****************************************
*	 Prozeßnummer = 1
*	 Delay = 400
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorität = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 3020001
*	 ATSRAM = 0
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
'test.bas: ignore
INIT:
PAR_6 = 0
PAR_9 = 4000 'delay time=10us
PAR_10 = 0 	'reset flags to 0
PAR_11 = 0
PAR_12 = 0

EVENT:
IF( PAR_6=0 )	THEN
	IF( PAR_10=0 ) THEN
		DAC(1,PAR_3)
		PAR_10 = 1
		PAR_13 = READ_TIMER()
	ENDIF
	IF( (PAR_10=1) AND ((READ_TIMER()-PAR_13)>PAR_9)) THEN
		PAR_10=2
	ENDIF
	IF( (PAR_10=2) AND (PAR_11=0) ) THEN
		SET_MUX(0)
		START_CONV(1)
		WAIT_EOC(1)
		PAR_4 = READADC(1)

		DAC(1,(32768 -(PAR_3-32768)))
		PAR_11 = 1
		PAR_13 = READ_TIMER()
	ENDIF
	IF( (PAR_11=1) AND ((READ_TIMER()-PAR_13)>PAR_9)) THEN
		PAR_11=2
	ENDIF
	IF(PAR_11=2) THEN
		SET_MUX(0)
		START_CONV(1)
		WAIT_EOC(1)
		PAR_5 = READADC(1)

		FPAR_2 = (PAR_4-PAR_5)/(2*ABSI(PAR_3-32768))

		PAR_7 = READ_TIMER()
		END
	ENDIF
ENDIF

FINISH:
	DAC(1,32768)