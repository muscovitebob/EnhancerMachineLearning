'''
Created on 29 Oct 2018

@author: wimth
'''
WINDOW_SIZE = 815 #this is the average sequence length in the bed files, check via awk 'OFS="\t" {SUM += $3-$2} END {print SUM, SUM/NR}' I_reg.bed P_reg.bed
STRIDE = 100

l_files = ['P_reg.bed','I_reg.bed']


with open('deep_learning.bed', 'w',newline='') as f_out: 

    for file in l_files:
        if file == 'P_reg.bed':
            s_suffix = 'P'
        else:
            s_suffix = 'I'
        
        with open(file) as f: 
            for s_bed in f:
                
                location,start_pos,end_pos = s_bed.split('\t')
                start_pos = int(start_pos)
                end_pos = int(end_pos)
                window_start_pos= max(0,start_pos - WINDOW_SIZE + STRIDE)
                window_end_pos = window_start_pos + WINDOW_SIZE
                while window_start_pos < end_pos:
                    s_name = location + ":" + str(window_start_pos) + "-" + str(window_end_pos) + "_" + s_suffix
                    f_out.write(location + "\t" + str(window_start_pos) + "\t" + str(window_end_pos) + "\t" +  s_name + '\n')
                    window_start_pos += STRIDE
                    window_end_pos += STRIDE
