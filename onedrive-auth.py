#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import os
import subprocess
import sys
import time
from pathlib import Path

from selenium import webdriver

URL_FILE = "/tmp/onedrive-url"
RESP_FILE = "/tmp/onedrive-resp"


def clean_up():
    try:
        os.remove(URL_FILE)
    except FileNotFoundError:
        pass
    try:
        os.remove(RESP_FILE)
    except FileNotFoundError:
        pass


def main():
    options = webdriver.ChromeOptions()
    options.add_argument(
        f"--user-data-dir={Path(__file__).parent.absolute()}/.chrome-profile")
    browser = webdriver.Chrome(options=options)

    clean_up()

    onedrive = subprocess.Popen(
        f"onedrive --reauth --auth-files {URL_FILE}:{RESP_FILE}",
        shell=True
    )

    while not os.path.exists(URL_FILE):
        time.sleep(0.1)

    with open(URL_FILE) as f:
        url = f.read()

    if not url:
        print("Did not receive an URL :(", file=sys.sterr)
        exit(1)

    browser.get(url)

    while not 'code=' in browser.current_url:
        time.sleep(1)

    with open(RESP_FILE, 'w') as f:
        f.write(browser.current_url)
        f.flush()

    onedrive.wait()

    os.system("systemctl --user restart onedrive")


if __name__ == "__main__":
    try:
        main()
    finally:
        clean_up()
