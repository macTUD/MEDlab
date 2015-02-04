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
' Simultaneously outputs DAC1 ADC1 into FIFO array
' DATA_1 = dIdV

'inputs:
' PAR_10 = bias
' PAR_1 = off switch
' PAR_4 = threshold for quitting program
'PAR_20 = gain setting (for set_mux command)

DIM DATA_1[20000] AS LONG AS FIFO
DIM DATA_2[20000] AS FLOAT AS FIFO 
DIM DATA_3[65536] as float 'lookup table for current
DIM progstage AS LONG 	'0=sweep to start value
												'1=measure
												'2=sweep to zero and end
DIM measureflag, reverseflag AS LONG
DIM dacinput, adcreadout AS LONG

INIT:
	FIFO_CLEAR(1)
	FIFO_CLEAR(2)
	PAR_1 = 0
	PAR_14=0
	PAR_17=0
	adcreadout = 0
	dacinput = PAR_9
	measureflag = 1
	progstage = 1

'SET_MUX(00 11 000 000b)'use gain of 8 for multiplexer
'SET_MUX(PAR_20)
SET_MUX(0)
'SET_MUX(00 00 000 000b)

'parameters	PAR_10, PAR_1 ... _3 are initialized from labview program

EVENT:
SELECTCASE progstage

	CASE 1	'measure
		IF (PAR_1 = 1) THEN
			progstage = 3
			measureflag = 2
		ENDIF

		SELECTCASE measureflag
			CASE 1 'read ADC 
				START_CONV(1)
				WAIT_EOC(1)
				PAR_5 = READADC(1)		
				FPAR_6= DATA_3[PAR_5]
				DATA_1 = dacinput
				DATA_2 = FPAR_6

				PAR_14=PAR_14+1
				IF ( adcreadout < 32768 ) THEN
					adcreadout = 65536-adcreadout
				ENDIF
				
				'Will skip this condiction for the LOG version.
				'IF (adcreadout < PAR_4) THEN 
				'	PAR_1 = 1
				'ENDIF			
		
			ENDSELECT	
		IF (FIFO_FULL(1)>10000) THEN
			PAR_17=PAR_17+1
			ACTIVATE_PC
		ENDIF	

	
	CASE 3 'fill DATA_1 and DATA_2 until FIFO is full
		DATA_1 = dacinput
		DATA_2 = DATA_3[adcreadout]
		IF (FIFO_FULL(1)>10000) THEN
			ACTIVATE_PC
			END
		ENDIF		
	ENDSELECT