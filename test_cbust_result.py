import unittest
from cbust_result import cbust_result
from Bio import motifs
import pandas as pd
import random

testfilepathf3 = "cbust_example/f3results.txt"
testfilepathjaspar = "cbust_example/jaspar2.txt"

class TestBestCBustedMotifs(unittest.TestCase):

    def test_jaspar_instantiation(self):
        self.newObj = cbust_result(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(self.newObj.jaspar_matrix_dict, dict)

    def test_identifier_set(self):
        self.newObj = cbust_result(testfilepathf3, testfilepathjaspar)
        self.assertNotEquals(len(self.newObj._retrieve_reliable_motifs(0.4,0.05)), 0)

    def test_getter_for_reliable_motif_isdict(self):
        self.newObj = cbust_result(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(self.newObj.get_reliable_motif_dict(0.4, 0.05), dict)

    def test_getter_for_reliable_motif_notempty(self):
        self.newObj = cbust_result(testfilepathf3, testfilepathjaspar)
        self.assertNotEqual(len(self.newObj.get_reliable_motif_dict(0.4, 0.05)), 0)

    def test_getter_for_reliable_motif_notempty_large_data(self):
        self.large_object = cbust_result("CBUSToutput/CBUSToutput_I_vs_P_f3.txt",
                                              "HomerOutput/HomerOutput-I_vs_P/homerMotifs.all.motifs")
        reliable_large_dict = self.large_object.get_reliable_motif_dict(0.4, 0.05)
        print(random.choice(list(reliable_large_dict.items())))
        self.assertNotEqual(len(reliable_large_dict), 0)

    def test_motif_matrix_writer(self):
        self.newObj = cbust_result(testfilepathf3, testfilepathjaspar)
        reliable_dict = self.newObj.get_reliable_motif_dict(0.4, 0.05)
        self.newObj.write_reliable_motif_matrix(reliable_dict, "test_matrix.txt")


if __name__ == '__main__':
    unittest.main()