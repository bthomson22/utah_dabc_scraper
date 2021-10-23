# Utah DABC Scarper

Author: Brandon Thomson

This is a web scraper designed to fetch data from the Utah DABC website for a specified list of products. Once run, an email will be sent to users on a mailing list with the availabilty & store location of each product.

### Quick Start

1. Create a gmail account to send the report from. Credentials for the account should be held within the `passwords.txt` file in the below format:
```
username:{email_address}
password:{password}
```

2. Populate a list of products you want to scrape in the `products.json` file. This should follow typical JSON formatting:
```
{
    "Product 1 Name": "Product 1 Sku",
    "Product 2 Name": "Product 2 Sku"
}
```

3. Create a mailing list to send the report to and save this in `mail_list.txt`. This should follow the below formatting:
```
email_1@email.com,email_2@email.com,email_3@email.com
```

4. Run the script using `python3 scraper.py`