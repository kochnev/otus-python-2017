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
        self.parsed_lines = [('/api/v2/banner/25019354', 0.39),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                             0.133),
                            ('/api/v2/banner/25019354', 0.39),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                             0.133),
                            ('/api/v2/banner/25019354', 0.39),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                             0.133)
                            ]

        self.report_data = [{'url': '/api/v2/banner/25019354', 'count':
                                    3, 'count_perc': 50.0, 'time_avg': 0.39,
                                    'time_max': 0.39, 'time_med': 0.39,
                                    'time_perc': 0.195, 'time_sum': 1.17},
                                   {'url':
                                    '/api/1/photogenic_banners/list/?server_name=WIN7RB4',
                                    'count': 3, 'count_perc': 50.0, 'time_avg':
                                    0.133, 'time_max': 0.133, 'time_med':
                                    0.133, 'time_perc': 0.067, 'time_sum':
                                    0.399}]

        self.empty_dir = "./" + uuid.uuid4().hex
        if not os.path.exists(self.empty_dir):
            os.makedirs(self.empty_dir)

    def test_get_latest_logfile(self):
        latest_logfile = la.get_latest_logfiles(config["LOG_DIR"])
        self.assertEqual(config["LOG_DIR"] + "/nginx-access-ui.log-20170630.gz",
                         latest_logfile.path)
    
    def test_get_latest_logfile_empty_dir(self):
        latest_logfile = la.get_latest_logfiles(self.empty_dir)
        self.assertEqual(latest_logfile, None)       
 
    def test_parse_logfile(self):
        lines = la.read_log(config["LOG_DIR"] + "/nginx-access-ui.log-20170630.gz")
        parsed_lines = la.parse_log(config, lines)
        list_parsed_lines = list(parsed_lines)
        self.assertListEqual(self.parsed_lines, list_parsed_lines)
    
    def test_parse_logfile_exceed_error_threshold(self):
        lines = la.read_log(config["LOG_DIR"] + "/nginx-access-ui.log-20170629.gz")
        with self.assertRaises(RuntimeError):
             parsed_lines = la.parse_log(config, lines)
             list(parsed_lines)

    def test_get_report_data(self):
        report_data = la.get_report_data(config, self.parsed_lines)
        self.assertListEqual(report_data, self.report_data)

    def tearDown(self):
        os.rmdir(self.empty_dir)


if __name__ == '__main__':
    unittest.main()

