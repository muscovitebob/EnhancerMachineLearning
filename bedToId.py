import sys
import pandas as pd
import numpy as np

"""
Convert the bed files containing sequence ID information
to csv files containing the same information but parsed into
the feature matrix id format

Example: python bed_to_id.py CNN_model_Keras/Data_Split_v3/I_reg_test.bed I_test.csv
"""

df= pd.DataFrame()
new_block = False
count = 0

outputfile = sys.argv[2]

with open(outputfile,'wb') as outfile:
	with open(sys.argv[1], 'r') as handle:
		for line in handle:
			splt = line.split("\t")
			outfile.write(splt[0]+":"+splt[1]+"-"+splt[2])
