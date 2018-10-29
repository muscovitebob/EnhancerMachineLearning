from Bio import motifs
import homer_io


homerMotifs = homer_io.read_motifs("HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs", residues ="ACGT")
# Make sure the matrices are correctly read
print(homerMotifs[1])
