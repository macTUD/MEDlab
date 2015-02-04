****************************************
*	 Prozeßnummer = 1
*	 Delay = 40000
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
'iv_sweep.bas: ramps voltage on DAC #PAR_1, recording voltage dependent current on ADC1.

'Inputs:
'PAR_1 = DAC
'PAR_2 = start voltage
'PAR_3 = end voltage
'PAR_4 = no of points to skip (0=record every point)
'PAR_5 = no of points to average over
'PAR_6 = no of loops to wait before measure
'PAR_7 = gain setting (for set_mux command)

'Outputs:
'DATA_1 = Voltage array
'DATA_2 = current array
'PAR_10 = current datapoint counter
'PAR_11 = Progress (0->255)

DIM DATA_1[65536], DATA_2[65536] AS INTEGER
DIM counter, skipcounter, avgcounter, waitcounter AS INTEGER
DIM loopflag, inoutflag, waitflag, posorneg AS INTEGER
DIM totalcurrent AS LONG

INIT:
	PAR_10 = 0
	FPAR_10 = 0
	
	counter = 32768
	skipcounter = 1
	avgcounter = 0
	waitcounter = 0
	loopflag = 0
	inoutflag = 0
	waitflag = 0
	
	IF(PAR_2 < PAR_3) THEN
		posorneg = 1
	ELSE
		posorneg = -1
	ENDIF
	totalcurrent = 0
	
	SET_MUX(PAR_7)

EVENT:
	SELECTCASE loopflag
		CASE 0 'sweep to start value
			SELECTCASE waitflag
				CASE 0
					IF(waitcounter >= (PAR_6*10)) THEN
						IF (counter = PAR_2) THEN
							loopflag = 1
							waitflag = 0
						ELSE
							waitflag = 1
						ENDIF
					ENDIF
					waitcounter = waitcounter + 1
				CASE 1
					DAC(PAR_1, counter)
					IF(counter < PAR_2) THEN INC(counter)
					IF(counter > PAR_2) THEN DEC(counter)
					SLEEP(50000)
					waitflag = 0
			ENDSELECT
	
		
		CASE 1 'sweep and measure simultaneously
			SELECTCASE inoutflag
				CASE 0 'output desired voltage on DAC
					PAR_11 = 255 * (counter - PAR_2) / (PAR_3 - PAR_2)
					DAC(PAR_1, counter)
					IF(counter = PAR_3) THEN 'are we at end voltage?
							loopflag = 2
					ELSE
						counter = counter + posorneg
					ENDIF
					IF(skipcounter > PAR_4) THEN inoutflag = 1
					skipcounter = skipcounter + 1
				CASE 1 'measure voltage on ADC1 (current)
					SELECTCASE waitflag
						CASE 0
							IF(waitcounter >= PAR_6) THEN
								waitflag = 1
							ENDIF
							waitcounter = waitcounter + 1
						CASE 1
							START_CONV(1)
							WAIT_EOC(1)
							totalcurrent = totalcurrent + READADC(1)
						  avgcounter = avgcounter + 1		
							IF(avgcounter >= PAR_5) THEN
								PAR_10 = PAR_10 + 1
								DATA_1[PAR_10] = counter
								DATA_2[PAR_10] = totalcurrent / PAR_5
								skipcounter = 1
								avgcounter = 0
								waitcounter = 0
								inoutflag = 0
								waitflag = 0
								totalcurrent = 0
							ENDIF
						
					ENDSELECT
			ENDSELECT
		CASE 2 'sweep back down to zero volts
				SELECTCASE waitflag
					CASE 0
						IF(waitcounter >= (PAR_6*10)) THEN
							IF(counter = 32768) THEN
								ACTIVATE_PC
								END
							ELSE
								waitflag = 1
							ENDIF
						ENDIF
						waitcounter = waitcounter + 1
					CASE 1
						DAC(PAR_1, counter)
						IF(counter < 32768) THEN INC(counter)
						IF(counter > 32768) THEN DEC(counter)
						SLEEP(50000)
						waitflag = 0
				ENDSELECT
			

	ENDSELECT