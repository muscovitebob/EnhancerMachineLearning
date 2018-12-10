#!/usr/bin/env Rscript
library(MAST)
library(reshape2)
library(dplyr)

# Example run command from bash:
# Rscript Mast_reduce.R feature_matrix_2.csv outputMatrixTest.csv
args = commandArgs(trailingOnly=TRUE)
#args = c("feature_matrix_2.csv", "testMatrix.csv")
inputMatrixName = args[1]
outputMatrixName = args[2]

FM = read.csv(inputMatrixName, check.names=FALSE)

FM[is.na(FM)] <- 0

# Create SCA object
flattenedSet <- melt(FM, id=c("id","_label"))
colnames(flattenedSet) <- c("ID", "Class", "Motif", "Score")

FM_sca_format = FromFlatDF(flattenedSet, idvars="ID", primerid="Motif", measurement="Score", cellvars="Class")

# Run
lrtOut <- LRT(FM_sca_format, comparison = "Class")  # Each label vs "rest"
lrtOut <- data.frame(lrtOut, pAdj=p.adjust(lrtOut$p.value, method="fdr"))
lrtOut <- lrtOut[order(lrtOut$pAdj, decreasing=TRUE),]

head(lrtOut,30)

summary(lrtOut)

# Select 50%
median <- median(lrtOut$pAdj)
motifs <- subset(lrtOut, pAdj < median, select = c(primerid))

new_FM <- FM[,c(motifs$primerid)]
new_df <- new_FM %>% select("id", "_label", everything())

write.csv(new_df, outputMatrixName, row.names = F)