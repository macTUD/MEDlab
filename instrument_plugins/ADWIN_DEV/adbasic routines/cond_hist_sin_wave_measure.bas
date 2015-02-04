****************************************
*	 Prozeßnummer = 2
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
' creates sin waveform output, Vrms = 10V, on DAC1
' with ref output on DAC2 (1V pulses)
' to specified frequency (in Hz) not higher than a few kHz
'
' set up so that one cycle = 1 second
'
' slight problem with sweeping back to zero - use seperate program
'
' required Variables: 
'FPAR_21    	: frequency [Hz]
'FPAR_22			: rms amplitude (V)
'PAR_21 		: number of periods

DIM DATA_1[65537],DATA_2[65537] AS INTEGER	'waveform table
DIM count AS FLOAT
DIM i,loopno  AS INTEGER
DIM qper AS INTEGER 'quarter period
#DEFINE PI 3.14159265 

LOWINIT:
	GLOBALDELAY = 400	'cycle-time of 0.01ms
	SET_MUX(0)
	loopno = 0
	qper = 16384
	FOR i = 1 TO 4*qper
		'amplitude is qper
  		DATA_1[i] = 2*1.414*(FPAR_22/10)*qper*sin((2*PI*i)/(4*qper))
	NEXT i
	DATA_1[65537] = DATA_1[1] ' one additional element is necessary !
	FOR i = 1 TO 2*qper
		'amplitude is qper
  		DATA_2[i] = 0.2*qper
	NEXT i
	FOR i = 2*qper+1 TO 4*qper
		'amplitude is qper
  		DATA_2[i] = 0
	NEXT i
	DATA_2[65537] = 0
  count = 0
 	DAC(1, 32768)		' 0 Volt output

EVENT:
  count = count + (FPAR_21*0.65537) ' frequency is used for incrementing the array index
  IF (count >= 65537) THEN 
		count = count - 65537
		loopno = loopno + 1
		IF (loopno = PAR_21) THEN
			START_CONV(3)
			WAIT_EOC(3)
			PAR_1=READADC(2)
			'stop program
			DAC(1,32768)
			DAC(2,32768)
			ACTIVATE_PC
			END
		ENDIF
	ENDIF
	i = count + 1	' the first valid array index is 1
  DAC(1, DATA_1[i] + 32768)
	DAC(2, DATA_2[i] + 32768)
