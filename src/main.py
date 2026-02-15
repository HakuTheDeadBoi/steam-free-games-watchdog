from datetime import date
from html.parser import HTMLParser
import os
import re
from smtplib import SMTP_SSL
from typing import TypedDict
from urllib.request import Request, urlopen

HREF_RE = re.compile(
    r'^https:\/\/store\.steampowered\.com\/app\/[0-9]+\/[A-Za-z_]+\/\?snr=[0-9_]+\/?$'
)

class GameDict(TypedDict):
    link: str
    name: str

class SMTPConfigDict(TypedDict):
    email: str
    host: str    
    password: str
    port: str
    recipients: list[str]

class SteamFreeGamesFinder(HTMLParser):
    START_COMMENT = 'List Items'
    END_COMMENT = 'End List Items'

    def __init__(self):
        self.items_list_start_found: bool = False
        self.collected_data: list[dict[str, str]] = []
        self.cls = self.__class__
        super().__init__()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not self.items_list_start_found:
            return
        
        href = None
        for attr in attrs:
            if attr[0] == 'href':
                href = attr[1]
                break

        if href:
            if not re.match(HREF_RE, href):
                raise Exception('HREF pattern not matching, cannot reliably parse link and name.')

            query_string_idx = href.index('/?')
            last_slash_idx = href.rfind('/', None, query_string_idx) + 1
            name = href[last_slash_idx:query_string_idx].replace('_', ' ')

            self.collected_data.append({
                'name':name,
                'link':href
            })
        
    def handle_comment(self, data: str) -> None:
        if self.cls.END_COMMENT in data:
            self.items_list_start_found = False
        elif self.cls.START_COMMENT in data:
            self.items_list_start_found = True

def main() -> None:
    recipients = os.environ.get('RECIPIENTS')
    smtp_config = {
        'host': os.environ.get('HOST'),
        'port': os.environ.get('PORT'),
        'email': os.environ.get('EMAIL'),
        'password': os.environ.get('PASSWORD'),
        'recipients': recipients.split(',') if recipients else '',
    }

    if not all(smtp_config.values()):
        raise Exception(f'SMTP connection can\'t be established since configuration is incomplete! {list(smtp_config.items())}')

    URL = 'https://store.steampowered.com/search?maxprice=free&supportedlang=english&specials=1&hidef2p=1'
    html = get_html(URL)
    data = parse_html(html)
    response = render_response(data)
    status = send_mail(response, smtp_config)
    return status

def get_html(url: str) -> str:
    req = Request(url=url)
    resp = urlopen(req)
    if resp.code != 200:
        raise Exception(f"HTTP request was unsuccessful, code: {resp.code}")
    
    return resp.read().decode('utf-8')

def parse_html(html: str) -> list[GameDict]:
    sfgi = SteamFreeGamesFinder()
    sfgi.feed(html)
    return sfgi.collected_data

def render_response(data: list[GameDict]) -> str:
    header = f"Ahoj, dne {date.today()} jsem navštívil Steam a našel tyto hry se 100% slevou!\n"
    games_list = ''
    message = ''
    for game in data:
        name = f'Jméno: {game['name']}\n'
        link = f'Link: {game['link']}\n'
        eoln = '****\n'
        games_list += name + link + eoln
    
    message = games_list or 'Žádné hry se 100% slevou nebyly nalezeny. :-('
    return f'{header}{message}'

def send_mail(msg: str, config: SMTPConfigDict) -> dict[str, tuple[int, str]]:
    with SMTP_SSL(config['host'], config['port']) as server:
        server.login(
            user = config['email'],
            password = config['password'],
        )
        return server.send_message(
            msg = msg,
            from_addr = config['email'],
            to_addrs=config['recipients'],
        )
