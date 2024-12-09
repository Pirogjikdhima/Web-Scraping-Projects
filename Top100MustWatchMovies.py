import re

from bs4 import BeautifulSoup
import requests


def remove_numbers_before_first_parenthesis(input_string: str) -> str:
    """Removes numbers before the first closing parenthesis in the string.

    Args:
        input_string: The input string that may contain numbers before the first closing parenthesis.

    Returns:
        The modified string with numbers removed before the first closing parenthesis.
        If no closing parenthesis is found, returns the original string.
    """
    # Find the position of the first closing parenthesis
    first_parenthesis_pos = input_string.find(')')
    
    # If there is no closing parenthesis, return the original string
    if first_parenthesis_pos == -1:
        return input_string
    
    # Split the string into two parts: before and after the first closing parenthesis
    before_parenthesis = input_string[:first_parenthesis_pos]
    after_parenthesis = input_string[first_parenthesis_pos:]
    
    # Remove numbers from the part before the first closing parenthesis
    before_parenthesis = re.sub(r'\d+', '', before_parenthesis)
    
    # Concatenate the two parts and return the result
    return before_parenthesis + after_parenthesis


def main() -> None:
    """Fetches a list of movies from a webpage and saves them to a text file."""
    url = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        titles = soup.find_all("h3", class_="title")
        
        # Reverse the list of movie titles
        movies = [title.get_text() for title in titles][::-1]
        
        # Write the movie titles to a file
        with open("movies.txt", "w") as file:
            for movie in movies:
                file.write(f"{movie}\n")
    else:
        raise ValueError(f"Failed to retrieve data. Status code: {response.status_code}")


if __name__ == "__main__":
    main()
