#!/usr/bin/env Rscript

# Select a subset from the feature matrix containing only rows given by the 
# id containing csv files passed as second argument and third argument

# Example run command from bash:
# Rscript select_subset.R feature_matrix_2.csv feature_matrix_2_test.csv I_test.csv P_test.csv

args = commandArgs(trailingOnly=TRUE)

inputMatrixName = args[1]
outputMatrixName = args[2]

subsetMatrixName1 = args[3]
subsetMatrixName2 = args[4]

FM = read.csv(inputMatrixName, check.names=FALSE)

subsetIDs1 = read.csv(subsetMatrixName1, check.names=FALSE, header = F)
subsetIDs2 = read.csv(subsetMatrixName2, check.names=FALSE, header = F)

new_FM <- FM[c(subsetIDs1$V1, subsetIDs2$V1),]

write.csv(new_FM, outputMatrixName, row.names = F)


