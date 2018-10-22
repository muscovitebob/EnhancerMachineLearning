'''
Created on 16 Oct 2018

@author: wimth
'''
import pandas as pd
import re,os

save_dir = r'F:\PROJECT\DataWrangling'
sub_dir = ''
f_output_name = 'bed_v1'
f_input_name = 'GSE75661_7.5k_collapsed_counts.txt'
output_path= os.path.join(save_dir,sub_dir,f_output_name +'.csv')
input_path = os.path.join(save_dir,sub_dir,f_input_name)
df_7_5K_data = pd.read_csv(input_path,sep='\t')

ls_columns = ["oligo",   #this array determines the order of the columns (besides the names)
           "chrom",
           "start",
           "end"
           ]

l_oligo = []
l_chrom = []
l_start = []
l_end = []

l_oligo_rs = []

p1 = re.compile('^chr')
p2 = re.compile('[:_]')
for oligo in df_7_5K_data.Oligo:
    print (oligo)
    m = p1.match(oligo)
    if m:
        l_oligo_split = p2.split(oligo)
        nb_startpos = int(l_oligo_split[1]) - 74
        l_oligo.append(oligo)
        l_chrom.append(l_oligo_split[0])
        l_start.append(nb_startpos)
        l_end.append(nb_startpos+150)
    else:
        l_oligo_split = oligo.split('_')
        l_oligo.append(oligo)
        l_chrom.append(l_oligo_split[0])
        l_start.append(0)
        l_end.append(0)
        
        l_oligo_rs.append(l_oligo_split[0])

d_df = {}  # the dict that will be used to create the dataframe  
d_df[ls_columns[0]] = l_oligo
d_df[ls_columns[1]] = l_chrom
d_df[ls_columns[2]] = l_start
d_df[ls_columns[3]] = l_end
data=pd.DataFrame(d_df)
data.to_csv(output_path,columns=ls_columns,header=True)

f_output_name = 'rs_list'
output_path= os.path.join(save_dir,sub_dir,f_output_name +'.txt')
with open(output_path, 'w') as f:
    for item in l_oligo_rs:
        f.write("%s\n" % item)

# d_df = {} 
# d_df['oligo_rs'] = l_oligo_rs
# data=pd.DataFrame(d_df)
# f_output_name = 'rs_list'
# output_path= os.path.join(save_dir,sub_dir,f_output_name +'.txt')
# data.to_csv(output_path,columns=['oligo_rs'],header=False)
