import click
import requests
import time, threading
import datetime
import signal
import sys
from bs4 import BeautifulSoup
from difflib import Differ

class Periodicli:
    def __init__(self, url, period, verbose, log_mode):
        self.url = url
        self.period = period
        self.verbose = verbose
        self.current_state = self.get_page_text()
        self.init_date = self._build_timestamp()
        self.log_mode = log_mode
        self._log('INFO', f'Initial state: {self.current_state}')

        self.periodic_check()


    def get_page_text(self):
        response = requests.get(self.url)
        parsed_page = BeautifulSoup(response.content, 'html.parser')
        self._log('INFO', f'Response of get in {self.url}: {parsed_page.text}')
        # print(parsed_page.text)
        return parsed_page.text

    def periodic_check(self):
        threading.Timer(self.period, self.periodic_check).start()
        new_state = self.get_page_text()
        self._log('INFO', f'Current state: {new_state}')

        if new_state != self.current_state:
            print(f'The page of {self.url} changed at {time.ctime()}')
            if self.log_mode:
                self.write_logs(self.current_state, new_state)
            self.current_state = new_state

    def write_logs(self, text_a, text_b):
        filename = self._build_filename()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        with open(filename, "a") as f:
            f.write(f'[{date}] Diff at {self.url}:\n')
            f.write(self.get_diff(text_a, text_b))
        f.close()

    def get_diff(self, text_a, text_b):
        differ = Differ()
        text_a = text_a.split('\n')
        text_a = [s + '\n' for s in text_a]

        text_b = text_b.split('\n')
        text_b = [s + '\n' for s in text_b]

        diffs = []

        for line in differ.compare(text_a, text_b):
            if line.startswith("+") or line.startswith("-"):
                diffs.append(line)

        return ''.join(diffs)
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