import qt
import numpy as np
import array 


def pulse(filename):
    '''
    Generate an arbitrary pattern file for the AWG520.
    '''

    #still implement check if the file already exists.
    g=file(filename,"w+")
    

    g.close()


def pulse_ACII_file(filename,input_list):
    '''
    Generate ASCII file with pulse shape to be converted by the
    AWG File Conversion Utility. Based on an input_list with elements between -1,1
    '''

    #still implement check if the file already exists.
    g=file(filename,'w+')

    for t in input_list:
        if t<-1 or t>1:
            return "Error, not a good list, values exceed between -1 and 1."
        s = float2bytestring(t)
        w=s+',0,0<cr><lf>'
        g.write(w)

    g.close()
    return 0

def float2bytestring(input_float):
    '''
    This function converts a float elt [-1,1] to a 10-byte string of the format
    0,0,0,0,...,0, where 1,0,0,...,0 is almost -1.
    '''
    #find correct binnumber
    bin_nr = float2bin(input_float)

    #convert to bytes
    bit_string = np.binary_repr(bin_nr,10)

    #reverse order for correct little endian representation
    rev_bit_string=bit_string[::-1]

    output=''
    for bit in rev_bit_string:
        output= output + str(bit) + ','
        
    #output.remove
    return output[:-1] 

    
    
def float2bin(input_float):     
    step_size=2.0/1024

    if input_float<-1 or input_float>1:
        return "Error, not within range."
    if input_float==1.0:
        return 1023

    my_bin = (input_float+1.0)/step_size
      
    return int(np.floor(my_bin))
    
