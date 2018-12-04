#!/usr/bin/env bash
# Boris on 3 Dec 18
# This script contains a function to run cbust against every motif presented one by one and save the output
# for later passing to cbust_result.feature_matrix_special to generate the feature matrix

NEW_DIR=cbustout
# SEQUENCE_FILE = I_reg.fna or P_reg.fna

# $1 is the .fna filename, $2 is the motif filename
one_by_one_cbuster () {
    SEQUENCE_FILE=$1
    motif_file=$2
    NEW_DIR="cbust_one_by_one_output_$(date '+%H_%M')"
    mkdir $NEW_DIR
    #awk '{print ">" $0 > "matrix_temp_" NR}' RS='>' $motif_file
    gcsplit -z -s $motif_file '/>/' '{*}'
    mv xx* $NEW_DIR
    for filename in $NEW_DIR/xx*;
        do
          echo $filename
          ./cbust -g 20 -l -c 0 -m 0 -f 1 $filename $SEQUENCE_FILE > "$NEW_DIR"/cbusted_one_by_one_results.txt
        done
}

one_by_one_cbuster Get_BED_FASTA/I_reg.fna RSATed_homer_motifs/I_vs_P_RSATed_converted.cb
