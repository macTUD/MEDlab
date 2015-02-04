def spyview_process(data=0,len1=0,minval1=0,maxval1=0,len2=0,minval2=0,maxval2=0,len3=0,minval3=0,maxval3=0):
    '''
    Inteded to be simple and easily adjusted

    To be written in the meta file:
    example:
    '#loop1'
    len(f_list)
    f1_start
    f1_stop
    Frequency (Hz) #better get name from coordinate...
    '#loop2'
    len(g_list)
    gate_start
    gate_stop
    Gate [V]
    '#loop3'
    len(pow_list)
    pow_start
    f1_power
    Power [dBm]
    #values
    4
    S21 (Mlog) [dBm]]

    Substitute for "data.new_block"
    Creates spyview meta.txt file after every block is completed

    REQUIRED Arguments:
        data -- the data object
        len1 -- number points of inner loop
        minval1 -- minval of inner loop
        maxval1 -- maxval of inner loop
        len2 -- number pointsof outer loop
        minval2 -- minval of outer loop
        maxval2 -- maxval of outer loop
        len3
        minval3 -- minval of outermost loop
        maxval3 -- maxval of outermost loop
    '''
    metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n'
                   +str(len1)+'\n'
                   +str(minval1)+'\n'
                   +str(maxval1)+'\n'
                   +str(data.get_dimension_name(0))+'\n'
                   +'#outer loop\n'
                   +str(len2)+'\n'
                   +str(minval2)+'\n'
                   +str(maxval2)+'\n'
                   +str(data.get_dimension_name(1))+'\n'
                   +'#outer most loop\n'
                   +str(len3)+'\n'
                   +str(minval3)+'\n'
                   +str(maxval3)+'\n'
                   +str(data.get_dimension_name(2))+'\n'
                  )                       

    metafile.write('#values\n'
                   +'4\n'
                   +str(data.get_dimension_name(3)))
    metafile.write('#values\n'
                   +'5\n'
                   +str(data.get_dimension_name(4)))
    metafile.close()

#There should be something that converts a datafile back into a data object...

##def spyview_post_process(filename):
##    '''
##    Substitue for "data.new_block"
##    Creates spyview meta.txt file after every block is completed
##
##    Arguments:
##        filename -- data file to use 
##    '''
##    datafile=open(filename,'r')
##    data=[]
##    for line in datafile:
##        if (len(line)>2) and (line[0]!='#')
##        data.append(line.split())
##
##    innervals=[]
##    blockvals=[]
##    for i in data:
##        innervals.append(i[0])
##        outervals.append(i[1])
##       
##    
##    metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
##    metafile.write('#inner loop\n%s\n%s\n%s\n%s\n'%
##        (data.get_npoints_max_block(), min(innervals), max(innervals),
##         data.get_dimension_name(0)))
##    metafile.write('#outer loop\n%s\n%s\n%s\n%s\n'%
##        (len(_blockvals), min(_blockvals), max(_blockvals),
##         data.get_dimension_name(1)))#len(_blockvals) = data.get_nblocks()
##    metafile.write('#outermost loop (unused)\n1\n0\n1\nNothing\n')
##    metafile.write('#values\n3\n%s'%data.get_dimension_name(2))
##    metafile.close()
