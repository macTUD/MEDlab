****************************************
*	 Prozeﬂnummer = 1
*	 Delay = 400
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorit‰t = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 4000001
*	 ATSRAM = 0
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
'test.bas: ignore

DIM VNEG AS INTEGER

INIT:
PAR_10 = 100

SET_MUX(0)

EVENT:

DAC(1,PAR_3)

SLEEP(PAR_10)

PAR_4 = ADC(1)

SLEEP(PAR_10)

VNEG = 32768-(PAR_3-32768)

DAC(1,VNEG)

SLEEP(PAR_10)
	
PAR_5 = ADC(1)

FPAR_2 = (PAR_4-PAR_5)/2*ABSI(PAR_3-32768)

PAR_7 = READ_TIMER()
END

FINISH:
	DAC(1,32768)