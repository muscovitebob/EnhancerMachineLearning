from Bio import motifs
import pandas as pd
import homer_io

testfilepath = "cbust_example/f3results.txt"

class BestCBustedMotifs:
    '''
    This class represents the best motifs as determined by cbust - we take the highest scoring motifs from
    the highest scoring clusters.
    '''
    def __init__(self, f3_output_filepath, jaspar_matrix_filepath):
        self.primary_cbust_matrix = pd.read_csv(f3_output_filepath, error_bad_lines=False, sep='\t', skiprows=3, skipfooter=9)
        self.cbust_run_info = pd.read_csv("cbust_example/f3results.txt", error_bad_lines=False)[-8:]
        self.jaspar_matrix = motifs.read(jaspar_matrix_filepath, 'jaspar')






#homerMotifs = homer_io.read_motifs("HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs", residues ="ACGT")
