import unittest
from crawler.api import API
from crawler.utils import fetch

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.api = API("http://www.omdbapi.com/", "your_api_key_here", dbpath='test_classified.db')

    def test_collect(self):
        result = self.api.collect()
        self.assertIsInstance(result, list)

    def test_search(self):
        file_id = 1
        title = "Inception"
        year = "2010"
        result = self.api.search(file_id, title, year)
        self.assertIsNotNone(result)

    def test_is_processed(self):
        file_id = 1
        self.api.save(file_id, {"Title": "Inception"})
        self.assertTrue(self.api.is_processed(file_id))

    def test_fetch(self):
        columns = ['file_id', 'title', 'year']
        table_title = 'filedetails'
        data = fetch(columns, table_title)
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()