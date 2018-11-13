#!/usr/bin/env bash
# Boris on 28 Oct 18

# HOMER running!

#./homer.v4.9/bin/homer2 denovo -i fasta_complete_pos_ex.fa -b fasta_complete_neg_ex.fa > HOMERoutput.txt

# feed HOMER into ClusterBuster

./cbust -l -f 3 -c 0.01 HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs \
Get_BED_FASTA/I_reg.fna > CBUSToutput/CBUSToutput_I_vs_P_f3.txt

./cbust -l -f 3 -c 0.01 HomerOutput/HomerOutput-P_vs_I/homerMotifs.all.motifs \
Get_BED_FASTA/P_reg.fna > CBUSToutput/CBUSToutput_P_vs_I_f3.txt

./cbust -l -f 0 -c 0 -m 0 HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs \
Get_BED_FASTA/I_reg.fna > CBUSToutput/CBUSToutput_I_vs_P_f0.txt

./cbust -l -f 2 -c 0 -m 0 HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs \
Get_BED_FASTA/I_reg.fna > CBUSToutput/CBUSToutput_I_vs_P_f2.txt