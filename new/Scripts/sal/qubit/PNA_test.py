if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')


pna.reset()
#qt.msleep(sweeptime+.1)

pna.setup(start_frequency=start_freq,stop_frequency=stop_freq)
#qt.msleep(sweeptime+.1)

pna.set_power(power)
#qt.msleep(sweeptime+.1)

pna.set_resolution_bandwidth(bandwidth)
#qt.msleep(sweeptime+.1)

pna.set_sweeppoints(f_points)
#qt.msleep(sweeptime+.1)

sweeptime = pna.get_sweeptime()+.1
#qt.msleep(sweeptime)

pna.sweep()
qt.msleep(sweeptime+.1)
trace=pna.fetch_data(polar=True)
