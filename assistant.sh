#!/usr/bin/env bash
# before running, you need to install homer.v4.9 into the project directory

# uncomment and run the following line if HOMER refuses to work - installs itself
# you need to have perl installed. use your favorite package manager
#perl ./homer.v.4.9/configureHomer.pl

# uncomment the following command to download and unpack the human genome assembly hg19 to use as background
# in motif discovery. warning: this will take a few minutes
#perl ./homer.v4.9/configureHomer.pl -install hg19


# count how many promoter sequences we have in target file
N=$(grep -c "^>" fasta_complete.fasta)


#randomly chosen genomic sequences once - don't rerun if you want to reproduce
#bedtools random -g hg19.genome -n $N -l 150 > background_chunk_coords.bed

BED=background_chunk_coords.bed

#this downloads most of hg19 - 3 GB, so takes some time, comment out when you do this once

for chr in `seq 1 22` X Y
do
    wget -O - -q http://hgdownload.cse.ucsc.edu/goldenPath/hg19/chromosomes/chr$chr.fa.gz | gunzip -c >> hg19.fa
    echo "Chr $chr done"
done
echo "Done hg19.fa download"


#getting the randomly chosen sequence coords in bed file into an actual sequence file

echo "getting fasta from bedfile"
fastaFromBed -fi hg19.fa -bed $BED -fo $BED.fasta
echo "done fasta from bedfile"


./homer.v4.9/bin/homer2 denovo -i fasta_complete.fasta -b background_chunk_coords.bed.fasta > output.txt