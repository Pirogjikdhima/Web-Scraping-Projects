import os
import re

from bs4 import BeautifulSoup
import requests


class Chapter:
    """Represents a chapter with a title and its paragraphs."""
    def __init__(self, title: str, paragraphs: list[str]) -> None:
        """Initializes a Chapter instance with title and paragraphs."""
        self.title = title
        self.paragraphs = paragraphs


def request(url: str, headers: dict = None) -> requests.Response:
    """Sends an HTTP GET request to the specified URL and returns the response.

    Args:
        url: The URL to send the GET request to.
        headers: Optional HTTP headers to include in the request.

    Returns:
        A Response object containing the server's response.

    Raises:
        ValueError: If the status code of the response is not 200.
    """
    if headers is None:
        headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/50.0.2661.102 Safari/537.36')
        }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError("Couldn't open the link, status code: "
                         f"{response.status_code}")
    
    return response


def get_novel(name: str) -> tuple[requests.Response, str]:
    """Constructs the URL for the novel and returns the response and formatted novel title.

    Args:
        name: The name of the novel.

    Returns:
        A tuple containing the response and formatted novel title.
    """
    novel_title = re.sub(r'[^a-zA-Z]', ' ', name).lower().replace(" ", "-")
    url = f"https://www.lightnovelworld.com/novel/{novel_title}/chapters"
    response = request(url)
    return response, novel_title


def get_chapter_links(response: requests.Response) -> list:
    """Extracts chapter links from the novel's chapter list page.

    Args:
        response: The response object of the novel's chapter page.

    Returns:
        A list of chapter links.
    """
    soup = BeautifulSoup(response.content, features="lxml")
    unordered_list = soup.find("ul", class_="chapter-list")
    list_items = unordered_list.find_all("li")
    links = [item.find('a')['href'] for item in list_items if item.find('a')]
    return links


def get_chapter(link: str, novel_title: str) -> None:
    """Downloads the content of a chapter and saves it.

    Args:
        link: The URL link to the chapter.
        novel_title: The formatted title of the novel for saving the chapter.
    """
    url = f"https://www.lightnovelworld.com{link}"
    response = request(url)
    soup = BeautifulSoup(response.content, features="lxml")
    
    title = soup.find("span", class_="chapter-title").text.strip()
    paragraphs = [p.text.strip() for p in soup.find_all("p")]
    
    chapter = Chapter(title=title, paragraphs=paragraphs)
    save_chapter(chapter, novel_title)


def save_chapter(chapter: Chapter, novel_title: str) -> None:
    """Saves the chapter to a text file.

    Args:
        chapter: The Chapter object containing the chapter's content.
        novel_title: The formatted title of the novel to create the folder.
    """
    if not os.path.exists(novel_title):
        os.makedirs(novel_title)
    
    chapter_title = re.sub(r'[^a-zA-Z0-9 ]', '', chapter.title).strip()
    filename = f"{chapter_title}.txt"
    
    with open(os.path.join(novel_title, filename), 'w', encoding='utf-8') as file:
        file.write(f"{chapter.title}\n\n")
        for paragraph in chapter.paragraphs:
            file.write(f"{paragraph}\n\n")


def get_page(response: requests.Response) -> tuple[requests.Response, bool]:
    """Checks if there is another page of chapters and fetches it.

    Args:
        response: The response object of the current chapter page.

    Returns:
        A tuple containing the response of the next page and a boolean
        indicating if there is another page.
    """
    soup = BeautifulSoup(response.content, features="lxml")
    pagenav = soup.find("div", class_="pagenav")
    skip_to_next = pagenav.find("li", class_="PagedList-skipToNext") if pagenav else None
    
    if not skip_to_next:
        return None, False
    
    page = skip_to_next.find("a")['href']
    url = f"https://www.lightnovelworld.com{page}"
    other_response = request(url)
    return other_response, True


def main() -> None:
    """Main function to orchestrate downloading chapters of a novel."""
    novel_name = input("Enter the novel name: ")
    response, novel_title = get_novel(novel_name)
    
    links = get_chapter_links(response)
    for link in links:
        get_chapter(link, novel_title)
    
    other_response, condition = get_page(response)
    while condition:
        links = get_chapter_links(other_response)
        for link in links:
            get_chapter(link, novel_title)
        other_response, condition = get_page(other_response)
    
    print(f"All chapters have been saved in the folder: {novel_title}")


if __name__ == "__main__":
    main()
