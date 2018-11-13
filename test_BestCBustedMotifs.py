import unittest
from BestCBustedMotifs import BestCBustedMotifs
from Bio import motifs
import pandas as pd

testfilepathf3 = "cbust_example/f3results.txt"
testfilepathjaspar = "cbust_example/jaspar2.txt"

class TestBestCBustedMotifs(unittest.TestCase):

    def test_jaspar_instantiation(self):
        self.newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(self.newObj.jaspar_matrix_dict, dict)

    def test_identifier_set(self):
        self.newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertNotEquals(len(self.newObj._retrieve_reliable_motifs(0.4,0.05)), 0)



if __name__ == '__main__':
    unittest.main()