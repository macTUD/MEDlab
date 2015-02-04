****************************************
*	 Prozeﬂnummer = 1
*	 Delay = 40000
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
'mega_bias.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.

'Inputs:
'PAR_1 = start voltage
'PAR_2 = end voltage
'PAR_3 = no of points to skip (1=record every point)
'PAR_4 = no of points to average over
'PAR_5 = no of loops to wait before measure
'PAR_6 = gain setting (for set_mux command)

'Outputs:
'DATA_1 = current array
'PAR_10 = current datapoint counter

DIM DATA_1[65536] AS INTEGER
DIM counter, skipcounter, avgcounter, waitcounter AS INTEGER
DIM loopflag, inoutflag, waitflag, posorneg AS INTEGER
DIM totalcurrent AS LONG

INIT:
PAR_10 = 0
counter = 32768
skipcounter = 1
avgcounter = 0
waitcounter = 0
loopflag = 0
inoutflag = 0
waitflag = 0
IF(PAR_1 < PAR_2) THEN
	posorneg = 1
ELSE
	posorneg = -1
ENDIF
totalcurrent = 0

SET_MUX(PAR_6)

EVENT:

SELECTCASE loopflag
	CASE 0 'sweep to start value
		DAC(1, counter)
		IF(counter = PAR_1) THEN 'are we at start voltage?
			loopflag = 1
		ELSE
			IF(counter < PAR_1) THEN INC(counter)
			IF(counter > PAR_1) THEN DEC(counter) 
		ENDIF
	CASE 1 'sweep and measure simultaneously
		SELECTCASE inoutflag
			CASE 0 'output desired voltage on DAC
				DAC(1, counter)
				IF(counter = PAR_2) THEN 'are we at end voltage?
						loopflag = 2
				ELSE
					counter = counter + posorneg
				ENDIF
				IF(skipcounter >= PAR_3) THEN inoutflag = 1
				skipcounter = skipcounter + 1
			CASE 1 'measure voltage on ADC1
				SELECTCASE waitflag
					CASE 0
						IF(waitcounter >= PAR_5) THEN
							waitflag = 1
						ENDIF
						waitcounter = waitcounter + 1
					CASE 1
						START_CONV(1)
						WAIT_EOC(1)
						totalcurrent = totalcurrent + READADC(1)
					  avgcounter = avgcounter + 1		
						IF(avgcounter >= PAR_4) THEN
							PAR_10 = PAR_10 + 1
							DATA_1[PAR_10] = totalcurrent / PAR_4
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
		DAC(1, counter)
		IF(counter = 32768) THEN
			ACTIVATE_PC
			END
		ELSE
			IF(counter < 32768) THEN INC(counter)
			IF(counter > 32768) THEN DEC(counter) 
		ENDIF
ENDSELECT