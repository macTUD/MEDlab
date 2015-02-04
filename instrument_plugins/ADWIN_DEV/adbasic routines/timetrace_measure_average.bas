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
'timetrace_measure_average.bas: records voltage dependent current on ADC1.

'Inputs:
'PAR_8 = no of points to measure over
'PAR_9 = no of loops to wait before measure
'PAR_10 = no of points to average over
'PAR_20 = gain setting (for set_mux command)

'Outputs:
'DATA_2 = current array
'PAR_4 = start time in native units
'PAR_5 = end time in native units
'PAR_7 = current datapoint counter

#DEFINE PI 3.14159265 
'DIM DATA_1[65536] as integer 
DIM DATA_2[65536] as integer
DIM meascounter, waitcounter, avgcounter as integer
DIM totalcurrent as integer
DIM waitflag as integer '0=wait, 1=measure

INIT:
PAR_7 = 1
waitflag = 0
meascounter = 1
waitcounter = 0
avgcounter = 1
totalcurrent = 0

'SET_MUX(00 10 000 000b)'use gain of 8 for multiplexer
SET_MUX(PAR_20)

EVENT:
SELECTCASE waitflag
	CASE 0
		IF(waitcounter = PAR_9) THEN
			waitflag = 1
		ENDIF
		waitcounter = waitcounter + 1
	CASE 1
		START_CONV(1)
		WAIT_EOC(1)
		totalcurrent = totalcurrent + READADC(1)
		IF(avgcounter = PAR_10) THEN
			DATA_2[PAR_7] = totalcurrent / PAR_10
			avgcounter = 0
			totalcurrent = 0
			IF(meascounter = PAR_8) THEN
				waitflag = 0
				ACTIVATE_PC
				END
			ENDIF
			PAR_7 = PAR_7 + 1
			meascounter = meascounter + 1
		ENDIF
		avgcounter = avgcounter + 1
ENDSELECT
