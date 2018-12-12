import pandas as pd
import numpy as np

P_reg_test = "CNN_model_Keras/Data_Split_v3/P_reg_test.bed"
I_reg_test = "CNN_model_Keras/Data_Split_v3/I_reg_test.bed"


def format_beds(bed_filepath):
    genomic_position_list = []
    with open(bed_filepath, 'r') as handle:
        for line in handle:
            splt = line.split("\t")
            current_line = splt[0]+":"+splt[1]+"-"+splt[2].rstrip()
            genomic_position_list.append(current_line)
    handle.close()
    return genomic_position_list

P_reg_test_positions = format_beds(P_reg_test)
I_reg_test_positions = format_beds(I_reg_test)


inputMatrixName = "FMs/FM_orig.csv"
outputMatrixName = "FMs/FM_orig_test.csv"
subsetMatrixName1 = "subsets/P_test.csv"
subsetMatrixName2 = "subsets/I_test.csv"

input_matrix = pd.read_csv(inputMatrixName, index_col=0)

