from bs4 import BeautifulSoup as bs
from splinter import Browser
import pandas as pd

executable_path = {'executable_path': '/Users/Gemma/Downloads/chromedriver'}
browser = Browser('chrome', **executable_path)

def scrape():
    executable_path = {'executable_path': '/Users/Gemma/Downloads/chromedriver'}
    browser = Browser('chrome', **executable_path)
    news_title, news_p = mars_news(browser)
    
    data = {'news_title':news_title, 'news_p':news_p, 
           'featured_image':featured_image(browser), 'mars_weather':mars_weather(browser),
           'mars_facts':mars_facts(), 'mars_hemispheres':mars_hemispheres(browser)}
    browser.quit()
    return data

# NASA Mars News
def mars_news(browser):
    url = "https://mars.nasa.gov/news"
    browser.visit(url)

    html = browser.html
    soup = bs(html, 'html.parser')

    try:
        # Pulling latest news article title
        news_title = soup.find('div', class_='content_title').get_text()

        # Pulling latest news article paragraph
        news_p = soup.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None
    
    return news_title, news_p


# JPL Mars Space Images
def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Click on image
    button = browser.find_by_id('full_image')
    button.click()

    # Get more information on featured image
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info = browser.find_link_by_partial_text('more info')
    more_info.click()

    html = browser.html
    soup = bs(html, 'html.parser')

    # Find url of featured image
    featured_image_url = soup.select_one('figure.lede a img')
    try:
        featured_image_url = featured_image_url.get('src')
    except AttributeError:
        return None
    featured_image_url = f"https://www.jpl.nasa.gov{featured_image_url}"
    
    return featured_image_url


# Mars Weather
def mars_weather(browser):
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    html = browser.html
    soup = bs(html, 'html.parser')

    # Find the latest tweet
    tweet = soup.find('div', attrs={'class':'tweet', 'data-name':'Mars Weather'})
    mars_weather = tweet.find('p', 'tweet-text').get_text()
    return mars_weather


# Mars Facts
def mars_facts():
    try:
        facts = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None
    facts.columns = ['Description', 'Value']
    facts.set_index('Description', inplace=True)

    # Convert data frame into html table
    return facts.to_html(classes="table table-striped")


# Mars Hemispheres
def mars_hemispheres(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create the empty list to store image urls
    hemisphere_image_urls = []

    # All of the hemispheres
    links = browser.find_by_css('a.product-item h3')
    for i in range(len(links)):
        hemisphere = {}
        # Click on link for hemisphere
        browser.find_by_css('a.product-item h3')[i].click()
        # Get href for image
        sample_image = browser.find_link_by_text('Sample').first
        hemisphere['img_url'] = sample_image['href']
        # Get title
        hemisphere['title'] = browser.find_by_css('h2.title').text
        # Append to list
        hemisphere_image_urls.append(hemisphere)
    
        browser.back()

    # Return list of dictionaries of urls and titles
    return hemisphere_image_urls


if __name__ == '__main__':
    print(scrape())

