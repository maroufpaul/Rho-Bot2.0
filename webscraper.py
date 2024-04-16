import requests
from bs4 import BeautifulSoup
import json

def scrape_links(url, depth=1, max_depth=2):
    """
    Scrape links from the given URL. Depth controls how deep the scrape goes.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        links_dict = {}

        # Scrape the current page
        for link in soup.find_all('a', href=True):
            title = link.text.strip()
            href = link['href']

            if title and href.startswith('http'):
                links_dict[title] = href

        # If depth is less than max_depth, recursively scrape the linked pages
        if depth < max_depth:
            for title, href in links_dict.items():
                sub_links = scrape_links(href, depth + 1, max_depth)
                links_dict[title] = {'url': href, 'sub_links': sub_links}

        return links_dict
    except requests.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return {}

def save_to_json(data, filename):
    """
    Save the given data to a JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {filename}")
    except IOError as e:
        print(f"Error writing to file {filename}: {str(e)}")

# Scraping the links with increased depth
url_to_scrape = "https://www.rhodes.edu"
scraped_links = scrape_links(url_to_scrape, depth=1, max_depth=2)

# Saving the result to a JSON file
save_to_json(scraped_links, 'scraped_links.json')
