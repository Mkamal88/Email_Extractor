import re
from collections import deque
from typing import Any, Union
from urllib.parse import urlsplit
import requests.exceptions
import urllib3
from bs4 import BeautifulSoup
from validate_email import validate_email
from pyisemail import is_email

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

keyWords = ('contact', 'about', 'touch', 'reservation')
Filter = ('facebook', 'twitter', 'whatsapp', 'login', '#comment', 'mailto:', 'tel:', 'javascript', 'sitemap', 'locations', 'linkedin', 'youtube', 'flickr', 'instagram')


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    return list(seen_twice)


def validate(email):
    detailed_result_with_dns = is_email(email, check_dns=True, diagnose=True)
    return detailed_result_with_dns.diagnosis_type


def hunting(starting_url):
    extracted_emails = ""
    content = ""
    found = 0
    not_found = 0
    if starting_url.startswith('http'):
        domain = re.match(r'(?:^https?://([^/]+)(?:[/,]|$)|^(.*)$)', starting_url)
        domain = domain.group(1).replace('www.', '').replace('Www.', '')
        name = re.match(r'[^.]*', domain).group()
        print("Starting with ", starting_url)

        unprocessed_urls = deque([starting_url])
        processed_urls = set()
        emails = set()

        while len(unprocessed_urls):
            try:
                # move next url from the queue to the set of processed urls
                url = unprocessed_urls.popleft()
                processed_urls.add(url)
                # extract base url to resolve relative links
                parts = urlsplit(url)
                base_url = "{0.scheme}://{0.netloc}".format(parts)
                path = url[:url.rfind('/') + 1] if '/' in parts.path else url
                # get url's content
                if url.find(domain) != -1:
                    print("Crawling URL %s" % url)
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        response = requests.get(url, headers=headers, verify=False)
                    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                        continue

                    # extract all email addresses and add them into the resulting set
                    new_emails = re.findall(r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+", response.text, re.I)
                    valid_list = []
                    for mail in new_emails:
                        # is_valid = validate_email(mail, verify=True, check_mx=True)
                        is_valid = validate(mail)
                        if is_valid == 'VALID':
                            valid_list.append(mail)
                    new_emails = valid_list
                    _content = "".join(new_emails)
                    emails.update(new_emails)
                    # create a beautiful soup for the html document
                    soup = BeautifulSoup(response.text, 'lxml')
                    if len(new_emails) < 1 or _content.find(name) == -1 or _content.find("wixpress") != -1:
                        # Find all links in one page
                        links_count = len(soup.find_all("a"))
                        for href in soup.find_all("a"):
                            # extract link url from the anchor
                            link = href.attrs["href"] if "href" in href.attrs else ''
                            title: Union[str, Any] = href.attrs["title"] if "title" in href.attrs else ''
                            if not any(f in link.lower() for f in Filter):
                                if link.startswith('/') or link.startswith('#') or link.startswith(
                                        './') or link.startswith('../'):
                                    link = base_url + link
                                    link = link.replace('../', '/')
                                    link = link.replace('./', '/')
                                elif link.find('/') == -1 and link.find('#') == -1 and len(link) > 1:
                                    if path.endswith('/'):
                                        link = path + link
                                    else:
                                        link = path + '/' + link
                                elif not link.startswith('http'):
                                    link = path + link

                                words = link.split('/')
                                new_list = list_duplicates(words)
                                if not link in unprocessed_urls and not link in processed_urls and len(
                                        "".join(new_list)) == 0:
                                    if any(w in link.lower() for w in keyWords) or any(
                                            w in title.lower() for w in keyWords) or links_count <= 3:
                                        unprocessed_urls.append(link)
            except (
                    requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
                    requests.exceptions.TooManyRedirects):
                continue
            if len(emails):
                extracted_emails = ", ".join(list(dict.fromkeys(emails)))
            else:
                extracted_emails = ""
    if len(extracted_emails) < 1:
        extracted_emails = "Null"
        not_found += 1
    else:
        found += 1
    content += starting_url + ',' + '"' + extracted_emails + '"' + "\n"
    return content
    # print(content)

# hunting(starting_url)