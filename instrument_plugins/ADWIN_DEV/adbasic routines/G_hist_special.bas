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
' reads ADC1 and determines conductance
' simultaneously into FIFO array
' DATA_1 = FIFO array of current

'ínputs:
'PAR_10 = bias offset
'PAR_1 = off switch
'PAR_2 = flag
'FPAR_1 = lowest current

'define variables
DIM DATA_1[10000] AS FLOAT AS FIFO 'array of currents
DIM DATA_2[65536] AS FLOAT 'lookup table for current
DIM counter, measureflag, descendflag AS LONG
DIM adcreadout, dacout, upordown AS INTEGER
DIM current AS FLOAT

INIT:
	FIFO_CLEAR(1)
	PAR_1 = 0
	PAR_2 = 0
	measureflag = 0
	descendflag = 0
	dacout = 32768
	IF (PAR_10>32768) THEN
		upordown = 1
	ELSE
		upordown = -1
	ENDIF

'parameters	are initialized from labview program

EVENT:
	SELECTCASE measureflag
		CASE 0 'sweep DAC to starting value
			IF (dacout = PAR_10) THEN
				DAC(1,dacout)
				measureflag = 1
			ELSE
				DAC(1,dacout)
				dacout = dacout + upordown*1
			ENDIF
		CASE 1 'read ADC 
			START_CONV(3)
			WAIT_EOC(3)
			adcreadout = READADC(1)
					
			current = DATA_2[adcreadout]
			DATA_1 = current
		
			IF(current<FPAR_1) THEN
				PAR_2 = 1
			ENDIF
			
			IF (FIFO_FULL(1)>1000) THEN
				ACTIVATE_PC
				IF(PAR_2 = 1) THEN
					PAR_1 = 1
				ENDIF
			ENDIF

			IF (PAR_1 = 1) THEN
				measureflag = 2
			ENDIF
		CASE 2 'sweep DAC back down to zero
			IF (dacout = 32768) THEN
				DAC(1,dacout)
				END
			ELSE
				DAC(1,dacout)
				dacout = dacout - upordown*1
			ENDIF			
	ENDSELECT
