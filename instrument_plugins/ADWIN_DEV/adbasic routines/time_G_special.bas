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

'ínputs:
'PAR_10 = bias offset
'PAR_1 = off switch (sweeps back to zero and stops program
'PAR_2 = flag to clear previous data and repeat measurement
'PAR_3 = no. of readings to average over
'DATA_2 = lookup table of current

'outputs
'FPAR_1 = current
'FPAR_2 = lock-in magnitude
'FPAR_3 = lock-in phase
'FPAR_4 = threshold current for quitting program
'FPAR_5 = current setting (-1 = logarithmic scale)


'define variables
DIM DATA_2[65536] AS FLOAT 'lookup table for current
DIM counter, progstep, descendflag AS LONG
DIM adcreadout, dacout, upordown AS INTEGER
DIM current AS FLOAT
DIM	limag,lipha AS LONG

INIT:
	PAR_1 = 0
	PAR_2 = 0
	progstep = 0
	descendflag = 0
	dacout = 32768
	IF (PAR_10>32768) THEN
		upordown = 1
	ELSE
		upordown = -1
	ENDIF

EVENT:
	SELECTCASE progstep
		CASE 0 'sweep DAC to starting value
			IF (dacout = PAR_10) THEN
				DAC(1,dacout)
				progstep = 1
			ELSE
				DAC(1,dacout)
				dacout = dacout + upordown*1
			ENDIF
		CASE 1 'standby mode
			IF(PAR_2 = 1) THEN
				progstep = 2
				counter = 1
				current = 0
				limag = 0
				lipha = 0
			ENDIF
			IF (PAR_1 = 1) THEN
				progstep = 3
			ENDIF
		CASE 2 'measure routine
			SET_MUX(0)	'set multiplexer to channel 1
			SLEEP(25) 'wait 2.5us
			START_CONV(1)	'start ADC1 conversion
			WAIT_EOC(1)		'wait for end-of-conversion
			adcreadout = READADC(1)
			IF(FPAR_5<0) THEN
				current = current + DATA_2[adcreadout]
			ELSE
				current = current + (10*(adcreadout-32768)*FPAR_5)/32768
			ENDIF
		
			IF (counter=PAR_3) THEN
				FPAR_1 = current/PAR_3
				ACTIVATE_PC
				progstep = 1
				PAR_2 = 0
			ENDIF
			'(FPAR_1<FPAR_4) THEN
				'PAR_1 = 1
			'ENDIF
			counter = counter+1
		CASE 3 'sweep DAC back down to zero
			IF (dacout = 32768) THEN
				DAC(1,dacout)
				END
			ELSE
				DAC(1,dacout)
				dacout = dacout - upordown*1
			ENDIF			
	ENDSELECT