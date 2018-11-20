'''
Created on 20 Nov 2018

@author: wimth
'''

import os
import pandas as pd

DIR = 'F:\PROJECT\HomerOutput\cbustOnHomerMotifs'
l_files = ['Homer_Ireg_TOTAL_cbustOut','Homer_Preg_TOTAL_cbustOut']
#l_files = ['Homer_Ireg_TOTAL_cbustOut_toy']

d_sequence_d_motif_crmscore = {}
s_sequence='';s_motif='';crm_score=0
ic_catch_crm=False;ic_catch_motif=False
for file in l_files:
    with open(os.path.join(DIR,file)) as f: 
        for line in f:
            if ic_catch_crm:
                crm_score = float(line.split()[0])
                ic_catch_crm=False
                if d_sequence_d_motif_crmscore.get(s_sequence):
                    d_sequence_d_motif_crmscore[s_sequence][s_motif] = crm_score
                else:
                    d_sequence_d_motif_crmscore[s_sequence] = {s_motif:crm_score}
            elif ic_catch_motif:
                s_motif = line.split()[4]
                ic_catch_motif=False
                ic_catch_crm = True
            elif line.startswith('>'):
                s_sequence = line.split()[0][1:]
                ic_catch_motif = True
                
print('composing the panda')
df = pd.DataFrame.from_dict(d_sequence_d_motif_crmscore,orient='index')
print('writing the panda')
df.to_csv(os.path.join(DIR,'feature_matrix.csv'))