#!/usr/bin/env bash


# How to get the FASTA files starting from the data in the paper.

# STEP1: get original data
# -----
# Get GSE75661_7.5k_collapsed_counts.txt.gz from https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE75661

# STEP2: parsing via IBP_data_wranglin.py
# -----
# Use python script IBP_data_wranglin.py to create

# o	bed_v1.csv : csvfile in bed like format => oligoID / chrom / start / end
#		the positive examples already have the right range (the SNV sits in the middle (starting at -74bp ending at +75bp, giving a range of 150bp
#		the negative examples (rs number).  The range for these are still blank.  (need to be obtained in the following step)
# o	rs_list.txt : text file of all the negatives. = list of SNP-id (eg. rs427230)

# STEP3: obtaining the location of the SNPs
# -----
# o	get BEDfile of hg19 snps:
mysql --user=genome --host=genome-mysql.cse.ucsc.edu -A -N -D hg19 -e 'SELECT chrom, chromStart, chromEnd, name FROM snp147Common' > snp147Common.bed

# o	get ranges of the SNPs :
awk 'NR==FNR {h[$1] = 1; next} {if(h[$4]==1) print$4 ,"\t",$1 ,"\t",$2 ,"\t",$3}' rs_list.txt snp147Common.bed > rs_out.bed

# STEP4: create bed_withrsadded.csv via excel
# -----
# -via simple copy paste in excel :  add the ranges of the SNPs to the bed_v1.csv.
# -mark the positive and negative examples via an extra column (for future reference)
# expand the range of the snps to 150bp (with SNP centered)

# STEP5: make bed-file from csv
# -----
awk -F"," '{ print $3 "\t" $4  "\t" $5 }'  bed_withrsadded.csv |uniq | tr -d ' ' | tr -d '\r'| sed '1d' > complete.bed

# remark :  the original file contained SNV of the enhancers, and also both variants of the SNP.  This will create double ranges.
# These variants and minor alleles are filtered out, so are not considered in the final file.
# (these could be obtained by matching with a second supplementary file GSE75661_7.5k_Barcode_Oligo.tab.gz, but at this point this is not done)

# STEP6: use BED-tools to get fasta from bed file

# o   retrieve HG19 fasta file : GCF_000001405.25_GRCh37.p13_genomic.fna

# o	change headers of chromosomes to match the bed-file
sed -i -E 's/>NC_0*([^.]*).(.*)/>chr\1/' GCF_000001405.25_GRCh37.p13_genomic.fna

# o	create fasta file via bed-tools
bedtools getfasta -fi GCF_000001405.25_GRCh37.p13_genomic.fna -bed complete.bed  -fo  fasta_complete.fna

# o	split into positve and negatives (first 272 records are positives, equaling 136 enhancer sequences)
# fasta_complete_pos_ex.fna
# fasta_complete_neg_ex.fna
