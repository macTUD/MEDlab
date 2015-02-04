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
' ramp_n_read_lockin.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.
' voltage on DAC1 also has oscillation, and also reads ADC2, which may have lock-in signal
'reference output for lock-in on DAC2

'Inputs:
'PAR_1 = start voltage
'PAR_2 = end voltage
'PAR_6 = point skip (1=record every point)
'PAR_8 = no of points to average over
'PAR_9 = no of loops to wait before measure
'PAR_20 = gain setting (for set_mux command)
'FPAR_21    	: frequency [Hz]
'FPAR_22			: rms amplitude (V)
'PAR_21 		: number of periods

'Outputs:
'DATA_1 = voltage array
'DATA_2 = current array
'PAR_3 = current DAC output counter
'PAR_4 = start time in native units
'PAR_5 = end time in native units
'PAR_7 = current datapoint counter

#DEFINE PI 3.14159265 
DIM DATA_1[65536],DATA_2[65536], DATA_3[65536] as integer 
DIM counter1,counter2,skipcounter,avgcounter,waitcounter as integer
DIM loopflag,inoutflag,waitflag,posorneg as integer '0=sweep to start value, 1=sweep and measure, 2=sweep to zero
DIM totalcurrent as LONG

DIM DATA_4[65537],DATA_5[65537] AS INTEGER	'waveform table
DIM count AS FLOAT
DIM i,loopno  AS INTEGER
DIM qper AS INTEGER 'quarter period
#DEFINE PI 3.14159265 

INIT:
	GLOBALDELAY = 400	'cycle-time of 0.01ms
	SET_MUX(PAR_20)
	loopno = 0
	qper = 16384
	FOR i = 1 TO 4*qper
		'amplitude is qper
  		DATA_4[i] = 2*1.414*(FPAR_22/10)*qper*sin((2*PI*i)/(4*qper))
	NEXT i
	DATA_4[65537] = DATA_4[1] ' one additional element is necessary !
	PAR_23 = DATA_4[qper]
	FOR i = 1 TO 2*qper
		'amplitude is qper
  		DATA_5[i] = 0.2*qper
	NEXT i
	FOR i = 2*qper+1 TO 4*qper
		'amplitude is qper
  		DATA_5[i] = 0
	NEXT i
	DATA_5[65537] = 0
	
	PAR_3 = 0
	PAR_7 = 0
	PAR_9 = (PAR_21*40000000)/(FPAR_21*GLOBALDELAY)
	loopflag=0
	inoutflag=0
	waitflag=0
	counter1=32768
	counter2=PAR_2
	skipcounter=1
	avgcounter=1
	waitcounter=0
	IF( PAR_1<PAR_2 ) THEN
		posorneg=1
	ELSE
		posorneg=-1
	ENDIF

EVENT:

SELECTCASE loopflag
	CASE 0 	'sweep to start value
		DAC(1,counter1)
		IF( counter1=PAR_1 ) THEN 'are we at start voltage?
			loopflag=1
		ELSE
			IF( counter1<PAR_1) THEN INC(counter1)
			IF( counter1>PAR_1) THEN DEC(counter1) 
		ENDIF
	CASE 1 'alternately sweep and measure
		SELECTCASE inoutflag
			CASE 0 'output desired voltage on DAC
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
							count = 0
							START_CONV(3)
							WAIT_EOC(3)
							DATA_3[PAR_7]=READADC(2)
							DAC(1, PAR_1+PAR_3*posorneg )
						ENDIF
						waitcounter = waitcounter + 1
  					count = count + (FPAR_21*0.65537) ' frequency is used for incrementing the array index
  					IF (count >= 65537) THEN count = count - 65537
						i = count + 1	' the first valid array index is 1
  					DAC(1, DATA_4[i] + PAR_1+PAR_3*posorneg)
						DAC(2, DATA_5[i] + 32768)
					CASE 1
						START_CONV(3)
						WAIT_EOC(3)
						totalcurrent = totalcurrent + READADC(1)
						IF( avgcounter = PAR_8 ) THEN
							DATA_1[PAR_7] = PAR_1+PAR_3*posorneg
							DATA_2[PAR_7] = totalcurrent/PAR_8
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
	CASE 2 'sweep back down to zero volts
		DAC(1,counter2)
		DAC(2,32768)
		IF( counter2=32768 ) THEN
			IF (par_7 > 0) THEN par_7 = par_7 - 1 'delete non-existent points
			ACTIVATE_PC
			END
		ELSE
			IF( counter2<32768) THEN INC(counter2)
			IF( counter2>32768) THEN DEC(counter2) 
		ENDIF
ENDSELECT