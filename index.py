"""
Module for scraping car data from Riyasewana and storing it in Google Sheets.
"""

import os
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ACCEPT_HEADER_VALUE = ('text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                       'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7')
USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')
headers = {
    'accept': ACCEPT_HEADER_VALUE,
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': USER_AGENT
}

def extract_riyasewana_advertisement(url):
    """Extract car details from a Riyasewana advertisement page.

    This function takes a URL of a Riyasewana advertisement page and returns a dictionary of car details.
    """
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        car_details = {
            'make': soup.find('td', text='Make').find_next_sibling('td').text.strip(),
            'model': soup.find('td', text='Model').find_next_sibling('td').text.strip(),
            'year_of_manufacture': soup.find('td', text='YOM').find_next_sibling('td').text.strip(),
            'mileage_km': soup.find('td', text='Mileage (km)').find_next_sibling('td').text.strip(),
            'gear': soup.find('td', text='Gear').find_next_sibling('td').text.strip(),
            'fuel_type': soup.find('td', text='Fuel Type').find_next_sibling('td').text.strip(),
            'options': soup.find('td', text='Options').find_next_sibling('td').text.strip(),
            'engine_cc': soup.find('td', text='Engine (cc)').find_next_sibling('td').text.strip(),
            'details': soup.find('td', text='Details').find_next_sibling('td').text.strip(),
            'contact': soup.find('td', text='Contact').find_next_sibling('td').text.strip()
        }
        return car_details
    return None

def scrape_riyasewana_list(url):
    """Scrape the Riyasewana listing page and return a list of car dictionaries.
    
    This function takes a URL of a Riyasewana listing page and returns a list of car dictionaries.
    """
    cars = []
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('li.item.round'):
            car = {
                'title': item.find('h2', class_='more').find('a').get('title').strip(),
                'url': item.find('h2', class_='more').find('a').get('href').strip(),
                'image': (item.find('div', class_='imgbox')
                         .find('img').get('src').strip()),
                'location': (item.find('div', class_='boxtext')
                           .find_all('div', class_='boxintxt')[0].text.strip()),
                'price': (item.find('div', class_='boxtext')
                         .find_all('div', class_='boxintxt')[1].text.strip()),
                'mileage': (item.find('div', class_='boxtext')
                           .find_all('div', class_='boxintxt')[2].text.strip()),
            }
            ad_details = extract_riyasewana_advertisement(car['url'])
            if ad_details is not None:
                car.update(ad_details)
            cars.append(car)
    return cars

def store_cars_in_google_sheet(cars, google_sheet_name, sheet_name):
    """Store car data in a Google Sheet.

    This function takes a list of car dictionaries and stores them in a specified Google Sheet,
    avoiding duplicate entries based on the car's URL.
    """
    google_credentionals_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_PATH')
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentionals_path, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open(google_sheet_name).worksheet(sheet_name)
    header = [
        "Title", "URL", "Image", "Location", "Price", "Mileage", "Make", "Model", 
        "Year of Manufacture", "Mileage (km)", "Gear", "Fuel Type", "Options", 
        "Engine (cc)", "Contact", "Details"
    ]
    if not sheet.row_values(1):
        sheet.append_row(header)
    existing_urls = sheet.col_values(2)
    newest_additions = []
    for car in cars:
        if car.get('url', '') not in existing_urls:
            row = [
                car.get('title', ''),
                car.get('url', ''),
                "https:" + car.get('image', ''),
                car.get('location', ''),
                ''.join(c for c in car.get('price', '') if c.isdigit()),
                ''.join(c for c in car.get('mileage', '') if c.isdigit()),
                car.get('make', ''),
                car.get('model', ''),
                ''.join(c for c in car.get('year_of_manufacture', '') if c.isdigit()),
                ''.join(c for c in car.get('mileage_km', '') if c.isdigit()),
                car.get('gear', ''),
                car.get('fuel_type', ''),
                car.get('options', ''),
                ''.join(c for c in car.get('engine_cc', '') if c.isdigit()),
                car.get('contact', ''),
                car.get('details', '')
            ]
            sheet.append_row(row)
            newest_additions.append(row)

def collect_car_data(url):
    """Collect car data from the given URL and store it in Google Sheets."""
    cars = scrape_riyasewana_list(url)
    google_sheet_name = os.environ.get('GOOGLE_SHEET_NAME')
    worksheet_name = os.environ.get('WORKSHEET_NAME')
    store_cars_in_google_sheet(cars, google_sheet_name, worksheet_name)

if __name__ == "__main__":
    RIYASEWANA_LISTING_URL = "https://riyasewana.com/search/cars/toyota/ist"
    collect_car_data(RIYASEWANA_LISTING_URL)
