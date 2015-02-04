****************************************
*	 Prozeßnummer = 1
*	 Delay = 400
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
' reads ADC1 and adjusts DAC to give positiveor negative PAR_10 
' on DAC1; simultaneously outputs DAC1 ADC1 into FIFO array
' DATA_1 = dIdV

'inputs:
' PAR_10 = bias
' PAR_1 = off switch
' PAR_2 = threshold for switching from +ve to -ve
' PAR_3 = threshold for switching from -ve to +ve
' PAR_4 = threshold for quitting program

DIM DATA_1[20000],DATA_2[20000] AS LONG AS FIFO
DIM progstage AS LONG 	'0=sweep to start value
												'1=measure/change pol
												'2=sweep to zero and end
DIM measureflag, reverseflag AS LONG
DIM dacinput, adcreadout AS LONG

INIT:
	FIFO_CLEAR(1)
	FIFO_CLEAR(2)
	PAR_1 = 0
	adcreadout = 0
	dacinput = 32768
	measureflag = 1
	reverseflag = 0
	progstage = 0

'parameters	PAR_10, PAR_1 ... _3 are initialized from labview program

EVENT:
SELECTCASE progstage
	CASE 0	'sweep to start value
		IF (PAR_10 > 32768) THEN
			INC(dacinput)
		ELSE
			DEC(dacinput)
		ENDIF
		DAC(1,dacinput)
		IF(dacinput = PAR_10) THEN 
			progstage = 1
		ENDIF
	CASE 1	'measure/change pol
		IF (PAR_1 = 1) THEN
			progstage = 2
			measureflag = 2
		ENDIF

		SELECTCASE measureflag
			CASE 0 'reset dac
				IF (((reverseflag=1) AND (PAR_10>32768)) OR ((reverseflag=0) AND (PAR_10<32768))) THEN
					DEC(dacinput)
				ELSE
					INC(dacinput)
				ENDIF
				DAC(1,dacinput)
				IF((dacinput = PAR_10) OR (dacinput = (65535-PAR_10))) THEN
					measureflag = 1
				ENDIF
			CASE 1 'read ADC 
				START_CONV(3)
				WAIT_EOC(3)
				adcreadout = READADC(1)		

				DATA_1 = dacinput
				DATA_2 = adcreadout

				IF ( adcreadout < 32768 ) THEN
					adcreadout = 65536-adcreadout
				ENDIF

				IF (adcreadout < PAR_4) THEN
					PAR_1 = 1
				ELSE
					SELECTCASE reverseflag
						CASE 0
							IF ( adcreadout < PAR_2 ) THEN
								reverseflag = 1
								measureflag = 0
							ENDIF
						CASE 1
							IF ( adcreadout > PAR_3 ) THEN
								reverseflag = 0
								measureflag = 0
							ENDIF
					ENDSELECT	
				ENDIF			
			ENDSELECT
		
		IF (FIFO_FULL(1)>10000) THEN
			ACTIVATE_PC
		ENDIF

	CASE 2	'sweep to zero + end
		IF (((reverseflag=0) AND (PAR_10>32768)) OR ((reverseflag=1) AND (PAR_10<32768))) THEN
			DEC(dacinput)
		ELSE
			INC(dacinput)
		ENDIF
		DAC(1,dacinput)
		IF(dacinput = 32768) THEN
			progstage = 3
		ENDIF
	
	CASE 3 'fill DATA_1 and DATA_2 until FIFO is full
		DATA_1 = dacinput
		DATA_2 = adcreadout
		IF (FIFO_FULL(1)>10000) THEN
			ACTIVATE_PC
			END
		ENDIF		
	ENDSELECT