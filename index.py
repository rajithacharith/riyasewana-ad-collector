import os
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

def extract_riyasewana_advertisement(url):
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
    else:
        return None

def scrape_riyasewana_list(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    }
    cars = []
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('li.item.round'):
            car = {
                'title': item.find('h2', class_='more').find('a').get('title').strip(),
                'url': item.find('h2', class_='more').find('a').get('href').strip(),
                'image': item.find('div', class_='imgbox').find('img').get('src').strip(),
                'location': item.find('div', class_='boxtext').find_all('div', class_='boxintxt')[0].text.strip(),
                'price': item.find('div', class_='boxtext').find_all('div', class_='boxintxt')[1].text.strip(),
                'mileage': item.find('div', class_='boxtext').find_all('div', class_='boxintxt')[2].text.strip(),
            }
            ad_details = extract_riyasewana_advertisement(car['url'])
            if ad_details is not None:
                car.update(ad_details)
            cars.append(car)
    return cars

def email_newest_listings(newest_additions):
    print("Emailing newest listings")

            
def store_cars_in_google_sheet(cars, google_sheet_name, sheet_name):
    google_credentionals_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_PATH')
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentionals_path, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open(google_sheet_name).worksheet(sheet_name)
    header = ["Title", "URL", "Image", "Location", "Price", "Mileage", "Make", "Model", "Year of Manufacture", "Mileage (km)", "Gear", "Fuel Type", "Options", "Engine (cc)","Contact","Details"]
    if not sheet.row_values(1):
        sheet.append_row(header)
    existing_urls = sheet.col_values(2)  
    print(existing_urls)
    newest_additions = []
    for car in cars:
        if car.get('url', '') not in existing_urls:
            row = [
                car.get('title', ''),
                car.get('url', ''),
                "https:" + car.get('image', ''),
                car.get('location', ''),
                car.get('price', ''),
                car.get('mileage', ''),
                car.get('make', ''),
                car.get('model', ''),
                car.get('year_of_manufacture', ''),
                car.get('mileage_km', ''),
                car.get('gear', ''),
                car.get('fuel_type', ''),
                car.get('options', ''),
                car.get('engine_cc', ''),
                car.get('contact', ''),
                car.get('details', '')
            ]
            sheet.append_row(row)
            newest_additions.append(row)
    
def collect_car_data(url):
    cars = scrape_riyasewana_list(url)
    store_cars_in_google_sheet(cars, "Test", "Sheet2")


if __name__ == "__main__":
    riyasewana_listing_url = "https://riyasewana.com/search/cars/toyota/ist"
    collect_car_data(riyasewana_listing_url)
