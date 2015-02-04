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
PAR_6 = 4000 'delay time in 25ns increments

EVENT:
DAC(1,PAR_1)
PAR_5 = READ_TIMER()
DO
	'wait
UNTIL  ((READ_TIMER()-PAR_5)>PAR_6)

SET_MUX(0)
START_CONV(1)
WAIT_EOC(1)
PAR_2 = READADC(1)
		
DAC(1,PAR_3)

PAR_5 = READ_TIMER()
DO
	'wait
UNTIL ((READ_TIMER()-PAR_5)>PAR_6)

SET_MUX(0)
START_CONV(1)
WAIT_EOC(1)
PAR_4 = READADC(1)
FPAR_2 = (PAR_2-PAR_4)/(PAR_1-PAR_3)
END

FINISH:
	DAC(1,32768)