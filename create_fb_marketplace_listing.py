from playwright.sync_api import sync_playwright
import random
import time

FB_URL = 'https://www.facebook.com/'

def post_facebook_marketplace_listing(credentials: dict, property_details: dict):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login_to_facebook(page, credentials)
        create_marketplace_listing(page, property_details)

        browser.close()

def login_to_facebook(page, credentials):
    page.goto(FB_URL)
    page.wait_for_timeout(random.randint(1000, 3000))

    page.fill('input[name="email"]', credentials['username'])
    page.wait_for_timeout(random.randint(1000, 3000))
    page.fill('input[name="pass"]', credentials['password'])
    page.wait_for_timeout(random.randint(1000, 3000))
    page.click('button[name="login"]')
    page.wait_for_timeout(random.randint(1000, 3000) + 3000)

    page.wait_for_load_state('load')

def create_marketplace_listing(page, property_details):
    # Navigate to Facebook Marketplace
    page.goto('https://www.facebook.com/marketplace/create/rental')
    page.wait_for_timeout(random.randint(1000, 3000))

    # Fill in the listing details
    page.wait_for_selector('label[aria-label="Home for Sale or Rent"]')
    page.click('label[aria-label="Home for Sale or Rent"]')
    page.wait_for_timeout(random.randint(1000, 3000))
    page.keyboard.press('ArrowDown')
    page.wait_for_timeout(random.randint(1000, 3000))
    page.keyboard.press('Enter')
    page.wait_for_timeout(random.randint(1000, 3000))

    page.wait_for_selector('label[aria-label="Rental type"]')
    page.click('label[aria-label="Rental type"]')
    page.wait_for_timeout(random.randint(1000, 3000))
    page.keyboard.press('ArrowDown')
    page.wait_for_timeout(random.randint(1000, 3000))
    page.keyboard.press('Enter')
    page.wait_for_timeout(random.randint(1000, 3000))

    if property_details['privateRoom']:
        page.wait_for_selector('input[aria-label="This is a private room in a shared property."]')
        page.click('input[aria-label="This is a private room in a shared property."]')
        page.wait_for_timeout(random.randint(1000, 3000))

    page.wait_for_selector('label[aria-label="Bathroom Type"]')
    page.click('label[aria-label="Bathroom Type"]')
    page.wait_for_timeout(random.randint(1000, 3000))
    page.keyboard.press('ArrowDown')
    page.wait_for_timeout(random.randint(1000, 3000))
    page.keyboard.press('Enter')
    page.wait_for_timeout(random.randint(1000, 3000))

    # Fill in form fields
    fields = {
        "How many people live here?": property_details['numberOfResidents'],
        "Number of bedrooms": property_details['bedrooms'],
        "Number of bathrooms": property_details['bathrooms'],
        "Price per month": property_details['price'],
        "Rental address": property_details['address'],
        "Rental description": property_details['description']
    }

    for label_text, value in fields.items():
        label = page.wait_for_selector(f'label:has-text("{label_text}")')
        input_type = 'textarea' if label_text == "Rental description" else 'input[type="text"]'
        input_field = label.query_selector(input_type)
        if input_field:
            input_field.fill(str(value))
            page.wait_for_timeout(random.randint(1000, 3000))
            
            # Handle address selection from dropdown
            if label_text == "Rental address":
                page.keyboard.press('ArrowDown')
                page.wait_for_timeout(random.randint(1000, 3000))
                page.keyboard.press('Enter')
                page.wait_for_timeout(random.randint(1000, 3000))

    # Upload images
    add_photo_button = page.wait_for_selector('xpath=//span[text()="Add photos"]')
    for image_path in property_details['images']:
        with page.expect_file_chooser() as fc_info:
            add_photo_button.click()
        file_chooser = fc_info.value
        file_chooser.set_files(property_details['images'])
        page.wait_for_timeout(random.randint(1000, 3000))

    # Click Next and Publish
    page.wait_for_selector('div[aria-label="Next"]')
    page.click('div[aria-label="Next"]')
    page.wait_for_timeout(random.randint(1000, 3000))
    
    page.wait_for_selector('div[aria-label="Publish"]')
    print('Publishing listing...')
    # TODO: Uncomment to actually publish
    page.click('div[aria-label="Publish"]')
    page.wait_for_timeout(random.randint(1000, 3000))

if __name__ == "__main__":
    # Example usage
    credentials = {
        "username": "qiqimei1205@gmail.com",
        "password": "Pux2oCsy1w"
    }

    property_details = {
        "title": "1B1B Suite Rental in a Newly Built 5B5B House",
        "price": "1250",
        "category": "Property Rentals",
        "propertyType": "Apartment",
        "rentalType": "Rent",
        "privateRoom": True,
        "bathroomType": "Private",
        "bedrooms": "1",
        "bathrooms": "1",
        "address": "123 Main St, Tacoma, WA",
        "description": "Private bathrooms, furnished common spaces, modern amenities...",
        "location": "Tacoma, WA",
        "images": ["./tests/image/photo.jpg"],
        "numberOfResidents": "1"
    }

    post_facebook_marketplace_listing(credentials, property_details)