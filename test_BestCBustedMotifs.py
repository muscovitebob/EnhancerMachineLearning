import unittest
from BestCBustedMotifs import BestCBustedMotifs
from Bio import motifs
import pandas as pd
import random

testfilepathf3 = "cbust_example/f3results.txt"
testfilepathjaspar = "cbust_example/jaspar2.txt"

class TestBestCBustedMotifs(unittest.TestCase):

    def test_jaspar_instantiation(self):
        self.newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(self.newObj.jaspar_matrix_dict, dict)

    def test_identifier_set(self):
        self.newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertNotEquals(len(self.newObj._retrieve_reliable_motifs(0.4,0.05)), 0)

    def test_getter_for_reliable_motif_isdict(self):
        self.newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(self.newObj.get_reliable_motif_dict(0.4, 0.05), dict)

    def test_getter_for_reliable_motif_notempty(self):
        self.newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertNotEqual(len(self.newObj.get_reliable_motif_dict(0.4, 0.05)), 0)

    def test_getter_for_reliable_motif_notempty_large_data(self):
        self.large_object = BestCBustedMotifs("CBUSToutput/CBUSToutput_I_vs_P_f3.txt",
                                              "HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs")
        reliable_large_dict = self.large_object.get_reliable_motif_dict(0.4, 0.05)
        print(random.choice(list(reliable_large_dict.items())))
        self.assertNotEqual(len(reliable_large_dict), 0)


if __name__ == '__main__':
    unittest.main()