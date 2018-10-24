#get second excel file (supplementary data 2) from https://www.nature.com/articles/ncomms7683#supplementary-information
#save the excel file as a tab-separated file
#to get the fasta sequences you need the hg19 fasta file in your folder
sed 1,3d ncomms7683-s3.txt  | awk '$12 = /I_reg/ { print $8,"\t",$9,"\t" $10 }' | tr -d ' ' |uniq > I_reg.bed
sed 1,3d ncomms7683-s3.txt  | awk '$12 = /P_reg/ { print $8,"\t",$9,"\t",$10 }' | tr -d ' ' |uniq > P_reg.bed
bedtools getfasta -fi GCF_000001405.25_GRCh37.p13_genomic.fna -bed I_reg.bed  -fo  I_reg.fna
bedtools getfasta -fi GCF_000001405.25_GRCh37.p13_genomic.fna -bed P_reg.bed  -fo  P_reg.fna