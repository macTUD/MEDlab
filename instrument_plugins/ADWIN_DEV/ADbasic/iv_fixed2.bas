****************************************
*	 Prozeﬂnummer = 2
*	 Delay = 1000
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorit‰t = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 4000001
*	 ATSRAM = 0
*	 OPT_LEVEL = 2
*	 SAVECOMPIL = 0
****************************************
'iv_fixed.bas: slowly ramp voltage on DAC #PAR_20

'Inputs:
'PAR_20 = DAC
'PAR_21 = Target gate voltage

'Outputs:
'PAR_30 = Current gate voltage

EVENT:

DAC(PAR_20, PAR_30)
IF(PAR_30 < PAR_21) THEN INC(PAR_30)
IF(PAR_30 > PAR_21) THEN DEC(PAR_30)
IF(PAR_30 = PAR_21) THEN
	ACTIVATE_PC
	END
ENDIF