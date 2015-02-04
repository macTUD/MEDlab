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
' creates pulse waveform output, V = 10V (max), 
' to specified frequency (in Hz) not higher than a few kHz
'
' set up so that one cycle = 1 second
'
'
' required Variables: 
'FPAR_11    	: frequency [Hz]
'FPAR_12			: amplitude (V)
'PAR_11 		: number of periods

DIM DATA_1[65537] AS INTEGER	'waveform table
DIM count AS FLOAT
DIM i,loopno  AS INTEGER
DIM qper AS INTEGER 'quarter period
#DEFINE PI 3.14159265 

LOWINIT:
	GLOBALDELAY = 400	'cycle-time of 0.01ms
	loopno = 0
	qper = 16384
	FOR i = 1 TO 2*qper
		'amplitude is qper
  		DATA_1[i] = 2*(FPAR_12/10)*qper
	NEXT i
	FOR i = (1 + 2*qper) TO (4 * qper + 1)
  		DATA_1[i] = 0 
	NEXT i
  	
 	count = 0

EVENT:
  count = count + (FPAR_11*0.65537) ' frequency is used for incrementing the array index
  IF (count > 65537) THEN 
		count = count - 65537
		loopno = loopno + 1
		IF (loopno = PAR_11) THEN
			'stop program
			DAC(1,32768)
			ACTIVATE_PC
			END
		ENDIF
	ENDIF
	i = count + 1	' the first valid array index is 1
  DAC(1, DATA_1[i] + 32768)
