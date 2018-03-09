import unittest
import memc_load
import os
from optparse import OptionParser


class TestMemcLoad(unittest.TestCase):
    def setUp(self):
        op = OptionParser()
        op.add_option("-t", "--test", action="store_true", default=False)
        op.add_option("-l", "--log", action="store", default=None)
        op.add_option("--dry", action="store_true", default=True)
        op.add_option("--pattern", action="store", default="test_logs/*.tsv.gz")
        op.add_option("--idfa", action="store", default="127.0.0.1:33013")
        op.add_option("--gaid", action="store", default="127.0.0.1:33014")
        op.add_option("--adid", action="store", default="127.0.0.1:33015")
        op.add_option("--dvid", action="store", default="127.0.0.1:33016")
        (self.opts, args) = op.parse_args()

    def test_file_rename(self):
        memc_load.main(self.opts)
        self.assertEqual(True, os.path.isfile('test_logs/.sample.tsv.gz'))
        self.assertEqual(True, os.path.isfile('test_logs/.sample1.tsv.gz'))
        self.assertEqual(True, os.path.isfile('test_logs/.sample2.tsv.gz'))


if __name__ == "__main__":
    unittest.main()
