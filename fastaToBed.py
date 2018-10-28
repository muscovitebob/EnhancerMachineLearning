import sys

'''
This script can be used to convert the positive and negative example files created by Wim
to the bed formats as used by i-cisTarget. 
Use the python script in command line and put the target fasta file as first argument. 
Script will create an output file called "pos_ex.bed" i.d. a bed file with the positive examples of enhancer sequences.
'''
with open("pos_ex.bed", "a") as bed:
    with open(sys.argv[1], 'r') as handle:
        for line in handle:
            if line.startswith('>'):
                splt1 = line[1:].split(":")
                splt2 = splt1[1].split("-")
                chr = splt1[0]
                loc1 = splt2[0]
                loc2 = splt2[1]
                bed.write(chr + "\t" + loc1 + "\t" + loc2)
