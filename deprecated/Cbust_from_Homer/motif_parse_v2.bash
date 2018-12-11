#!/bin/bash
PATH=$PATH\:/mnt/c/Users/wimth/Documents/BioInfSoftware/ClusterBuster; export PATH

NEW_DIR=cbustout
SEQUENCE_FILE=I_reg.fna

mkdir $NEW_DIR
for filename in $(find IvsP PvsI -name "*.motif")
do
	echo "${filename}"
	awk '$1 ~ /^>/ { print ">" $2};$1 ~ /^[0-9]/{print}' "${filename}" > matrix_temp 
	cbust -g20 -l -c 0 -m 0 -f 1 matrix_temp "$SEQUENCE_FILE" > "$NEW_DIR"/Homer__"${filename///}"_cbustOut 
done
cat $NEW_DIR/* > Homer_Ireg_TOTAL_cbustOut
#find /cbustout/ -name *cbustOut -exec cat {} + > Homer_IvsP_Known_TOTAL_cbustOut


