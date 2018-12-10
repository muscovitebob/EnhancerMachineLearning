#!/usr/bin/env bash

echo "Running MAST matrix reduction..."

Rscript Mast_reduce.R feature_matrix_2.csv feature_matrix_2_mast_reduced.csv

echo -e "\nYou should now run this matrix through Boruta to further reduce it."