from bs4 import BeautifulSoup
import pandas as pd
import requests
import smtplib
import logging
import re
from pretty_html_table import build_table
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


subject = 'Booze available!'

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
        
def setup_logging():
    logging.basicConfig(filename='scrape.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def main():
    credentials = get_credentials()
    mail_list = get_mail_list()
    products_dict = {'Crater Lake':'910543','Vida':'089221','Larceny':'018856'}
    appended_data = []  
    setup_logging()
    
    try:
        for key, value in products_dict.items():

            url= f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/ProductDetail/Index?sku={value}'
            html_content = requests.get(url).text
            soup = BeautifulSoup(html_content, "lxml")
            gdp = soup.find_all("table", id = "storeTable")
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
            # print(df_prod)
            appended_data.append(df_prod)

        # print('\n########## ALL STORES ##########\n')

        df = pd.concat(appended_data, ignore_index = True)
        # print(df)

        df['Store Qty'] = df['Store Qty'].astype(int)
        df = df[df['Store Qty'] > 0]
        print(df)

        if len(df.index)>0:
            try:
                gmail_user = credentials['username']
                gmail_password = credentials['password']
                sent_from = gmail_user
                to = mail_list
                # subject = 'Booze available!'
                # msg_body = build_table(df,'blue_light')
                # message = """From: %s
                # To: %s
                # Subject: %s
                # %s
                # """ % (sent_from, to, subject, msg_body)

                # server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                # server.ehlo()
                # server.login(gmail_user, gmail_password)
                # server.sendmail(sent_from, to, message)
                # server.close()

                message = MIMEMultipart()
                message['Subject'] = 'Booze Available!'
                message['From'] = 'utah.dabc.scraper@gmail.com'
                message['To'] = 'bthomson22@gmail.com'
                body_content = build_table(df, 'blue_light')
                message.attach(MIMEText(body_content, 'html'))
                msg_body = message.as_string()
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(message['From'], message['To'], msg_body)
                server.close()
                
                logging.info('Email sent!')
                print("\nThere's some available!")
                # print(df)

            # except SMTPResponseException as e:
            #     error_code = e.smtp_code
            #     error_message = e.smtp_error

            except Exception:
                logging.info('Something went wrong...')

        else:
            logging.info('None available :(')
            print("\nNone available :(")

    except Exception:
        logging.info('Failed to scrape')

def check_logger():
    try:
        infile = r"scrape.log"
        important = []
        keep_phrases = ["Email sent!"]
        with open(infile) as f:
            f = f.readlines()
        for line in f:
            for phrase in keep_phrases:
                if phrase in line:
                    important.append(line)
                    break
        if len(important) > 0:
            return "Stop"
        else:
            return "Go"
    except Exception:
        return "Go"

if __name__ == '__main__':
    main()