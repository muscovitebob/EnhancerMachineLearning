#!/usr/bin/env bash
# Lucas on 11 dec 18
# converts  FMs/FM_orig.csv to FMs/FM_orig_test.csv, FMs/FM_orig_train.csv and FMs/FM_orig_val.csv
# in such a way that the new test/train FM and wims test/train set match


python bedToId.py CNN_model_Keras/Data_Split_v3/P_reg_test.bed subsets/P_test.csv
python bedToId.py CNN_model_Keras/Data_Split_v3/I_reg_test.bed subsets/I_test.csv

python bedToId.py CNN_model_Keras/Data_Split_v3/P_reg_train.bed subsets/P_train.csv
python bedToId.py CNN_model_Keras/Data_Split_v3/I_reg_train.bed subsets/I_train.csv

Rscript select_subset.R FMs/FM_orig.csv FMs/FM_orig_test.csv subsets/P_test.csv subsets/I_test.csv

# Doing this will lose you the validation set which should be part of the train set in this workflow
#Rscript select_subset.R FMs/FM_orig.csv FMs/FM_orig_train.csv subsets/P_train.csv subsets/I_train.csv

# In a consecutive step, lets reduce the newly created FMs/FM_orig_train to a mast reduced FMs/FM_mast_reduced_train.csv

Rscript Mast_reduce.R FMs/FM_orig_train.csv FMs/FM_mast_reduced_train.csv