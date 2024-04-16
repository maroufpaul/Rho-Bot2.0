import json


def remove_duplicate_sublinks(data):
    """
    Remove duplicate sub-links across the entire JSON data,
    keeping only one instance of each unique link.
    """
    unique_links = set()  # To keep track of unique sub-links
    new_data = {}

    for main_key, main_value in data.items():
        if isinstance(main_value, dict):
            main_url = main_value.get('url', '')
            sub_links = main_value.get('sub_links', {})

            new_sub_links = {}
            for sub_key, sub_url in sub_links.items():
                if sub_url not in unique_links:
                    unique_links.add(sub_url)
                    new_sub_links[sub_key] = sub_url

            new_data[main_key] = {'url': main_url, 'sub_links': new_sub_links}

    return new_data


# Specify the file path of your JSON file
file_path = 'scraped_links.json'

# Load the existing JSON data with UTF-8 encoding
with open(file_path, 'r', encoding='utf-8') as file:
    links_data = json.load(file)

# Remove duplicates
cleaned_data = remove_duplicate_sublinks(links_data)

# Specify the path for the new cleaned JSON file
new_file_path = 'scraped_links_preprocess.json'

# Saving the cleaned data to a new JSON file with UTF-8 encoding
with open(new_file_path, 'w', encoding='utf-8') as file:
    json.dump(cleaned_data, file, indent=4)

print(f"Cleaned data saved to {new_file_path}")
