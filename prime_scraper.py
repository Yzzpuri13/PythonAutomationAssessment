import json
import time
from playwright.sync_api import sync_playwright

def run(playwright):
    # Launch a new browser
    browser = playwright.chromium.launch(headless=True)
    # Create a new browser context
    context = browser.new_context()
    # Open a new page
    page = context.new_page()
    # Navigate to the desired URL
    page.goto("https://www.amazon.com/deals")
    print("Navigating to Amazon deals page...")
    
    # Locate and click the "Prime Exclusive" checkbox
    prime_checkbox = page.locator("div[data-csa-c-element-id='filter-accessType-Prime Exclusive'] label")
        
    # Scroll to the checkbox
    print("Locating and clicking the 'Prime Exclusive' checkbox...")
    prime_checkbox.evaluate("element => element.scrollIntoView()")
    
    # Check the checkbox
    print("Checking the checkbox...")
    prime_checkbox.check()
    
    # Wait for the page to update
    print("Waiting for the page to update...")
    page.wait_for_load_state("networkidle")
    
    # Get the title of the page
    title = page.title()
    # Print the title
    print(f"Page title: {title}")
    
    # Extract product details
    product_cards = page.locator("a[data-testid='product-card-link']")
    
    products = []
    max_products = 3
    
    for i in range(min(product_cards.count(), max_products)):
        card = product_cards.nth(i)
        print(f"Processing product card {i + 1}...")
                        
        try:
            product_name = card.locator("p.ProductCard-module__title_awabIOxk6xfKvxKcdKDH").inner_text()
        except:
            product_name = "No Product Name"
            
        # Wait 15 seconds before going to the product detail page
        print("Waiting 15 seconds before navigating to the product detail page...")
        time.sleep(15)

        try:
            product_link = card.get_attribute("href")
            product_link = f"{product_link}"
            if not product_link.startswith("https://www.amazon.com"):
                product_link = f"https://www.amazon.com{product_link}"
            print(f"Product Link: {product_link}")
        except:
            product_link = "No Product Link"
            
        # Navigate to the product detail page to extract prices
        detail_page = context.new_page()
        try:
            detail_page.goto(product_link, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"Failed to load product detail page for {product_name}: {e}")
            continue
        
        try:
            list_price = detail_page.locator("span.a-text-price span.a-offscreen").inner_text()
        except:
            list_price = "No List Price"

        try:
            discounted_price = detail_page.locator("span.a-price span.a-offscreen").first.inner_text()
        except:
            discounted_price = "No Discounted Price"

        product = {
            "product-name": product_name,
            "product-link": product_link,
            "list-price": list_price,
            "discounted-price": discounted_price
        }

        products.append(product)
        detail_page.close()
    
    # Print the extracted products in JSON format
    print(json.dumps(products, indent=2))
    
    # Save the extracted products to a txt file
    with open("products.txt", "w") as file:
        file.write(json.dumps(products, indent=2))
        print("Data written to products.txt successfully.")
    
    # Close the browser
    browser.close()

# Use the Playwright library
with sync_playwright() as playwright:
    run(playwright)
