****************************************
*	 Proze�nummer = 1
*	 Delay = 400
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorit�t = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 4000001
*	 ATSRAM = 0
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
' creates triangle waveform output, Vp-p = 20V, 
' to specified frequency (in Hz) not higher than a few kHz
'
' set up so that one cycle = 1 second
'
' slight problem with sweeping back to zero - use seperate program
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
	FOR i = 1 TO qper
		'amplitude is qper
  		DATA_1[i] = 2*(FPAR_12/10)*i ' 0V->10V
	NEXT i
	FOR i = (1 + qper) TO (3 * qper)
  		DATA_1[i] = 2*(FPAR_12/10)*(2*qper - i) ' 10V->-10V
	NEXT i
	FOR i = (1 + (3 *  qper)) TO (4 * qper)
  		DATA_1[i] = 2*(FPAR_12/10)*(i - 4 * qper)  ' -10V->0V
	NEXT i
  	
	DATA_1[65537] = DATA_1[1] ' one additional element is necessary !
  	count = 0
 	DAC(1, 32768)		' 0 Volt output

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
