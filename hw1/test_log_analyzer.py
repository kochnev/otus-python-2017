import unittest
# from .context import log_analyzer
from collections import defaultdict
import os
import shutil
import gzip
from datetime import datetime

import log_analyzer


class TestGetLogfiles(unittest.TestCase):

    def setUp(self):
        # set up for test_get_logfile
        self.dir = os.path.abspath('./test_log_folder')

        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        self.test_lines = [
            '1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390',
            '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133'
        ]
        for x in range(1, 5):
            str_d = "2018010{0}".format(x)
            file_name = "nginx-access-ui.log-{0}.gz".format(str_d)
            try:
                with gzip.open(os.path.join(self.dir, file_name), 'wb') as fd:
                    for line in self.test_lines:
                        fd.write((line + '\n').encode('utf-8'))
            except FileExistsError:
                pass

        # set up for test_parse_logfile
        self.latest_logfile_name = os.path.join(self.dir, "nginx-access-ui.log-20180104.gz")
        self.sample_list = [('/api/v2/banner/25019354', '0.390'),
                            ('/api/1/photogenic_banners/list/?server_name=WIN7RB4', '0.133')]

    def test_get_logfile(self):
        logfiles = log_analyzer.get_logfiles("nginx-access-ui.log-*.gz", self.dir)
        latest_logfile = max(logfiles, key=lambda item: item[1])
        latest_logfile_name = os.path.basename(latest_logfile[1])
        self.latest_logfile = latest_logfile

        self.assertEqual("nginx-access-ui.log-20180104.gz", latest_logfile_name)

    def test_parse_logfile(self):
        lines = log_analyzer.read_log(self.latest_logfile_name)
        parsed_lines = log_analyzer.parse_log(lines)
        line_list = list(parsed_lines)

        self.assertListEqual(self.sample_list, line_list)

    def tearDown(self):
        shutil.rmtree(self.dir)


if __name__ == '__main__':
    unittest.main()
