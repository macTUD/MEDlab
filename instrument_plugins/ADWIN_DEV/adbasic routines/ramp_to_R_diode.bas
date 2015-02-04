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
'ramp_to_R.bas: outputs voltage V on DAC1, reads current I on ADC 1
'uses diode to measure current
'first measures resistance R_init of sample, then sweeps until V/I=FPAR_1*R_init

'Inputs:
'PAR_1 = start voltage sweep
'PAR_2 = end voltage sweep
'PAR_3 = voltage which resistance measurement is made

'FPAR_1 = value of resistance at which to stop program given in multiple of initial resistance (>1.0)

'Outputs:
'DATA_1 = voltage array
'DATA_2 = current array

'FPAR_2 = conductance in native units
'FPAR_3 = actual conductance in native units

'PAR_4 = current value at +ve PAR_3
'PAR_5 = current value at -ve PAR_3
'PAR_6 = length of data array
'PAR_7 = start time in native units
'PAR_8 = end time in native units
'PAR_9 = delay time
'PAR_10 = flag
'PAR_11 = flag
'PAR_12 = flag
'PAR_13 = dummy for reading time

#DEFINE PI 3.14159265 
DIM DATA_1[10000] as integer 
DIM DATA_2[10000] as integer
DIM counter as integer

INIT:
PAR_6 = 0
PAR_9 = 4000 'delay time=10us
PAR_10 = 0 	'reset flags to 0
PAR_11 = 0
PAR_12 = 0

EVENT:
IF( PAR_6=0 )	THEN
	IF( PAR_10=0 ) THEN
		DAC(1,PAR_3)
		PAR_10 = 1
		PAR_13 = READ_TIMER()
	ENDIF
	IF( (PAR_10=1) AND ((READ_TIMER()-PAR_13)>PAR_9)) THEN
		PAR_10=2
	ENDIF
	IF( (PAR_10=2) ) THEN
		SET_MUX(0)
		START_CONV(1)
		WAIT_EOC(1)
		PAR_4 = READADC(1)

		FPAR_2 = (PAR_4-32768)/ABSI(PAR_3-32768)

		PAR_7 = READ_TIMER()
	ENDIF
ENDIF

IF( PAR_10=2 ) THEN
	IF( PAR_12=0 ) THEN
		DATA_1[PAR_6] = PAR_1+PAR_6
		DAC(1,DATA_1[PAR_6])
		PAR_12 = 1
		PAR_13 = READ_TIMER()
	ENDIF
	IF( (PAR_12=1) AND ((READ_TIMER()-PAR_13)>PAR_9)) THEN
		PAR_12=2
	ENDIF
	IF( PAR_12=2 ) THEN
		SET_MUX(0)
		START_CONV(1)
		WAIT_EOC(1)
		DATA_2[PAR_6] = READADC(1)
		FPAR_3 = (DATA_2[PAR_6]-32768)/(DATA_1[PAR_6]-32768)

		IF( (((PAR_1+PAR_6)>PAR_2) OR (PAR_6>9999)) OR ( FPAR_3<(FPAR_2/FPAR_1)) ) THEN
			PAR_8 = READ_TIMER()
			ACTIVATE_PC
			DAC(1,32768)	'reset DAC1 to 0V
			END
		ENDIF
	
		PAR_6 = PAR_6 + 1
		PAR_12 = 0
	ENDIF
ENDIF