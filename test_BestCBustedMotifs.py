import unittest
from BestCBustedMotifs import BestCBustedMotifs
from Bio import motifs
import pandas as pd

testfilepathf3 = "cbust_example/f3results.txt"
testfilepathjaspar = "cbust_example/jaspar2.txt"

class TestBestCBustedMotifs(unittest.TestCase):

    def test_jaspar_instantiation(self):
        newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(newObj.jaspar_matrix, motifs.jaspar)

    def test_pandas_instantiation(self):
        newObj = BestCBustedMotifs(testfilepathf3, testfilepathjaspar)
        self.assertIsInstance(newObj.primary_cbust_matrix, pd.DataFrame)

