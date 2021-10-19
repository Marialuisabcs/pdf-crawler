import sys
from pathlib import Path

import pdfcrawler.crawler
from pdfcrawler import *


class CLI:
    def __init__(self):
        self.folder = None
        self.options = {
            'help': self.help,
            'add-folder': self.add_folder,
            'add-url': self.add_url,
            'download-pdfs': self.download_pdfs,
            'get-folder': self.get_folder,
            'exit': lambda: sys.exit(1)
        }

    def request_option(self):
        option = input('>> ')
        while option not in self.options:
            print('Invalid option, try again.')
            option = input('>> Option: ')

        self.options[option]()

    def help(self):
        for option in self.options:
            print(option)

        self.request_option()

    def add_folder(self):
        folder_name = input('>> Folder name: ')
        while not folder_name:
            print('Folder name can not be empty')
            folder_name = input('>> Folder name: ')
        self.folder = folder_name
        (Path.cwd() / 'output' / folder_name).mkdir(exist_ok=True)
        print('Folder selected succesfully!')
        self.request_option()

    def add_url(self):
        url = input('>> Please, add your url from a google scholar search: ')
        while not url:
            print('Url can not be empty')
            url = input('>> Url: ')

        if not self.folder:
            self.add_folder()

        print('\nCrawling...\n')
        pdfcrawler.crawler.run(url, self.folder)
        print('\n\nFinished')

        self.request_option()

    def download_pdfs(self):
        while not self.folder:
            print('No folder selected! Select `add-folder` option')
            self.request_option()

        print('\nDownloading files...\n')
        pdfcrawler.crawler.download(Path.cwd() / 'output' / self.folder / 'pdf_links.txt', self.folder)
        print('\n\nFinished')

        self.request_option()

    def get_folder(self):
        print('current folder: ' + str(self.folder))

    def start(self):
        print('current folder: ' + str(self.folder))
        print('Type `help` for help')
        self.request_option()


if __name__ == '__main__':
    cli = CLI()
    cli.start()

