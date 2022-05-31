import unittest
import pandas as pd
import numpy as np
import sys
import os
from pprint import pprint
import json
sys.path.append('../')
from src.fetch_data import DataLoader
from src.rotating_logs import get_rotating_log


#logger = get_rotating_log(filename='unittest_data_loader.log', logger_name='TestDataLoaderLogger')


class TestDataLoader(unittest.TestCase):

    def setUp(self) -> pd.DataFrame:
        pass
        

    def test_read_csv(self):
        ad_df = DataLoader.read_csv('tests/test_data.csv')
        self.assertEqual(len(ad_df), 6)
        #logger.info(f"Finished testing csv from disk reader")
    
    def test_dvc_get_data(self):
        data_path = 'data/raw/test.csv'
        version = '90f3a7cc29d56a07cb6cb6e5bb0944d17a438ff7'#, 'raw_data'
        repo = '.'
        test_df = DataLoader.dvc_get_data(data_path, version, repo)
        self.assertTrue(test_df['Open'].isnull().any())
        #logger.info(f"Finished testing csv from DVC reader")


if __name__ == '__main__':
    unittest.main()
