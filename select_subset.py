import pandas as pd
import numpy as np

def format_beds(bed_filepath):
    genomic_position_list = []
    with open(bed_filepath, 'r') as handle:
        for line in handle:
            splt = line.split("\t")
            current_line = splt[0]+":"+splt[1]+"-"+splt[2].rstrip()
            genomic_position_list.append(current_line)
    handle.close()
    return genomic_position_list

P_reg_test = "CNN_model_Keras/Data_Split_v3/P_reg_test.bed"
I_reg_test = "CNN_model_Keras/Data_Split_v3/I_reg_test.bed"


P_reg_test_positions = format_beds(P_reg_test)
I_reg_test_positions = format_beds(I_reg_test)

P_and_I_reg_test_positions = P_reg_test_positions + I_reg_test_positions

# ['chr11:18142000-18143215' 'chr20:32720468-32721138'
#  'chr1:17495715-17496285' 'chr1:200398305-200398635'
#  'chr3:71545725-71545958' 'chr12:45677775-45677858']
# these are not in our feature matrix at all. No time to figure out why, so we just drop them.

anomaly = ['chr11:18142000-18143215', 'chr20:32720468-32721138','chr1:17495715-17496285', 'chr1:200398305-200398635',
           'chr3:71545725-71545958', 'chr12:45677775-45677858']

P_and_I_reg_test_positions_abridged = [x for x in P_and_I_reg_test_positions if x not in anomaly]

inputMatrixName = "FMs/FM_orig.csv"
outputMatrixName = "FMs/FM_orig_test.csv"
subsetMatrixName1 = "subsets/P_test.csv"
subsetMatrixName2 = "subsets/I_test.csv"

input_matrix = pd.read_csv(inputMatrixName, index_col=0)

train_matrix = input_matrix.drop(P_and_I_reg_test_positions_abridged)
not_in_set_P_and_I_reg_test_positions_abridged = set(input_matrix.index) - set(train_matrix.index)
test_matrix = input_matrix.loc[list(not_in_set_P_and_I_reg_test_positions_abridged)]

test_matrix.to_csv("FMs/FM_orig_test.csv")
train_matrix.to_csv("FMs/FM_orig_train.csv")

