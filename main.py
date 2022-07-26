import csv
import json
import os
import time
import traceback

import requests
from bs4 import BeautifulSoup

encoding = "utf-8"


def biohort():
    if not os.path.isfile("biohort.json"):
        print("Fetching response from BioHort")
        params = (
            ('sorting', 'state'),
            ('state', ''),
            ('radius', '250'),
            ('latitude', '51.165691'),
            ('longitude', '10.451526'),
            ('country', 'DE'),
            ('initsearch', '1'),
        )
        res = requests.get('https://hvtool.biohort.com/rest/dealersearch', params=params)
        with open("biohort.json", "w") as f:
            json.dump(res.json(), f, indent=4)
        return res.json()
    else:
        print("Loading cached response from BioHort")
        with open("biohort.json", "r") as f:
            return json.load(f)


def gelbeseiten(bh):
    url = f"https://www.gelbeseiten.de/suche/{bh['name']}/bundesweit"
    soup = BeautifulSoup(requests.get(url).content, 'lxml')
    class_dict = {
        "website": "contains-icon-homepage gc-btn gc-btn--s",
        "email": "contains-icon-email gc-btn gc-btn--s"
    }
    for key, value in class_dict.items():
        if soup.find("a", class_=value):
            bh[key] = soup.find("a", class_=value).get("href")
        else:
            bh[key] = ""
    return bh


def main():
    logo()
    scraped = []
    if not os.path.isfile("biohort.csv"):
        with open("biohort.csv", "w", encoding=encoding, newline='') as f:
            csv.DictWriter(f, fieldnames=["name", "phone", "website", "email"]).writeheader()
    else:
        with open("biohort.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                scraped.append(row['name'])
    with open("biohort.csv", "a", encoding=encoding, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["name", "phone", "website", "email"])
        for data in biohort()['data']:
            try:
                bh = {}
                for header in ['name', 'phone']:
                    bh[header] = data.get(header, "")
                if bh['name'] not in scraped:
                    bh = gelbeseiten(bh)
                    writer.writerow(bh)
                    f.flush()
                    scraped.append(bh['name'])
                    print(json.dumps(bh, indent=4))
                else:
                    print(f"Already scraped '{bh['name']}'")
            except:
                traceback.print_exc()
                print(f"Error while processing row {data}")
                time.sleep(1)


def logo():
    os.system('color 0a')
    print(r"""
  _     _       _               _    __  __             _  _                   _  _              
 | |__ (_) ___ | |_   ___  _ _ | |_  \ \/ /  __ _  ___ | || |__  ___  ___ ___ (_)| |_  ___  _ _  
 | '_ \| |/ _ \| ' \ / _ \| '_||  _|  >  <  / _` |/ -_)| || '_ \/ -_)(_-</ -_)| ||  _|/ -_)| ' \ 
 |_.__/|_|\___/|_||_|\___/|_|   \__| /_/\_\ \__, |\___||_||_.__/\___|/__/\___||_| \__|\___||_||_|
                                            |___/                                              
====================================================================================================
                biohort x gelbeseiten scraper by https://github.com/evilgenius786
====================================================================================================
[+] Resumable
[+] Fast
[+] Efficient
[+] Remove duplicates
[+] CSV/JSON output
[+] Without browser
____________________________________________________________________________________________________
""")


if __name__ == '__main__':
    main()
