from bs4 import BeautifulSoup
import urllib.request
import bs4
import re
import socket
import whois
from datetime import datetime
import time
import pytz
from googlesearch import search

import sys
import requests
from patterns import *

import os

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_and_save_html(url):
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()

        html = response.text

        return html
    except requests.exceptions.RequestException:
        return None

def having_ip_address(url):
    ip_address_pattern = ipv4_pattern + "|" + ipv6_pattern
    match = re.search(ip_address_pattern, url)
    return -1 if match else 1


def url_length(url):
    if len(url) < 54:
        return 1
    if 54 <= len(url) <= 75:
        return 0
    return -1


def shortening_service(url):
    match = re.search(shortening_services, url)
    return -1 if match else 1


def having_at_symbol(url):
    match = re.search('@', url)
    return -1 if match else 1


def double_slash_redirecting(url):
    last_double_slash = url.rfind('//')
    return -1 if last_double_slash > 6 else 1


def prefix_suffix(domain):
    match = re.search('-', domain)
    return -1 if match else 1


def having_sub_domain(url):
    if having_ip_address(url) == -1:
        match = re.search(
            '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
            '([01]?\\d\\d?|2[0-4]\\d|25[0-5]))|(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}',
            url)
        pos = match.end()
        url = url[pos:]
    num_dots = [x.start() for x in re.finditer(r'\.', url)]
    if len(num_dots) <= 3:
        return 1
    elif len(num_dots) == 4:
        return 0
    else:
        return -1


def domain_registration_length(domain):
    expiration_date = domain.expiration_date
    today = datetime.now(pytz.UTC)
    registration_length = 0
    
    if expiration_date:
        if isinstance(expiration_date, list):
            registration_length = abs((expiration_date[0] - today).days)
        else:
            registration_length = abs((expiration_date - today).days)
    return -1 if registration_length / 365 <= 1 else 1


def favicon(url, soup, domain):
    for head in soup.find_all('head'):
        for head.link in soup.find_all('link', href=True):
            dots = [x.start() for x in re.finditer(r'\.', head.link['href'])]
            return 1 if url in head.link['href'] or len(dots) == 1 or domain in head.link['href'] else -1
    return 1


def https_token(url):
    match = re.search(http_https, url)
    if match and match.start() == 0:
        url = url[match.end():]
    match = re.search('http|https', url)
    return -1 if match else 1


