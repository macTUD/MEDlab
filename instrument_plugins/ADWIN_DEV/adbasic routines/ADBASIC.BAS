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
' ramp_n_read.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.

'Inputs:
'PAR_1 = start voltage
'PAR_2 = end voltage
'PAR_42 = -end voltage
'PAR_6 = point skip (1=record every point)
'PAR_8 = no of points to average over
'PAR_9 = no of loops to wait before measure
'PAR_20 = gain setting (for set_mux command)

'Outputs:
'DATA_1 = voltage array
'DATA_2 = current array
'PAR_3 = current DAC output counter
'PAR_4 = start time in native units
'PAR_5 = end time in native units
'PAR_7 = current datapoint counter

#DEFINE PI 3.14159265 
DIM DATA_1[65536] as integer 
DIM DATA_2[65536] as integer
DIM counter1,counter2,skipcounter,avgcounter,waitcounter as integer
DIM loopflag,inoutflag,waitflag,posorneg as integer '0=sweep to start value, 1=sweep and measure, 2=sweep to zero
DIM totalcurrent as LONG

INIT:
PAR_3 = 0
PAR_7 = 0
PAR_42= PAR_1 - (PAR_2 - PAR_1)
loopflag=0
inoutflag=1 'begin measurement after start voltage is reached
waitflag=0
counter1=32768
counter2=PAR_2
skipcounter=1
avgcounter=1
waitcounter=0
totalcurrent = 0
IF( PAR_1<PAR_2 ) THEN
	posorneg=1
ELSE
	posorneg=-1
ENDIF

'SET_MUX(00 11 000 000b)'use gain of 8 for multiplexer
SET_MUX(PAR_20)
'SET_MUX(00 00 000 000b)

EVENT:

SELECTCASE loopflag
	CASE 0 	'sweep to zero
		DAC(1,counter1)
		IF( counter1=PAR_1 ) THEN 'are we at start voltage?
			loopflag=1
		ELSE
			IF( counter1<PAR_1) THEN INC(counter1)
			IF( counter1>PAR_1) THEN DEC(counter1) 
		ENDIF
	CASE 1 'sweep to one end and measure simultaneously
		SELECTCASE inoutflag
			CASE 0 'output desired voltage on DAC1
				avgcounter = 1
				totalcurrent = 0
				IF( (PAR_1+PAR_3*posorneg)=PAR_2 ) THEN 'are we at end voltage?
					PAR_5 = READ_TIMER()
					loopflag=2
				ELSE
					PAR_3 = PAR_3 + 1
				ENDIF
				DAC(1,PAR_1+PAR_3*posorneg)
				IF( PAR_3=0 ) THEN 	'read the current time
					PAR_4 = READ_TIMER()
				ENDIF
				IF(skipcounter=PAR_6) THEN inoutflag=1
				skipcounter = skipcounter + 1
			CASE 1 'measure voltage on ADC1
				SELECTCASE waitflag
					CASE 0
						IF(waitcounter = PAR_9) THEN
							waitflag=1
						ENDIF
						waitcounter = waitcounter + 1
					CASE 1
						START_CONV(1)
						WAIT_EOC(1)
						totalcurrent = totalcurrent + READADC(1)
						IF( avgcounter = PAR_8 ) THEN
							DATA_1[PAR_7+1] = PAR_1+PAR_3*posorneg
							DATA_2[PAR_7+1] = totalcurrent/PAR_8
							PAR_22 = DATA_1[1]
							PAR_23 = DATA_2[1]
							PAR_7 = PAR_7 + 1
							inoutflag=0
							waitflag=0
							skipcounter=1
							avgcounter=1
							waitcounter=0
						ENDIF
						avgcounter = avgcounter + 1
				ENDSELECT
			ENDSELECT

CASE 2 'sweep to the other end and measure simultaneously
	SELECTCASE inoutflag
			CASE 0 'output desired voltage on DAC1
				avgcounter = 1
				totalcurrent = 0
				IF( (PAR_1+PAR_3*posorneg)=PAR_42 ) THEN 'are we at end voltage?
					PAR_5 = READ_TIMER()
					loopflag=3
				ELSE
					PAR_3 = PAR_3 - 1
				ENDIF
				DAC(1,PAR_1+PAR_3*posorneg)
				IF( PAR_3=0 ) THEN 	'read the current time
					PAR_4 = READ_TIMER()
				ENDIF
				IF(skipcounter=PAR_6) THEN inoutflag=1
				skipcounter = skipcounter + 1
			CASE 1 'measure voltage on ADC1
				SELECTCASE waitflag
					CASE 0
						IF(waitcounter = PAR_9) THEN
							waitflag=1
						ENDIF
						waitcounter = waitcounter + 1
					CASE 1
						START_CONV(1)
						WAIT_EOC(1)
						totalcurrent = totalcurrent + READADC(1)
						IF( avgcounter = PAR_8 ) THEN
							DATA_1[PAR_7+1] = PAR_1+PAR_3*posorneg
							DATA_2[PAR_7+1] = totalcurrent/PAR_8
							PAR_22 = DATA_1[1]
							PAR_23 = DATA_2[1]
							PAR_7 = PAR_7 + 1
							inoutflag=0
							waitflag=0
							skipcounter=1
							avgcounter=1
							waitcounter=0
						ENDIF
						avgcounter = avgcounter + 1
				ENDSELECT
			ENDSELECT
CASE 3 'sweep to zero and measure simultaneously
	SELECTCASE inoutflag
			CASE 0 'output desired voltage on DAC1
				avgcounter = 1
				totalcurrent = 0
				IF( (PAR_1+PAR_3*posorneg)=PAR_1) THEN 'are we at end voltage?
					PAR_5 = READ_TIMER()
					loopflag=4
				ELSE
					PAR_3 = PAR_3 + 1
				ENDIF
				DAC(1,PAR_1+PAR_3*posorneg)
				IF( PAR_3=0 ) THEN 	'read the current time
					PAR_4 = READ_TIMER()
				ENDIF
				IF(skipcounter=PAR_6) THEN inoutflag=1
				skipcounter = skipcounter + 1
			CASE 1 'measure voltage on ADC1
				SELECTCASE waitflag
					CASE 0
						IF(waitcounter = PAR_9) THEN
							waitflag=1
						ENDIF
						waitcounter = waitcounter + 1
					CASE 1
						START_CONV(1)
						WAIT_EOC(1)
						totalcurrent = totalcurrent + READADC(1)
						IF( avgcounter = PAR_8 ) THEN
							DATA_1[PAR_7+1] = PAR_1+PAR_3*posorneg
							DATA_2[PAR_7+1] = totalcurrent/PAR_8
							PAR_22 = DATA_1[1]
							PAR_23 = DATA_2[1]
							PAR_7 = PAR_7 + 1
							inoutflag=0
							waitflag=0
							skipcounter=1
							avgcounter=1
							waitcounter=0
						ENDIF
						avgcounter = avgcounter + 1
				ENDSELECT
			ENDSELECT

	
	
	CASE 4 'sweep back down to zero volts
		DAC(1,counter2)
		IF( counter2=32768 ) THEN
			IF (par_7 > 0) THEN par_7 = par_7 - 1 'delete non-existent points
			ACTIVATE_PC
			END
		ELSE
			IF( counter2<32768) THEN INC(counter2)
			IF( counter2>32768) THEN DEC(counter2) 
		ENDIF
ENDSELECT