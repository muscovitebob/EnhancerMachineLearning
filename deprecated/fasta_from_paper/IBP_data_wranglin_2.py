'''
Created on 22 Oct 2018

@author: wimth
'''
import pandas as pd
import re,os

save_dir = r''
sub_dir = ''
f_output_name = 'bed_withrsadded'
f_input_name_1 = 'bed_v1.csv'
f_input_name_2 = 'rs_out.bed'
output_path= os.path.join(save_dir,sub_dir,f_output_name +'.csv')

input_path = os.path.join(save_dir,sub_dir,f_input_name_1)
bed_v1_data = pd.read_csv(input_path,sep=',',index_col=0)

input_path = os.path.join(save_dir,sub_dir,f_input_name_2)
rs_out_data = pd.read_csv(input_path,sep='\t',header=None)
rs_out_data.columns = bed_v1_data.columns
bed_v1_data['label'] = 'pos'
rs_out_data['label'] = 'neg'

rs_out_data['start'] -= 74
rs_out_data['end'] += 75

frames = [bed_v1_data, rs_out_data]
result = pd.concat(frames,ignore_index=True)

result.to_csv(output_path,header=True)