#!/usr/bin/env bash
# Boris on 3 Dec 18
# This script contains a function to run cbust against every motif presented one by one and save the output
# for later passing to cbust_result.feature_matrix_special to generate the feature matrix

NEW_DIR=cbustout
# SEQUENCE_FILE = I_reg.fna or P_reg.fna

# $1 is the directory name, $2 is the .fna filename, $3 is the motif filename
one_by_one_cbuster () {
    NEW_DIR = $1
    fna = $2
    SEQUENCE_FILE = $3
    mkdir $NEW_DIR
    for filename in $(find IvsP PvsI -name "*.motif")
    do
        # echo "${filename}"
        #retrieve the single motif, put into a temp file
        awk '$1 ~ /^>/ { print ">" $2};$1 ~ /^[0-9]/{print}' "${filename}" > matrix_temp
        #run temp file through cbust, append to new f1 type matri
        cbust -g 20 -l -c 0 -m 0 -f 1 matrix_temp "$SEQUENCE_FILE" > "$NEW_DIR"/Homer__"${filename///}"_cbustOut
    done
    cat $NEW_DIR/* > Homer_Ireg_TOTAL_cbustOut
    #find /cbustout/ -name *cbustOut -exec cat {} + > Homer_IvsP_Known_TOTAL_cbustOut
}
