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
'ramp_to_R_special.bas: outputs voltage V on DAC1, reads current I on ADC 1
'first measures resistance R_init of sample, then sweeps until V/I=FPAR_1*R_init

'Inputs:
'PAR_1 = start voltage sweep (native units)
'PAR_2 = end voltage sweep (native units)
'PAR_3 = voltage which resistance measurement is made (native units)

'FPAR_1 = value of resistance at which to stop program given in multiple of initial resistance (>1.0)
'FPAR_4 = value of conductance cut-off, in S
'FPAR_5 = value of first current at PAR_3, in A units

'Outputs:
'DATA_1 = voltage array
'DATA_2 = current array

'FPAR_2 = conductance in S
'FPAR_3 = actual conductance in S

'PAR_4 = current value (every DATA point)
'PAR_5 = current value at -ve PAR_3
'PAR_6 = length of data array
'PAR_7 = start time in native units
'PAR_8 = end time in native units
'PAR_9 = delay time between DAC output and ADC read (in units of 0.1us)

#DEFINE PI 3.14159265 
DIM DATA_1[65536] as integer 'voltage, native units
DIM DATA_2[65536] as float 'current, 1nA units
DIM DATA_3[65536] as float 'lookup table for current
DIM counter,counter1,loopflag,signflag as integer
'DIM VNEG AS INTEGER

INIT:
PAR_6 = 0
loopflag = 0
counter1 = 0
IF (PAR_1<32768) THEN
	signflag=-1
else
	signflag=1
ENDIF

SET_MUX(0)

EVENT:
'FPAR_20=DATA_3[1]
'FPAR_21=DATA_3[2]
'FPAR_22=DATA_3[30000]
'FPAR_23=DATA_3[4]
SELECTCASE loopflag
	CASE 0 'output voltage on DAC1
		IF (PAR_6 = 0) THEN 'is this the first loop?
			DAC(1,PAR_3)
			PAR_7 = READ_TIMER()
			loopflag = 2
		ELSE
			DATA_1[PAR_6] = PAR_1+signflag*PAR_6
			DAC(1,DATA_1[PAR_6])		
			loopflag = 1
		ENDIF
	CASE 1 'read current on ADC1
		IF (PAR_6 = 0) THEN 'is this the beginning of loop?
			START_CONV(1)
			WAIT_EOC(1)
			PAR_4 = READADC(1)
			FPAR_5 = DATA_3[PAR_4]
			FPAR_2 = (FPAR_5*3276.8)/(PAR_3-32768)
			DATA_1[0] = PAR_3
			DATA_2[0] = FPAR_5

			'is the measured initial conductance lower than the target
			IF( FPAR_2 < FPAR_4 ) THEN 
				PAR_6 = 1
				DAC(1,32768)	'reset DAC1 to 0V
				ACTIVATE_PC
				END'quit program
			ENDIF
		ELSE
			START_CONV(1)
			WAIT_EOC(1)
			PAR_4= READADC(1)
			DATA_2[PAR_6] = DATA_3[PAR_4]
			FPAR_3 = (3276.8*DATA_2[PAR_6])/(DATA_1[PAR_6]-32768)
			'IF ( FPAR_3 < FPAR_2) THEN PAR_20 = 1
			IF(signflag<0) THEN	
				IF( (((PAR_1+signflag*PAR_6) < PAR_2) OR (PAR_6 > 9999)) OR ( FPAR_3 < (FPAR_2/FPAR_1)) ) THEN
					PAR_8 = READ_TIMER()
					ACTIVATE_PC
					DAC(1,32768)	'reset DAC1 to 0V
					END'quit program
				ENDIF
			ENDIF
			IF(signflag>0) THEN	
				IF( (((PAR_1+signflag*PAR_6) > PAR_2) OR (PAR_6 > 9999)) OR ( FPAR_3 < (FPAR_2/FPAR_1)) ) THEN
					PAR_8 = READ_TIMER()
					ACTIVATE_PC
					DAC(1,32768)	'reset DAC1 to 0V
					END'quit program
				ENDIF
			ENDIF

		ENDIF
		PAR_6 = PAR_6 + 1
		loopflag = 0
	CASE 2
		IF (counter1=10) THEN
			loopflag = 1
		ENDIF
		counter1 = counter1+1
ENDSELECT