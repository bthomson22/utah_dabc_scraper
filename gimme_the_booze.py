from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
from pretty_html_table import build_table
import json
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
from smtplib import SMTPException
import sys
from datetime import datetime

now = datetime.now() # current date and time
todays_date = now.strftime("%m/%d/%Y")

subject = f'Daily Booze Report {todays_date}'

def get_credentials():
    credentials = {}
    with open('passwords.txt') as f:
        for x in f.readlines():
            entry = x.strip().split(':')
            credentials[entry[0]] = entry[1]
    return credentials

def get_mail_list():
    with open('mail_list.txt') as f:
        mail_list = [x.strip().split(', ') for x in f.readlines()][0]
    return mail_list

def get_products_dict():
    with open('products.json') as f:
        products = json.load(f)
    return products

def main():
    credentials = get_credentials()
    mail_list = get_mail_list()
    products = get_products_dict()
    appended_data = []  
    
    print('\n########## SCRAPING WEBSITE FOR THE BELOW PRODUCTS ##########\n')
    print(products)

    try:
        for key, value in products.items():
            print(f'\n########## RETRIEVING {key} ##########\n')
        
            url= f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/ProductDetail/Index?sku={value}'
            html_content = requests.get(url).text
            soup = BeautifulSoup(html_content, 'html.parser')
            gdp = soup.find_all('table', id = 'storeTable')
            table1 = gdp[0]
            body = table1.find_all("tr")
            head = body[0]
            body_rows = body[1:]

            headings = ('Store','Name','Address','City','Phone','Store Qty','Pin')
        
            all_rows = []
            for row_num in range(len(body_rows)):
                row = []
                for row_item in body_rows[row_num].find_all("td"):
                    aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
                    row.append(aa)
                all_rows.append(row)

            df_prod = pd.DataFrame(data=all_rows, columns=headings)
            df_prod['Product Name'] = key
            df_prod['Product_ID'] = value
            df_prod['URL'] = url
            print(df_prod)

            appended_data.append(df_prod)
            print(f'\n########## SUCESSFULLY RETRIEVED {key} ##########\n')
        
        print('\n########## SCRAPING FINISHED ##########\n')

        print('\n########## CREATING DATAFRAME ##########\n')

        df = pd.concat(appended_data, ignore_index = True)
        df['Store Qty'] = df['Store Qty'].astype(int)
        df = df[df['Store Qty'] > 0]
        df.reset_index(drop=True,inplace=True)

        print('\n########## RESULTS ##########\n')
        print(df)

        if len(df.index) > 0:
            try:
                gmail_user = credentials['username']
                gmail_password = credentials['password']
                sent_from = gmail_user

                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = sent_from
                msg['Bcc'] = ", ".join(mail_list)


                html = """\
                <html>
                <head></head>
                <body>
                    {0}
                </body>
                </html>
                """.format(build_table(df,'blue_light'))

                part1 = MIMEText(html, 'html')
                msg.attach(part1)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.login(gmail_user, gmail_password)
                server.sendmail(sent_from, mail_list , msg.as_string())
                server.quit()
                print('Mail Sent')

            except SMTPException as e:
                print('Error sending email')
                error_code = e.smtp_code
                error_message = e.smtp_error

        else:
            print("\nNone available :(")

    except Exception:
        print('Failed to scrape')


if __name__ == '__main__':
    main()