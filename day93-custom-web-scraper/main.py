from bs4 import BeautifulSoup
import requests
import pandas as pd

# Request and parse HTML content.
response = requests.get("https://www.audible.com/search?keywords=book&node=18573211011")
# response = requests.get("https://www.audible.com/es_US/search?keywords=book&node=18573211011&ref=a_search_c4_pageNext&page=3&ref_pageloadid=dvDZ03ESIMKOYjc5&pf_rd_p=1d79b443-2f1d-43a3-b1dc-31a2cd242566&pf_rd_r=KMGQ40XQRQRYP1H3WNHA&plink=nSvU5wXoXmpdFYVn&pageLoadId=qyMKoy3VZm6UDaAj&creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a")
web_page = response.text
soup = BeautifulSoup(web_page, "html.parser")

# Find all links that contain each category of interest.
titles_authors_narrators_links = soup.find_all('a', {'class': 'bc-link bc-color-link'})
small_letters_text = soup.find_all('span', {'class': 'bc-text bc-size-small bc-color-secondary'})
price_letters_text = soup.find_all('span', {'class': 'bc-text bc-size-base bc-color-base'})
img_tag = soup.find_all('img')

# Categorize each link to create the keys and values of a dictionary.
all_categories = {}
previous_value = None

for link in titles_authors_narrators_links:
    href = link.get('href', '') #  Empty string is the default value that will be returned if the 'href' attribute doesn't exist.
    text = link.text.strip() # .strip() removes extra whitespace
    if text and '/pd/' in href:
        category = "Title"
        # if category not in all_categories:
        #     all_categories[category] = []
        # all_categories[category].append(text)
        all_categories.setdefault(category, []).append(text) # Same as previous lines but in one line
    elif '/author/' in href or 'searchAuthor' in href:
        category = "Author"
        # Check if previous value was "Author" in order to skip it in case there are multiple authors.
        if 'author' in str(previous_value) or 'searchAuthor' in str(previous_value):
            pass
        else:
            all_categories.setdefault(category, []).append(text)
    elif 'Narrator' in href or "/ep/" in href:
        category = "Narrator"
        all_categories.setdefault(category, []).append(text)
    previous_value = link

for link in small_letters_text:
    text = link.text.strip()
    if "Duración" in text:
        category = "Duration"
        duration_text = text.split(": ")[1]
        all_categories.setdefault(category, []).append(duration_text)

for price in price_letters_text:
    text = price.text.strip()
    if "$" in text:
        category = "Price"
        all_categories.setdefault(category, []).append(text)

for img in img_tag:
    if ".jpg" in str(img['src']):
        category = "Image link"
        img_link = img['src']
        all_categories.setdefault(category, []).append(img_link)

# Troubleshooting zone.
dict_lengths = {key: len(value) for key, value in all_categories.items()}
# print(dict_lengths)

# Save dictionary as CSV file.
df = pd.DataFrame(all_categories)
df.to_csv('audiobooks.csv', index=False)
print("Data successfully scraped and exported to 'audiobooks.csv' 👍")
