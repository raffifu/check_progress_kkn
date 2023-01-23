import random
import string

import requests
from bs4 import BeautifulSoup
import re


class Simaster:
    SIMASTER_URL = 'https://simaster.ugm.ac.id'
    LOGIN_URL = f'{SIMASTER_URL}/services/simaster/service_login'
    BASE_URL_KKN = f'{SIMASTER_URL}/kkn/kkn/'
    LOGBOOK_PROGRAM = f'{SIMASTER_URL}/kkn/kkn/logbook_program'
    LOGBOOK_PROGRAM_DATA = f'{SIMASTER_URL}/kkn/kkn/logbook_program_data'
    HEADERS = {
        'UGMFWSERVICE': '1',
        'User-Agent': 'recap_kkn/1.0.0',
    }

    def __init__(self, credential, session=None):
        self.a_id = self._generate_random_a_id()
        self.credential = credential
        self.logged_in = False
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
                

    def login(self):
        req = self.session.post(self.LOGIN_URL, data={
            **self.credential
        })

        return self.is_logged_in()

    def is_logged_in(self):
        req = self.session.get(self.BASE_URL_KKN)

        if req.status_code == 200 and self.session.cookies.get("simasterUGM_cookie"):
            return True
        
        return False
    
    def set_session(self, ugm_session):
        self.session.cookies.set("simaster-ugm_sess", ugm_session, domain="simaster.ugm.ac.id")
    
    def data_proker(self):
        if not self.is_logged_in():
            raise RuntimeError("Login error")

        data={
            "simasterUGM_token" : self.session.cookies.get("simasterUGM_cookie")
        }

        url = self._get_url()

        if url is None:
            raise RuntimeError("Cannot get url")

        req = self.session.post(url, data=data)

        proker = []
        for data in req.json()['data']:
            if data['status_id'] == '2':
                soup = BeautifulSoup(data['action'], 'html.parser')
                found_tag = soup.find('a', attrs={'title': 'RPP Program'})  
                
                if found_tag is not None:
                    proker.append({"title": data['program_mhs_judul'], "jenis": data['program_jenis_id'], "url": found_tag.attrs['href']})

        return proker

    def detail_proker(self, url, is_bantu = False):
        if not self.is_logged_in():
            raise RuntimeError("Login error")
        
        req = self.session.get(url)

        if req.status_code != 200:
            raise RuntimeError("Cannot access resource")
        
        soup = BeautifulSoup(req.text, 'html.parser')

        table = soup.find_all("table")[1] if is_bantu else soup.find("table", id="datatables2")

        list_kegiatan = []
        head = ""
        for row in table.tbody.find_all("tr"):
            columns = row.find_all("td")

            if(len(columns) == 5):
                head = columns[1].text.strip()
                list_kegiatan.append({"RPP": head, "kegiatan": [], "jenis": "bantu" if is_bantu else "pokok"})
            elif(len(columns) == 2):
                proker = list_kegiatan[-1]
                
                if proker["RPP"] == head and columns[1].find("span", attrs={"class": "pull-right"}) != None:
                    proker["kegiatan"].append({"judul": columns[1].contents[0].strip(), "durasi": self._parse_durasi(columns[1].span.text.strip())})

        return list_kegiatan

    def _get_url(self):
        if not self.is_logged_in():
            raise RuntimeError("Login error")

        req = self.session.get(self.LOGBOOK_PROGRAM)

        f = re.findall(f"{self.LOGBOOK_PROGRAM_DATA}/[A-Za-z0-9-_]*=/[A-Za-z0-9-_]*=", req.text)
       
        if len(f) != 0:
            return f[0]
        
        return None

    @staticmethod
    def _generate_random_a_id():
        return ''.join(random.choice(string.hexdigits) for _ in range(16)).lower()
    
    @staticmethod
    def _parse_durasi(durasi):
        return int(durasi[1::].split(" ")[0])