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
'ramp_n_read_hyst.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.

'Inputs:
'PAR_1 = start voltage
'PAR_2 = end voltage
'PAR_3 = no of points to skip (1=record every point)
'PAR_4 = no of points to average over
'PAR_5 = no of loops to wait before measure
'PAR_6 = gain setting (for set_mux command)

'Outputs:
'DATA_1 = voltage array
'DATA_2 = current array
'PAR_10 = current datapoint counter

DIM DATA_1[131072] AS INTEGER
DIM DATA_2[131072] AS INTEGER
DIM counter1, counter2, skipcounter, avgcounter, waitcounter AS INTEGER
DIM loopflag, inoutflag, waitflag, dirflag, vend, posorneg AS INTEGER
DIM totalcurrent AS LONG

INIT:
PAR_10 = 0
counter1 = 32768
counter2 = PAR_1
skipcounter = 1
avgcounter = 0
waitcounter = 0
loopflag = 1
inoutflag = 0
waitflag = 0
dirflag = 0
vend = PAR_2
IF(PAR_1 < PAR_2) THEN
	posorneg = 1
ELSE
	posorneg = -1
ENDIF
totalcurrent = 0

'SET_MUX(00 11 000 000b) 'use gain of 8 for multiplexer
SET_MUX(PAR_6)

EVENT:

SELECTCASE loopflag

	CASE 1 'sweep and measure simultaneously
		SELECTCASE inoutflag
			CASE 0 'output desired voltage on DAC
				DAC(1, counter2)
				IF(counter2 = vend) THEN 'are we at end voltage?
					IF(dirflag = 0) THEN 'reverse sweep direction
						vend = PAR_1
						posorneg = -posorneg
						dirflag = 1
					ELSE
						loopflag = 2
					ENDIF
				ELSE
					counter2 = counter2 + posorneg
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
							DATA_1[PAR_10] = counter2
							DATA_2[PAR_10] = totalcurrent / PAR_4
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
			ACTIVATE_PC
			END
ENDSELECT