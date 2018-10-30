#!/usr/bin/env bash

# make sure P_reg.bed and I_reg.bed are in your folder
# beware : the bed file is around 750MB, the fasta file


#determine the average sequence length = this will be taken as the size of the input sequences for the CNN
# = hardcoded in the python script
awk 'OFS="\t" {SUM += $3-$2} END {print SUM, SUM/NR}' I_reg.bed P_reg.bed

python BED_for_deep_learning.py

bedtools getfasta -name -fi GCF_000001405.25_GRCh37.p13_genomic.fna -bed deep_learning.bed  -fo  deep_learning.fna