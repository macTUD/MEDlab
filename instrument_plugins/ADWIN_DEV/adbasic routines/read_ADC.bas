****************************************
*	 Prozeﬂnummer = 2
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

DIM counter AS INTEGER
DIM loopflag AS INTEGER

INIT:
counter = 0
loopflag = 1
SET_MUX(0)

EVENT:
SELECTCASE loopflag
		CASE 1
			DAC(1,32768)
			loopflag = 2
			'FOR counter = 1 TO 100
			'NEXT counter
		CASE 2
			START_CONV(1)
			WAIT_EOC(1)
			PAR_23 = READADC(1)
			'PAR_23=ADC(1)
			loopflag = 3
		CASE 3
			END
ENDSELECT

FINISH:
	DAC(1,32768)