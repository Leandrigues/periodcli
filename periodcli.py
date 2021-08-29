import click
import requests
from bs4 import BeautifulSoup
import time, threading

class Periodicli:
    def __init__(self, url, period):
        self.url = url
        self.period = period
        self.initial_state = self.get_page_text()

        self.periodic_check()


    def get_page_text(self):
        response = requests.get(self.url)
        parsed_page = BeautifulSoup(response.content, 'html.parser')

        return parsed_page.text

    def periodic_check(self):
        threading.Timer(self.period, self.periodic_check).start()
        current_state = self.get_page_text()

        if current_state != self.initial_state:
            print(f'The page of {self.url} changed at {time.ctime()}')
            # self.write_logs()

@click.command()
@click.option('-p', default=10, help='period in seconds to check for changes.')
@click.argument('url')
def cli(p, url):
    Periodicli(url, p)

if __name__ == '__main__':
    cli()