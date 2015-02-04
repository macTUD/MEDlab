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
'mega_gate.bas: slowly ramp gate voltage

'Inputs:
'PAR_20 = Target gate voltage

'Outputs:
'PAR_21 = Current gate voltage

EVENT:

DAC(2, PAR_21)
IF(PAR_21 < PAR_20) THEN INC(PAR_21)
IF(PAR_21 > PAR_20) THEN DEC(PAR_21)
IF(PAR_21 = PAR_20) THEN
	ACTIVATE_PC
	END
ENDIF