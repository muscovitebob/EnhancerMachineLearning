#!/usr/bin/env bash
# Boris on 3 Dec 18
# This script contains a function to run cbust against every motif presented one by one and save the output
# for later passing to cbust_result.feature_matrix_special to generate the feature matrix

one_by_one_cbuster_denovo () {
    # $1 is the .fna filename, $2 is the motif filename, $3 is the output folder name
    SEQUENCE_FILE=$1
    motif_file=$2
    NEW_DIR=$3
    mkdir $NEW_DIR
    gcsplit -z -s $motif_file '/>/' '{*}'
    mv xx* $NEW_DIR
    for filename in $NEW_DIR/xx*;
        do
           awk '$1 ~ /^>/ { print ">" $2};$1 ~ /^[0-9]/{print}' "${filename}" > matrix_temp
           cat matrix_temp > $filename
          ./cbust -g 20 -l -c 0 -m 0 -f 1 $filename $SEQUENCE_FILE >> "$NEW_DIR"/cbusted_one_by_one_results.txt
        done
}

one_by_one_cbuster_known () {
    # $1 is the .fna filename, $2 is the known motif folder name, $3 is the output folder name
    SEQUENCE_FILE=$1
    motif_folder=$2
    NEW_DIR=$3
    mkdir $NEW_DIR
    cp $motif_folder/*.motif $NEW_DIR
    for filename in $NEW_DIR/*.motif;
        do
          awk '$1 ~ /^>/ { print ">" $2};$1 ~ /^[0-9]/{print}' "${filename}" > matrix_temp
          cat matrix_temp > $filename
          ./cbust -g 20 -l -c 0 -m 0 -f 1 $filename $SEQUENCE_FILE >> "$NEW_DIR"/cbusted_one_by_one_results.txt
        done
}
# Run de novo found motifs I background

one_by_one_cbuster_denovo Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-P_vs_I/homerMotifs.all.motifs cbust_one_by_one_denovo_Ireg_P_vs_I

one_by_one_cbuster_denovo Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs cbust_one_by_one_denovo_Ireg_I_vs_P

# Run known found motifs I background

one_by_one_cbuster_known Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-P_vs_I/knownResults cbust_one_by_one_known_Ireg_P_vs_I

one_by_one_cbuster_known Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-I_vs_P/knownResults cbust_one_by_one_known_Ireg_I_vs_P

# Concat final file for I_reg

cat cbust_one_by_one_denovo_Ireg_P_vs_I/cbusted_one_by_one_results.txt cbust_one_by_one_denovo_Ireg_I_vs_P/cbusted_one_by_one_results.txt \
    cbust_one_by_one_known_Ireg_P_vs_I/cbusted_one_by_one_results.txt  cbust_one_by_one_known_Ireg_I_vs_P/cbusted_one_by_one_results.txt \
    > immovable_data/I_one_by_one_cbusted.txt

# Run de novo found motifs P background

one_by_one_cbuster_denovo Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-P_vs_I/homerMotifs.all.motifs cbust_one_by_one_denovo_Preg_P_vs_I

one_by_one_cbuster_denovo Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs cbust_one_by_one_denovo_Preg_I_vs_P

# Run known found motifs P background

one_by_one_cbuster_known Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-P_vs_I/knownResults cbust_one_by_one_known_Preg_P_vs_I

one_by_one_cbuster_known Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-I_vs_P/knownResults cbust_one_by_one_known_Preg_I_vs_p

# Concat final file for P_reg

cat cbust_one_by_one_denovo_Preg_P_vs_I/cbusted_one_by_one_results.txt cbust_one_by_one_denovo_Preg_I_vs_P/cbusted_one_by_one_results.txt \
    cbust_one_by_one_known_Preg_P_vs_I/cbusted_one_by_one_results.txt  cbust_one_by_one_known_Preg_I_vs_P/cbusted_one_by_one_results.txt \
    > immovable_data/P_one_by_one_cbusted.txt