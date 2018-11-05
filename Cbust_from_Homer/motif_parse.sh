#!/bin/bash

PATH=$PATH\:/mnt/c/Users/wimth/Documents/BioInfSoftware/ClusterBuster; export PATH
mkdir cbustout
for filename in *.motif
do
	echo "${filename}"
	awk '$1 ~ /^>/ { print ">" $2};$1 ~ /^[0-9]/{print}' "${filename}" > matrix_temp 
	cbust -g20 -l -c 0 -m 0 -f 1 matrix_temp I_reg.fna > cbustOut/Homer_PvsI_Known_"${filename}"_cbustOut 
done

find /cbustout -name *cbustOut -exec cat {} + > Homer_PvsI_Known_TOTAL_cbustOut
