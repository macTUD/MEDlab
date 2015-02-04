****************************************
*	 Prozeﬂnummer = 1
*	 Delay = 400
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorit‰t = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 3020001
*	 ATSRAM = 0
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
'test.bas: ignore

INIT:
PAR_5 = 0
PAR_6 = 0
PAR_7 = 0 'set voltage = 0, measure voltage = 1

EVENT:
IF( (PAR_5=0) AND (PAR_6<2) ) THEN
	IF( PAR_6=0 )	THEN
		IF( PAR_7=0 ) THEN
			DAC(1,PAR_1)
			PAR_7 = 1
		ELSE
			SET_MUX(0)
			START_CONV(1)
			WAIT_EOC(1)
			PAR_2 = READADC(1)
		
			PAR_6 = 1
			PAR_7 = 0
		ENDIF
	ELSE
		IF( PAR_7=0 ) THEN
			DAC(1,PAR_3)
			PAR_7 = 1
		ELSE
			SET_MUX(0)
			START_CONV(1)
			WAIT_EOC(1)
			PAR_4 = READADC(1)

			PAR_6 = 2
			PAR_7 = 0
			FPAR_2 = (PAR_2-PAR_4)/(PAR_1-PAR_3)
			END
		ENDIF
	ENDIF
ENDIF
FINISH:
	DAC(1,32768)