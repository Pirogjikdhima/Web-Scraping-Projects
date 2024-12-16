import os

from bs4 import BeautifulSoup
import pandas as pd
import requests


def find_next_link(soup: BeautifulSoup) -> str:
    """Finds the URL for the next page in pagination.

    Args:
        soup: BeautifulSoup object containing the HTML content.

    Returns:
        The URL for the next page if available, otherwise False.
    """
    div = soup.find("div", class_="ty-pagination__items")
    if div is None:
        return False
    
    a_elements = div.find_all("a", class_="cm-history ty-pagination__item cm-ajax")
    span_number = int(div.find("span").text) + 1
    
    urls = [link.get("href") for link in a_elements]
    
    for url in urls:
        if str(span_number) in url:
            return url
    
    return False


def save(response: requests.Response, filename: str) -> str:
    """Saves product data from the response to a CSV file and finds the next page.

    Args:
        response: Response object from the requests library.
        filename: Name of the file to save the data to.

    Returns:
        The URL for the next page if available, otherwise False.
    
    Raises:
        ValueError: If the response status code is not 200.
    """
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, features="lxml")
        products = soup.find_all("div")
        
        seen_products = set()
        product_data = []

        for product in products:
            title_element = product.find("a", class_="product-title")
            price_element = product.find("span", class_="ty-price-num")
            old_price_element = product.find("bdi")
            
            if title_element and price_element and old_price_element:
                title = title_element.get_text(strip=True).strip()
                current_price = price_element.get_text(strip=True).replace("Lekë", "").replace(".", ",").strip()
                old_price = old_price_element.get_text(strip=True).replace("Lekë", "").replace(".", ",").strip()
                
                if old_price == '-' or old_price == "Home":
                    continue
                
                product_entry = (title, current_price, old_price)
                
                if product_entry not in seen_products:
                    seen_products.add(product_entry)
                    product_data.append({
                        "Emri": title,
                        "Cmimi aktual": current_price,
                        "Cmimi i vjeter": old_price
                    })
        
        os.makedirs("Globe", exist_ok=True)
        df = pd.DataFrame(product_data)
        file_path = f"Globe/{filename}"

        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, mode='w', header=True, index=False)
        
        return find_next_link(soup)
    
    else:
        raise ValueError(f"Error: Problem with opening the website. Status code: {response.status_code}")


def submain(name: str, filename: str) -> None:
    """Handles the scraping and saving for a given category.

    Args:
        name: The category name for the URL.
        filename: The file name to save the data to.
    """
    url = f"https://globe.al/{name}/"
    response = requests.get(url)
    url = save(response, filename=filename)
    
    while url:
        response = requests.get(url)
        url = save(response, filename=filename)


def get_telefonia(filename="GlobeTelefonia.csv") -> None:
    """Starts the scraping for the Telefonia category."""
    submain("telefonia", filename=filename)


def get_foto_dhe_video(filename="GlobeFotoDheVideo.csv") -> None:
    """Starts the scraping for the Foto dhe Video category."""
    submain("foto-video-sq", filename=filename)    


def get_elektroshtepiake_te_medha(filename="GlobeElektroshtepiakeTeMedha2.csv") -> None:
    """Starts the scraping for the Elektroshtepiake Te Medha category."""
    submain("elektroshtepiake-te-medha-sq", filename=filename)    


def get_elektroshtepiake_te_vogla(filename="GlobeElektroshtepiakeTeVogla.csv") -> None:
    """Starts the scraping for the Elektroshtepiake Te Vogla category."""
    submain("elektroshtepiake-te-vogla-sq", filename=filename)  


def get_kompjutera_dhe_rrjeti(filename="GlobeKompjuteraDheRrjeti.csv") -> None:
    """Starts the scraping for the Kompjutera Dhe Rrjeti category."""
    submain("kompjutera-dhe-rrjeti", filename=filename)  


def get_kondicionimi(filename="GlobeKondicionimi.csv") -> None:
    """Starts the scraping for the Kondicionimi category."""
    submain("kondicionimi", filename=filename)   


def main() -> None:
    """Main function to start scraping for all categories."""
    get_elektroshtepiake_te_medha()
    get_elektroshtepiake_te_vogla()
    get_foto_dhe_video()
    get_kompjutera_dhe_rrjeti()
    get_kondicionimi()
    get_telefonia()   


if __name__ == '__main__':
    main()


    
    
    
    
    