def request_url(url, soup, domain):
    i = 0
    success = 0
    for img in soup.find_all('img', src=True):
        dots = [x.start() for x in re.finditer(r'\.', img['src'])]
        if url in img['src'] or domain in img['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for audio in soup.find_all('audio', src=True):
        dots = [x.start() for x in re.finditer(r'\.', audio['src'])]
        if url in audio['src'] or domain in audio['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for embed in soup.find_all('embed', src=True):
        dots = [x.start() for x in re.finditer(r'\.', embed['src'])]
        if url in embed['src'] or domain in embed['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    for iframe in soup.find_all('iframe', src=True):
        dots = [x.start() for x in re.finditer(r'\.', iframe['src'])]
        if url in iframe['src'] or domain in iframe['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    try:
        percentage = 100 - (success / float(i) * 100)
    except:
        return 1

    if percentage < 22.0:
        return 1
    elif 22.0 <= percentage < 61.0:
        return 0
    else:
        return -1


def url_of_anchor(url, soup, domain):
    i = 0
    unsafe = 0
    for a in soup.find_all('a', href=True):
        # javascript per 'JavaScript ::void(0)'
        if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in a['href'].lower() or not (
                url in a['href'] or domain in a['href']):
            unsafe = unsafe + 1
        i = i + 1
    
    try:
        percentage = unsafe / float(i) * 100
    except:
        return 1
    if percentage < 31.0:
        return 1
    elif 31.0 <= percentage < 67.0:
        return 0
    else:
        return -1


def links_in_tags(url, soup, domain):
    i = 0
    success = 0
    for link in soup.find_all('link', href=True):
        dots = [x.start() for x in re.finditer(r'\.', link['href'])]
        if url in link['href'] or domain in link['href'] or len(dots) == 1:
            success = success + 1
        i = i + 1
        
    for script in soup.find_all('script', src=True):
        dots = [x.start() for x in re.finditer(r'\.', script['src'])]
        if url in script['src'] or domain in script['src'] or len(dots) == 1:
            success = success + 1
        i = i + 1

    try:
        percentage = 100 - (success / float(i) * 100)
    except:
        return 1

    if percentage < 17.0:
        return 1
    elif 17.0 <= percentage < 81.0:
        return 0
    else:
        return -1


def sfh(url, soup, domain):
    for form in soup.find_all('form', action=True):
        if form['action'] == "" or form['action'] == "about:blank":
            return -1
        elif url not in form['action'] and domain not in form['action']:
            return 0
        else:
            return 1
    return 1


def submitting_to_email(soup):
    for form in soup.find_all('form', action=True):
        return -1 if "mailto:" in form['action'] else 1
    return 1


def abnormal_url(domain, url):
    if isinstance(domain.domain_name, list):
        hostname = domain.domain_name[0]
    else:
        hostname = domain.domain_name
    if hostname is None:
        return -1
    match = re.search(hostname.lower(), url)
    return -1 if match is None else 1


def iframe(soup):
    for iframes in soup.find_all('iframe', width=True, height=True, frameBorder=True):
        if iframes['width'] == "0" and iframes['height'] == "0" and iframes['frameBorder'] == "0":
            return -1
        if iframes['width'] == "0" or iframes['height'] == "0" or iframes['frameBorder'] == "0":
            return 0
    return 1


def age_of_domain(domain):
    if isinstance(domain.creation_date,list):
        creation_date = domain.creation_date[0]
    else:
        creation_date = domain.creation_date
    if isinstance(domain.expiration_date,list):
        expiration_date = domain.expiration_date[0]
    else:
        expiration_date = domain.expiration_date
    ageofdomain = 0
    if expiration_date:
        ageofdomain = abs((expiration_date - creation_date).days)
    return -1 if ageofdomain / 30 < 6 else 1

def google_index(url):
    site = search(url, 5)
    return 1 if site else -1


def statistical_report(url, hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        return -1
    url_match = re.search(
        r'at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweddy\.com|myjino\.ru|96\.lt|ow\.ly', url)
    ip_match = re.search(
        r'146\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|'
        r'107\.151\.148\.44|107\.151\.148\.107|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|52\.69\.166\.231|216\.58\.192\.225|'
        r'118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
        r'216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|'
        r'34\.196\.13\.28|103\.224\.212\.222|172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|'
        r'216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',
        ip_address)
    if url_match:
        return -1
    elif ip_match:
        return -1
    else:
        return 1


def get_hostname_from_url(url):
    hostname = url
    pattern = "https://www.|http://www.|https://|http://|www."
    pre_pattern_match = re.search(pattern, hostname)

    if pre_pattern_match:
        hostname = hostname[pre_pattern_match.end():]
        post_pattern_match = re.search("/", hostname)
        if post_pattern_match:
            hostname = hostname[:post_pattern_match.start()]
    return hostname


def get_domain_from_hostname(hostname):
    try:
        domain = whois.whois(hostname)
        if(domain.domain_name == None): domain = -1
    except:
        domain = -1
    return domain

def main(url):
    status = []
    html = fetch_and_save_html(url)
    if not html:
        return status

    soup = BeautifulSoup(html, 'html.parser')

    hostname = get_hostname_from_url(url)
    domain = get_domain_from_hostname(hostname)

    status.append(having_ip_address(url))
    status.append(url_length(url))
    status.append(shortening_service(url))
    status.append(having_at_symbol(url))
    status.append(double_slash_redirecting(url))
    status.append(prefix_suffix(hostname))
    status.append(having_sub_domain(url))
    status.append(-1 if domain == -1 else domain_registration_length(domain))
    status.append(favicon(url, soup, hostname))
    status.append(https_token(url))
    status.append(request_url(url, soup, hostname))
    status.append(url_of_anchor(url, soup, hostname))
    status.append(links_in_tags(url, soup, hostname))
    status.append(sfh(url, soup, hostname))
    status.append(submitting_to_email(soup))
    status.append(-1 if domain == -1 else abnormal_url(domain, url))
    status.append(iframe(soup))
    status.append(-1 if domain == -1 else age_of_domain(domain))
    status.append(-1 if domain == -1 else 1)
    status.append(google_index(url))
    status.append(statistical_report(url, hostname))

    return status
