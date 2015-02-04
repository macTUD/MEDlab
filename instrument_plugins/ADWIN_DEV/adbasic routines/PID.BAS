****************************************
*	 Prozeßnummer = 2
*	 Delay = 400
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorität = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 3020001
*	 ATSRAM = 0
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
' ramp.bas: ramps voltage on DAC1, recording voltage dependent current on ADC1.
' When resistance drops below FPAR_1% of previous value, reset output to 10mV and start 
' ramp again. Once target resistance is reached, exit program

' This version expects a diode in series with the electromigration sample.
' The curve for current voltage dependence is calculated independently

'Inputs:
'FPAR_1 = percentage threshold for ramp (in percent)
'FPAR_3 = target resistance (in ohms)

'Outputs:
'FIFO Data, raw output from DAC1 in FIFO buffer

'Diagnostic parameters:
'FPAR_4 = resistance of sample

DIM DATA_2[65537] AS INTEGER	'waveform table
DIM v_out, v_meas AS INTEGER
DIM V_out, V_meas, lastres AS FLOAT
#DEFINE PI 3.14159265 

LOWINIT:
	v_out = 0
	lastres=1000 	'make it 1kohm to begin with
EVENT:
	SET_MUX(0)
	START_CONV(1)
	WAIT_EOC(1)
	IF (v_out == 0) THEN
		'start ramp over from 10mV
		v_vol = 32
		DAC(1,v_out+32768)
	ELSE
		'continue ramp
		DAC(1,v_out+32768)
		v_meas = READADC(1)
		V_out = 10.0*(v_out-32768)/32768
		V_meas = 10.0*(v_meas-32768)/32768
		FPAR_4 = V_out/EXP(-19.40+20.4*V_meas)
		
		v_out = v_out+1
	ENDIF
	ACTIVATE_PC
	IF(FPAR_4>0.8*lastres)THEN
		v_out = 0
		lastres = FPAR_4
	ENDIF
	IF(FPAR_4>FPAR_3) THEN
		DAC(1,32768)
		END
	ENDIF
	
FINISH:
	FPAR_3 = count 	'for reset program