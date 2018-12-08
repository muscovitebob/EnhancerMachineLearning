setwd('/Users/lucascoppens/documents/Last\ sem/IBP/Github')
library(MAST)
library(reshape2)

FM = read.csv('feature_matrix_2.csv')

head(FM)

FM[is.na(FM)] <- 0

# Create SCA object
flattenedSet <- melt(FM, id=c("X","X_label"))
head(flattenedSet)
colnames(flattenedSet) <- c("ID", "Class", "Motif", "Score")

FM_sca_format = FromFlatDF(flattenedSet, idvars="ID", primerid="Motif", measurement="Score", cellvars="Class")

# Run
lrtOut <- LRT(FM_sca_format, comparison = "Class")  # Each label vs "rest"
lrtOut <- data.frame(lrtOut, pAdj=p.adjust(lrtOut$p.value, method="fdr"))
lrtOut <- lrtOut[order(lrtOut$pAdj, decreasing=TRUE),]

# Select 50%
median <- median(lrtOut$pAdj)
motifs <- subset(lrtOut, pAdj < median, select = c(primerid))

new_FM <- FM[,c(motifs$primerid)]

write.csv(new_FM, "feature_matrix_2_mast_reduced")


