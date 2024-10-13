import os

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver() -> webdriver.Chrome:
    """Sets up the Selenium WebDriver for Chrome with headless options.

    Returns:
        webdriver.Chrome: A configured Chrome WebDriver.
    """
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_number_of_pages(url: str, driver: webdriver.Chrome) -> int:
    """Retrieves the total number of pages for a product list.

    Args:
        url (str): The URL of the product category page.
        driver (webdriver.Chrome): The WebDriver instance to use for fetching.

    Returns:
        int: The total number of pages in the product list.
    """
    driver.get(url)
    pagination_xpath = '//*[@id="affix2"]/div/div[2]/ul/li'
    
    try:
        page_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, pagination_xpath))
        )
        page_numbers = [element.text.strip() for element in page_elements][1:-1]
        return 1 if len(page_numbers) == 1 else int(page_numbers[-1])
    except TimeoutException:
        print("TimeoutException: Unable to find pagination elements.")
        return 1


def scrape_product_data(url: str, pages: int, driver: webdriver.Chrome, directory: str, filename: str) -> None:
    """Scrapes product data and saves it as a CSV file.

    Args:
        url (str): The base URL of the product list.
        pages (int): The number of pages to scrape.
        driver (webdriver.Chrome): The WebDriver instance to use.
        directory (str): The directory where the CSV file will be saved.
        filename (str): The name of the output CSV file.
    """
    products = []
    price_xpath = "//*[contains(@class, 'product-price__amount--value') and contains(@class, 'ng-binding')]"
    title_xpath = "//*[contains(@class, 'product-list-item__content--title') and contains(@class, 'ng-binding')]"
   
    for page in range(1, pages + 1):
        page_url = f"{url}{page}"
        driver.get(page_url)
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, price_xpath))
            )
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, title_xpath))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.find_all("div", class_="ng-scope product-list-item-grid")

            for item in items:
                whitebox = item.find("div", class_="white-box")
                title = whitebox.find("h2", class_="product-list-item__content--title ng-binding").get_text()
                prices_section = whitebox.find("div", class_="product-list-item__prices pt35")
                happy_card = prices_section.find("div", class_="HappyCard")
                new_price_model = prices_section.find("div", class_="newPriceModel")

                current_price = happy_card.find("span", class_="product-price__amount--value ng-binding")
                current_price = current_price.get_text() if current_price else "N/A"
                
                old_price = new_price_model.find("span", class_="product-price__amount--value ng-binding").get_text()
                print(title, current_price, old_price)

                products.append({
                    "Emri": title,
                    "Cmimi aktual": current_price,
                    "Cmimi i vjeter": old_price
                })
        
        except TimeoutException:
            print(f"TimeoutException on page {page}: Unable to find product elements.")
            continue

    df = pd.DataFrame(products)
    file_path = os.path.join(directory, f'{filename}.csv')
    df.to_csv(file_path, mode='w', header=True, index=False)
    print(f"Data saved to {file_path}")


def create_directory(directory: str, name: str) -> str:
    """Creates a directory if it doesn't already exist.

    Args:
        directory (str): The parent directory.
        name (str): The name of the subdirectory.

    Returns:
        str: The path of the created directory.
    """
    path = os.path.join(directory, name)
    os.makedirs(path, exist_ok=True)
    return path


def get_categories(driver: webdriver.Chrome, base_directory: str) -> None:
    """Fetches product categories and scrapes the data for each.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        base_directory (str): The base directory where data will be stored.
    """
    driver.get("https://www.neptun.al/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="neptunMain"]')))
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    categories = soup.find("li", id="neptunMain").find_all("li", attrs={'data-tag': True})

    for category in categories:
        category_name = category.find('a').get_text(strip=True).title()
        category_path = create_directory(base_directory, category_name)
        
        subcategories_menu = category.find("ul", class_="dropdown-menu")
        subcategories = subcategories_menu.find_all("ul", class_="dropdown-menu")

        for subcategory in subcategories:
            subcategory_name = subcategory.find_previous('a').get_text(strip=True).title()
            subcategory_path = create_directory(category_path, subcategory_name)
            
            sub_subcategories = subcategory.find_all("a")
            for sub_subcategory in sub_subcategories:
                title = sub_subcategory.get_text(strip=True).title().replace("/", "")
                link = f"https://www.neptun.al{sub_subcategory['href']}?items=100&page="
                pages = get_number_of_pages(link, driver)
                scrape_product_data(url=link, pages=pages, driver=driver, directory=subcategory_path, filename=title)


def main() -> None:
    """Main function to initiate scraping."""
    driver = setup_driver()
    base_directory = "Neptun.al"
    
    get_categories(driver, base_directory)
    
    driver.quit()


if __name__ == "__main__":
    main()
