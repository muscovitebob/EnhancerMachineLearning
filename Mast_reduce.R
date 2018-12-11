#!/usr/bin/env Rscript
library(MAST)
library(reshape2)
library(dplyr)

# Example run command from bash:
# Rscript Mast_reduce.R feature_matrix_2.csv outputMatrixTest.csv
args = commandArgs(trailingOnly=TRUE)
#args = c("FMs/FM_orig_train.csv", "FMs/FM_mast_reduced_train.csv")
inputMatrixName = args[1]
outputMatrixName = args[2]

FM = read.csv(inputMatrixName, check.names=FALSE)

colnames(FM)

FM[is.na(FM)] <- 0

# Create SCA object
flattenedSet <- melt(FM, id=c("id","_label"))
head(flattenedSet)
colnames(flattenedSet) <- c("ID", "Class", "Motif", "Score")

FM_sca_format = FromFlatDF(flattenedSet, idvars="ID", primerid="Motif", measurement="Score", cellvars="Class")

n_occur <- data.frame(table(FM_sca_format$Motif))
n_occur[n_occur$Freq > 1,]


# Run
lrtOut <- LRT(FM_sca_format, comparison = "Class")  # Each label vs "rest"
lrtOut <- data.frame(lrtOut, pAdj=p.adjust(lrtOut$p.value, method="fdr"))
lrtOut <- lrtOut[order(lrtOut$pAdj, decreasing=TRUE),]

tail(lrtOut,30)

summary(lrtOut)

# Select 50%
motifs <- subset(lrtOut, pAdj < 0.05, select = c(primerid))

mtfs <- c()
for(motif in motifs$primerid){
  if (endsWith(motif, ".1")){
    mtfs <- c(mtfs, substr(motif, 1, nchar(motif)-2))
  }else{
    mtfs <- c(mtfs, motif)
  }
}

mtfs1 <- c()
for(motif in mtfs){
  if (endsWith(motif, ".1")){
    mtfs1 <- c(mtfs1, substr(motif, 1, nchar(motif)-2))
  }else{
    mtfs1 <- c(mtfs1, motif)
  }
}

new_FM <- FM[,c("id", "_label", mtfs1)]

write.csv(new_FM, outputMatrixName, row.names = F)