import sys
import os
import platform
import logging
from random import randrange, sample as random_sample
from locust import HttpLocust, TaskSet, task
from locust.main import parse_options

logger = logging.getLogger(__name__)

URL_LIST = []


def exit_with_failure_msg(msg):
    logger.critical(msg)
    exit(msg)


def increase_system_open_file_limits():
    if platform.system() == 'Windows':
        from win32 import win32file
        win32file._setmaxstdio(2048)
    else:
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_NOFILE, (2048, 131072))
        except Exception as e:
            raise


class UserBehavior(TaskSet):
    def __init__(self, *args, **kwargs):
        self.host = self.datacsv = None
        super(UserBehavior, self).__init__(*args, **kwargs)

    def _load_options(self):
        try:
            options = parse_options()
            self.host = options[1].host
        except Exception as e:
            logger.error(e)

    def _find_data_csv(self):
        csvs_found = []
        try:
            files_in_same_path = os.listdir()
            for _f in files_in_same_path:
                if _f.endswith('csv') or _f.endswith('tsv'):
                    csvs_found.append(_f)
                    self.datacsv = _f
        except Exception as e:
            logger.error(e)
            self.datacsv = None
        
        if len(csvs_found) > 1:
            self.datacsv = None

        return csvs_found

    def _build_urL_list(self):
        global URL_LIST
        if not self.datacsv: return
        with open(self.datacsv, 'r') as urls_file:
            urls_to_test = urls_file.readlines()
            for row in urls_to_test:
                URL_LIST.append(row.replace('\n', '').replace('\r', ''))

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        increase_system_open_file_limits()
        self._load_options()
        csvs_found = self._find_data_csv()
        self._build_urL_list()

        if not self.host:
            exit_with_failure_msg(
                "host must be passed after --host flag.\n+" +
                "Example: > locust --host https://example.com"
            )
        if not self.datacsv:
            if not len(csvs_found):
                exit_with_failure_msg(
                    "No CSV/TSV file found in same folder as locustfile.\n" +
                    "Example: > locust --host https://example.com"
                )
            else:
                exit_with_failure_msg(
                    "Two or more CSV data files found in same folder as locustfile\n" +
                    "{}".format(" | ".join(csvs_found))
                )

        num_sample_urls = 3
        logger.info('USING BASE HOSTNAME: {}'.format(self.host))
        logger.info('USING CSV FILE: {}'.format(self.datacsv))
        logger.info('TESTING {} VARIATIONS OF THE SAME URL'.format(len(URL_LIST)))
        logger.info('Sample of URLs:\n\n{}\n'.format(
            ((self.host + '{}\n') * num_sample_urls).format(*random_sample(URL_LIST, num_sample_urls))
        ))

    @task(1)
    def get_a_page(self):
        self.client.get(URL_LIST[randrange(0, len(URL_LIST))], name='{}'.format(self.host), timeout=60)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 1000
