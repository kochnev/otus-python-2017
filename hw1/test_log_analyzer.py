import os
import unittest
import log_analyzer as la
import uuid

config = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./test_reports",
    "LOG_DIR": "./test_log",
    "TS_DIR": "./test_ts",
    "THRESHOLD_ERR": 0.3
}


class TestLogAnalyzer(unittest.TestCase):
    def setUp(self):
        self.sample_list = [('/api/v2/banner/25019354', 0.39),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                             0.133),
                            ('/api/v2/banner/25019354', 0.39),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                             0.133),
                            ('/api/v2/banner/25019354', 0.39),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                             0.133) 
                            ]

        self.empty_dir = "./" + uuid.uuid4().hex
        if not os.path.exists(self.empty_dir):
            os.makedirs(self.empty_dir)

    def test_get_latest_logfile(self):
        latest_logfile = la.get_latest_logfiles(config["LOG_DIR"])
        self.assertEqual(config["LOG_DIR"] + "/nginx-access-ui.log-20170630.gz",
                         latest_logfile.path)
    
    def test_get_latest_logfile_empty_dir(self):
        with self.assertRaises(Exception) as context:
            la.get_latest_logfiles(self.empty_dir)

        self.assertTrue("There are not logfiles in {0}".format(self.empty_dir) in
                        str(context.exception))

    def test_parse_logfile(self):
        lines = la.read_log(config["LOG_DIR"] + "/nginx-access-ui.log-20170630.gz")

        # import pdb; pdb.set_trace()
        parsed_lines = la.parse_log(config, lines)
        line_list = list(parsed_lines)
        self.assertListEqual(self.sample_list, line_list)
    
    def tearDown(self):
        os.rmdir(self.empty_dir)


if __name__ == '__main__':
    unittest.main()

