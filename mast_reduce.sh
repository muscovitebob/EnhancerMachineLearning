#!/usr/bin/env bash

echo "Running MAST matrix reduction on unbalanced data..."

Rscript Mast_reduce.R feature_matrix_2.csv feature_matrix_2_mast_reduced.csv

echo -e "\nYou should now run this matrix through Boruta to further reduce it."

echo "Running MAST matrix reduction on balanced data..."

Rscript Mast_reduce.R FMs/FM_orig_train.csv FMs/FM_mast_reduced_train.csv

echo -e "\nYou should also run this matrix through Boruta to further reduce it."