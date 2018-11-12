from Bio import motifs
import pandas as pd
import io
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
        self.motif_names = list(self.primary_cbust_matrix.columns)[4:]
        self.jaspar_matrix_dict = self._read_jaspar_to_dict_of_names_and_pandas(jaspar_matrix_filepath)

    def _read_jaspar_to_dict_of_names_and_pandas(self, jaspar_matrix_filepath):
        jaspar_matrix_dict = dict()
        with open(jaspar_matrix_filepath) as jaspar_monolith:
            content = jaspar_monolith.read()
            one_matrix_per_string = content.split(sep=">")
            for i in range(1, len(one_matrix_per_string)):
                first = one_matrix_per_string[i]
                first1 = first.split("\n")
                jaspar_name = first1[0]
                first2 = '\n'.join(first1[1:])
                jaspar_matrix = pd.read_table(io.StringIO(first2), sep="\t",
                                              index_col=False, header=None, names=['A', 'C', 'G', 'T'])
                jaspar_matrix_dict[jaspar_name] = jaspar_matrix
        jaspar_monolith.close()
        return jaspar_matrix_dict









#homerMotifs = homer_io.read_motifs("HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs", residues ="ACGT")
