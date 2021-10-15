from pdfcrawler import *
import requests
from urllib.parse import *
from urllib.request import *
from bs4 import BeautifulSoup
import mimetypes
from pathlib import Path
import os

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
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
                only_pdf(href)
            continue
        print(f"{GRAY}[*] Internal link: {href}{RESET}")
        urls.add(href)
        internal_urls.add(href)
    return urls


def crawl(url, max_urls=30):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)


def only_pdf(link):
    if link.startswith("https:"):
        response = requests.get(link, headers=headers)
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type)
        if extension == ".pdf":
            with open("pdf_links.txt", 'a') as pdf:
                pdf.write(link + "\n")


def download(input_file):
    (Path.cwd() / 'pdfs').mkdir(exist_ok=True)
    print("Lendo links...")
    pdf_links = open(input_file, "r")
    pdfs = pdf_links.read().splitlines()
    pdf_links.close()
    print("Iniciando downloads...\n")
    cont = 1
    for link in pdfs:
        print('LINK = ' + link)
        print('CONT = ' + str(cont))
        req = Request(link, headers=headers)
        response = urlopen(req)
        file = open(os.path.join(Path.cwd() / 'pdfs', str(cont) + '.pdf'), 'wb')
        file.write(response.read())
        file.close()
        cont += 1


def url_opener(url_root):
    start_param = 10
    pags = [url_root]

    while start_param < 30:
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


def run(google_link):
    urls = url_opener(google_link)
    for url in urls:
        crawl(url)
    download('pdf_links.txt')
