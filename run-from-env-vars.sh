#!/bin/bash

echo "$products" > products.json
echo "$secrets" > passwords.txt
echo "$mail_list" > mail_list.txt

python3 gimme_the_booze.py