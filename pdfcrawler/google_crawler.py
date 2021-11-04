from pdfcrawler import *
from bs4 import BeautifulSoup as bs
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import *
from urllib.request import *
import os
import time
import random
import urllib
import requests


def is_valid(url: str):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def crawl(url: str, folder_name: str):
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")

    urls = set()
    soup = set()

    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc

    for i in range(0, 1000):

        try:
            session = get_session()
            print(f"Trying...{session.proxies}")
            soup = bs(session.get(url, headers=headers).content, "html.parser")
            time.sleep(random.randint(5, 9))
            if soup:
                break

        except Exception as e:
            continue

    for a_tag in soup.findAll("a"):

        href = a_tag.attrs.get("href")

        if href == "" or href is None:
            # href empty tag
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)

        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_valid(href):
            # not a valid URL
            continue

        if href in internal_urls:
            # already in the set
            continue

        if domain_name not in href:

            # external link
            if href not in external_urls:
                print(f"{GREEN}[!] External link: {href}{RESET}")
                external_urls.add(href)
                only_pdf(href, folder_name)
            continue

        print(f"{GRAY}[*] Internal link: {href}{RESET}")
        urls.add(href)
        internal_urls.add(href)


def only_pdf(link: str, folder_name: str):
    if link.startswith("https:"):
        path = urlparse(link).path

        if path.endswith(".pdf"):
            with open(os.path.join(Path.cwd() / 'output' / folder_name / 'azeem_links_test_02.txt'), 'a') as link_test:
                link_test.write(link + "\n")


def download(input_file: str, folder_name:str):
    (Path.cwd() / 'output' / folder_name / 'pdfs').mkdir(exist_ok=True)

    pdf_links = open(input_file, 'r')
    pdfs = pdf_links.read().splitlines()
    pdf_links.close()

    cont = 1

    for link in pdfs:
        print(f"{GREEN}[!] Downloading link {cont}: {link}{RESET}")

        try:
            urlretrieve(link, os.path.join(Path.cwd() / 'output' / folder_name / 'pdfs', str(cont) + '.pdf'))
            # time.sleep(random.randint(0, 9))
            cont += 1
        except urllib.error.HTTPError:
            print(f"{RED}[!!]Error 404: link {cont}")
            cont += 1
            pass


def url_opener(url_root: str):
    start_param = 630
    pags = [url_root]

    while start_param < 1000:
        params = {"start": str(start_param)}
        url_parse = urlparse(url_root)
        query = url_parse.query
        url_dict = dict(parse_qsl(query))
        url_dict.update(params)
        url_new_query = urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        new_url = urlunparse(url_parse)

        pags.append(new_url)

        start_param += 10

    return pags


def get_proxies():
    url = "https://free-proxy-list.net/"
    soup = bs(requests.get(url).content, "html.parser")
    proxies = []

    for row in soup.find("table").find_all("tr")[1:]:
        tds = row.find_all("td")

        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)

        except IndexError:
            continue

    return proxies


def get_session():
    session = requests.Session()
    proxy = random.choice(get_proxies())
    session.proxies = {"http": "http://" + proxy, "https": "http://" + proxy}

    return session


def run(google_link, folder_name):
    urls = url_opener(google_link)
    for url in urls:
        time.sleep(random.randint(5, 10))
        crawl(url, folder_name)
