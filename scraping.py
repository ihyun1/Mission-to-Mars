# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

# initialize browser, create data dictionary, end WebDriver and return the scraped data
def scrape_all():
    # Initiate headless driver for deployement
    browser = Browser('chrome', executable_path="chromedriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'hemispheres': hemisphere(browser),
        'last_modified': dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# ## Mars News

def mars_news(browser):
    # Scrape the Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find('div', class_='content_title')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get('src') #figure.lede = <figure /> and class lede

    except AttributeError:
        return None
        
    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

# ## Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    
    except BaseException: # BaseException is a little bit of a catchall for error handling. Using this as we are using Pandas not soup and splinter.
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes=["table-bordered", "table-striped", "table-hover"])

if __name__ == "__main__":
    # If running as scripte, print scraped data
    print(scrape_all())

# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

def hemisphere(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # HTML tag that holds all the links
    links = browser.find_by_css('a.product-item h3')

    for link in range(len(links)):
        # Create empty dictionary
        hemisphere = {}
        
        browser.find_by_css('a.product-item h3')[link].click()
        # Get url links
        element = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = element['href'] 
        # Get title
        hemisphere['title'] = browser.find_by_css('h2.title').text
        # Add the img_url and title to the list
        hemisphere_image_urls.append(hemisphere)
        # Go back to main browser to start loop again
        browser.back()

    return hemisphere_image_urls
