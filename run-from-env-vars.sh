#!/bin/bash

echo "$secrets" > passwords.txt
echo "$mail_list" > mail_list.txt

python3 scraper.py