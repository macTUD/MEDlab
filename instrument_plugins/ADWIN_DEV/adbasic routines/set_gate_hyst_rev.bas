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
*	 OPT_LEVEL = 0
*	 SAVECOMPIL = 0
****************************************
'set_gate_hyst.bas: slowly ramp gate voltage

'Inputs:
'PAR_20 = Target gate voltage
'PAR_1  = Target bias voltage
'Outputs:
'PAR_21 = Current gate voltage
'PAR_22 = Current bias voltage 

DIM v AS INTEGER
DIM loopflag as INTEGER


INIT:
loopflag = 0 


EVENT:
'
'		selectcase loopflag
'		CASE 0
'			DAC(2, PAR_21)
'			IF(PAR_21 < PAR_20) THEN INC(PAR_21)
'			IF(PAR_21 > PAR_20) THEN DEC(PAR_21)
'      IF(PAR_21=PAR_20) THEN loopflag=1
'		CASE 1
'			DAC(1,PAR_22)
'			IF(PAR_22 < PAR_1) THEN INC(PAR_22)
'			IF(PAR_22 > PAR_1) THEN DEC(PAR_22)
'      IF(PAR_22=PAR_1) THEN
'				ACTIVATE_PC
'	      END
'			ENDIF
'    ENDSELECT
	





IF (PAR_23=0) THEN 
SELECTCASE loopflag
		CASE 0
			DAC(2, PAR_21)
			IF(PAR_21 < PAR_20) THEN INC(PAR_21)
			IF(PAR_21 > PAR_20) THEN DEC(PAR_21)
      IF(PAR_21=PAR_20) THEN loopflag=1
		CASE 1
			DAC(1,PAR_22)
			IF(PAR_22 < PAR_1) THEN INC(PAR_22)
			IF(PAR_22 > PAR_1) THEN DEC(PAR_22)
      IF(PAR_22=PAR_1) THEN
				ACTIVATE_PC
	      END
      ENDIF
ENDSELECT

ELSE
	

SELECTCASE loopflag
		CASE 0
			DAC(1,PAR_22)
			IF(PAR_22 < PAR_1) THEN INC(PAR_22)
			IF(PAR_22 > PAR_1) THEN DEC(PAR_22)
      IF(PAR_22=PAR_1)   THEN loopflag=1
		CASE 1
			DAC(1,PAR_22)
			DAC(2, PAR_21)
			IF(PAR_21 < PAR_20) THEN INC(PAR_21)
			IF(PAR_21 > PAR_20) THEN DEC(PAR_21)
      IF(PAR_21=PAR_20)   THEN 
				ACTIVATE_PC
	      END
      ENDIF
ENDSELECT

ENDIF

