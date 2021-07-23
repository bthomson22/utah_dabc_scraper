# Import necessary packages
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

pd.set_option("expand_frame_repr", True)
# Site URL

products_dict = {'Crater Lake':'910543','Vida':'089221','Larceny':'018856'}
appended_data = []
# headings = ('Store','Name','Address','City','Phone','Store Qty','Pin')

for key, value in products_dict.items():

    url= f'https://webapps2.abc.utah.gov/ProdApps/ProductLocatorCore/ProductDetail/Index?sku={value}'

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse HTML code for the entire site
    soup = BeautifulSoup(html_content, "lxml")
    # print(soup.prettify()) # print the parsed data of html

    # On site there are 3 tables with the class "wikitable"
    # The following line will generate a list of HTML content for each table
    gdp = soup.find_all("table", id = "storeTable")
    print("Number of tables on site: ",len(gdp))

    # Lets go ahead and scrape first table with HTML code gdp[0]
    table1 = gdp[0]
    # the head will form our column names
    body = table1.find_all("tr")
    # Head values (Column names) are the first items of the body list
    head = body[0] # 0th item is the header row
    body_rows = body[1:] # All other items becomes the rest of the rows

    # Lets now iterate through the head HTML code and make list of clean headings

    # Declare empty list to keep Columns names
    headings = ('Store','Name','Address','City','Phone','Store Qty','Pin')
    # for item in head.find_all("th"): # loop through all th elements
    #     # convert the th elements to text and strip "\n"
    #     item = (item.text).rstrip("\n")
    #     # append the clean column name to headings
    #     headings.append(item)
    # print(headings)

    # Next is now to loop though the rest of the rows

    #print(body_rows[0])
 # will be a list for list for all rows
    all_rows = []
    for row_num in range(len(body_rows)): # A row at a time
        row = [] # this will old entries for one row
        for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
            # row_item.text removes the tags from the entries
            # the following regex is to remove \xa0 and \n and comma from row_item.text
            # xa0 encodes the flag, \n is the newline and comma separates thousands in numbers
            aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
            #append aa to row - note one row entry is being appended
            row.append(aa)
        # append one row to all_rows
        all_rows.append(row)

    df_prod = pd.DataFrame(data=all_rows, columns=headings)
    df_prod['Product Name'] = key
    df_prod['Product_ID'] = value
    # print(df_prod)
    appended_data.append(df_prod)

# We can now use the data on all_rowsa and headings to make a table
# all_rows becomes our data and headings the column names
print('\n########## ALL STORES ##########\n')

df = pd.concat(appended_data, ignore_index = True)
# print(df)

df['Store Qty'] = df['Store Qty'].astype(int)

df = df[df['Store Qty'] > 0]

if len(df.index)>0:
    print("\nThere's some available!")
    print(df)
else:
    print("\nNone available :(")
