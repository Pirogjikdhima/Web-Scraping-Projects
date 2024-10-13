import os
import re
import time

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def setup(url: str, pattern: re.Pattern, directory: str) -> None:
    """Sets up the Chrome WebDriver, navigates to the given URL, and processes links matching the pattern.

    Args:
        url: The URL to scrape for chapter links.
        pattern: A compiled regular expression pattern to match valid chapter URLs.
        directory: The directory to save the downloaded chapters.
    """
    options = Options()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)

    wait(3)

    selector = driver.find_element(By.CSS_SELECTOR, "button")
    selector.click()

    wait(3)

    links = driver.find_elements(By.CSS_SELECTOR, "a")
    
    for link in links:
        href = link.get_attribute("href")
        if href and pattern.match(href):
            new_url = href.replace("novelbin.me/novel-", "fast.novelupdates.net/")
            get_chapter(new_url, directory)

    driver.quit()


def get_chapter(url: str, directory: str) -> None:
    """Fetches a chapter from the given URL and saves it as a text file in the specified directory.

    Args:
        url: The chapter URL to scrape.
        directory: The directory to save the chapter as a text file.
    """
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, features="lxml")
        paragraphs = soup.find_all("p")
        title_element = soup.find_all("span", itemprop="name")[2]
        
        if title_element:
            title = title_element.get_text().strip()
            valid_title = re.sub(r'[\/:*?"<>|]', "", title).title()
            file_path = os.path.join(directory, f"{valid_title}.txt")

            with open(file_path, "w", encoding="utf-8") as file:
                for paragraph in paragraphs:
                    file.write(paragraph.get_text() + "\n\n")
        else:
            raise ValueError(f"No title found for URL: {url}")
    else:
        raise Exception(f"Failed to retrieve the webpage. Status code: {response.status_code}")


def wait(seconds: int) -> None:
    """Pauses execution for a given number of seconds.

    Args:
        seconds: The number of seconds to wait.
    """
    time.sleep(seconds)


def main() -> None:
    """Main function that sets up the scraping process and downloads chapters."""
    directory = "I Became A Flashing Genius At The Magic Academy"

    if not os.path.exists(directory):
        os.makedirs(directory)

    url = "https://novelbin.com/b/i-became-a-flashing-genius-at-the-magic-academy#tab-chapters-title"
    pattern = re.compile(r"https://fast.novelupdates.net/book/i-became-a-flashing-genius-at-the-magic-academy/chapter-[\w-]+")

    setup(url=url, pattern=pattern, directory=directory)

if __name__ == "__main__":
    main()
