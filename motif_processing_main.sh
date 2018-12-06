#!/usr/bin/env bash
# Boris on 3 Dec 18
# This script contains a function to run cbust against every motif presented one by one and save the output
# for later passing to cbust_result.feature_matrix_special to generate the feature matrix

one_by_one_cbuster_denovo () {
    # $1 is the .fna filename, $2 is the motif filename
    SEQUENCE_FILE=$1
    motif_file=$2
    NEW_DIR="cbust_one_by_one_output_denovo_$(date '+%H_%M')"
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
    # $1 is the .fna filename, $2 is the known motif folder name
    SEQUENCE_FILE=$1
    motif_folder=$2
    NEW_DIR="cbust_one_by_one_output_known_$(date '+%H_%M')"
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

one_by_one_cbuster_denovo Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-P_vs_I/homerMotifs.all.motifs

one_by_one_cbuster_denovo Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs

# Run known found motifs I background

one_by_one_cbuster_known Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-P_vs_I/knownResults

one_by_one_cbuster_known Get_BED_FASTA/I_reg.fna HomerOutput/HomerOutput-I_vs_P/knownResults

# Run de novo found motifs P background

one_by_one_cbuster_denovo Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-P_vs_I/homerMotifs.all.motifs

one_by_one_cbuster_denovo Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs

# Run known found motifs P background

one_by_one_cbuster_known Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-P_vs_I/knownResults

one_by_one_cbuster_known Get_BED_FASTA/P_reg.fna HomerOutput/HomerOutput-I_vs_P/knownResults

# the two P_vs_I and I_vs_P files are then concatenated and we run the feature_matrix_special cbust_result.py method
# on them to create a feature matrix