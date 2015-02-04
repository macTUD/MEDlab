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
PAR_3=33096

EVENT:
DAC(1,PAR_3)

FINISH:
	DAC(1,32768)