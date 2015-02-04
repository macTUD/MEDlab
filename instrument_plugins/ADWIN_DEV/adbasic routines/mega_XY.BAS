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
*	 OPT_LEVEL = 2
*	 SAVECOMPIL = 0
****************************************
'mega_bias.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.

'Inputs:
'PAR_1 = start voltage
'PAR_2 = end voltage
'PAR_3 = no of points to skip (0=record every point)
'PAR_4 = no of points to average over
'PAR_5 = no of loops to wait before measure
'PAR_6 = gain setting (for set_mux command)
'PAR_8 = set if sweep or constant bias (sweep=0; cte=1) 

'Outputs:
'DATA_1 = Voltage array
'DATA_2 = current array
'PAR_10 = current datapoint counter
'PAR_11 = Progress (0->255)

DIM DATA_1[65536], DATA_2[65536] , DATA_3[65536] AS INTEGER
DIM ctecounter,counter, skipcounter, avgcounter, waitcounter AS INTEGER
DIM loopflag, inoutflag, waitflag, posorneg AS INTEGER
DIM totalcurrent, totaltwo, time AS LONG

INIT:
	PAR_10 = 0
	FPAR_10 = 0
	
	counter = 32768
	skipcounter = 1
	ctecounter = 0'''
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
	
	'SET_MUX(PAR_6)
   SET_MUX(0)
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
					IF (PAR_8=0) THEN 'sweep or measure at constant bias
						PAR_11 = 255 * (counter - PAR_1) / (PAR_2 - PAR_1)
						DAC(1, counter)
						IF(counter = PAR_2) THEN 'are we at end voltage?
								loopflag = 2
						ELSE
							counter = counter + posorneg
						ENDIF
					ELSE
					   				
					ENDIF
					IF(skipcounter > PAR_3) THEN inoutflag = 1
					skipcounter = skipcounter + 1
					IF (ctecounter=255) THEN loopflag=2'sweep bias  to zero and end 
				CASE 1 'measure voltage on ADC1
					SELECTCASE waitflag
						CASE 0
							IF(waitcounter >= PAR_5) THEN
								waitflag = 1
							ENDIF
							waitcounter = waitcounter + 1
						CASE 1
							START_CONV(11b)
							WAIT_EOC(11b)
							totalcurrent = totalcurrent + READADC(1)
							totaltwo= totaltwo + READADC(2)
							avgcounter = avgcounter + 1		
							PAR_11 = ctecounter
							IF(avgcounter >= PAR_4) THEN
								ctecounter = ctecounter+1
								PAR_10 = PAR_10 + 1
								DATA_1[PAR_10] = counter
								DATA_2[PAR_10] = totalcurrent / PAR_4
								DATA_3[PAR_10] = totaltwo/ PAR_4 
								skipcounter = 1
								avgcounter = 0
								waitcounter = 0
								inoutflag = 0
								waitflag = 0
								totalcurrent = 0
								totaltwo = 0
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