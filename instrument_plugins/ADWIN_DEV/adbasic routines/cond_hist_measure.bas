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
*	 OPT_LEVEL = 1
*	 SAVECOMPIL = 0
****************************************
' measures voltage on first 2 ADCs simultaneously. Sampling rate is specified Global_Delay
'
' runs as process 2 
'
' CONVENTIONS:
' delay between readings is set by GLOBALDELAY, 
' so for 40,000, total reading time becomes 1 sec, 
' size of data arrays is 1000

DIM counter AS INTEGER

INIT:
	GLOBALDELAY = 400	'cycle-time of 0.01ms

	SET_MUX(0)							' Set Multiplexer of ADC1 and ADC2 to read 1 and 2
	counter = 1                   ' set counter
	PAR_1 = 0
	
EVENT:
	START_CONV(3)         
	WAIT_EOC(3)
	PAR_1 = READADC(1)    

	INC(counter)							' increase counter

	IF (counter > 1) THEN 	     ' stop if all measurement points have been taken
		ACTIVATE_PC
		END
	ENDIF
