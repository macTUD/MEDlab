****************************************
*	 Prozeﬂnummer = 1
*	 Delay = 40000
*	 Eventsource = 0
*	 Number of Loops = 0
*	 Priorit‰t = 0
*	 Version = 1
*	 FastStop = 0
*	 AdbasicVersion = 3020001
*	 ATSRAM = 0
*	 OPT_LEVEL = 1
*	 SAVECOMPIL = 0
****************************************
' switches voltage on DAC 1 to zero
' runs as process 1
' 
' uses no parameters
'
EVENT:
	DAC(1,32768)
	END