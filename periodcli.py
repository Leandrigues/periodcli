import click
import requests
import time, threading
import datetime
import signal
import sys
from bs4 import BeautifulSoup
from difflib import Differ

class Periodicli:
    def __init__(self, url, period, verbose, write_logs):
        self.url = url
        self.period = period
        self.verbose = verbose
        self.initial_state = self.get_page_text()
        self.init_date = self._build_timestamp()
        self.write_logs = write_logs
        self._log('INFO', f'Initial state: {self.initial_state}')

        self.periodic_check()

    def get_page_text(self):
        response = requests.get(self.url)
        parsed_page = BeautifulSoup(response.content, 'html.parser')
        self._log('INFO', f'Response of get in {self.url}: {parsed_page.text}')

        return parsed_page.text

    def periodic_check(self):
        threading.Timer(self.period, self.periodic_check).start()
        current_state = self.get_page_text()
        self._log('INFO', f'Current state: {current_state}')

        if current_state != self.initial_state:
            print(f'The page of {self.url} changed at {time.ctime()}')
            if self.write_logs:
                self.write_logs(self.initial_state, current_state)

    def write_logs(self, text_a, text_b):
        differ = Differ()
        filename = self._build_filename()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        with open(filename, "a") as f:
            f.write(f'[{date}] Diff at {self.url}:\n')
            for line in differ.compare(text_a, text_b):
                if line.startswith("+") or line.startswith("-"):
                    f.write(f'{line}\n')

        f.close()

    def _build_filename(self):
        return f"{self.url.split('//')[1].split('.')[0]}_{self.init_date}"

    def _build_timestamp(self):
        return str(time.time()).split('.')[-1]

    def _log(self, level, message):
        if self.verbose:
            print(f'[{level}] message')


@click.command()
@click.option('-p', default=2, help='period in seconds to check for changes.')
@click.option('-v', default=False, help='enables verbose mode.')
@click.option('-w', default=False, help='writes the page diffs to a file prefixed by the website\'s name (eg. google_12345678')
@click.argument('url')
def cli(p, v, w, url):
    Periodicli(url, p, v, w)

if __name__ == '__main__':
    cli()