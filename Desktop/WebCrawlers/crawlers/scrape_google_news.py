import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from datetime import datetime,timedelta
import pandas as pd
from textblob import TextBlob


# Perform a search on Google News and store the URL
search_url_Google = "https://www.google.com/search?q=google+stock+news&client=safari&sca_esv=574510585&rls=en&tbm=nws&sxsrf=AM9HkKk0GQD4m2SoX9dmJWw3Xg9OzeTsTQ:1697662506857&source=lnt&tbs=sbd:1&sa=X&ved=2ahUKEwjgtK3VvYCCAxXKJzQIHSU2DA8QpwV6BAgDEBM&biw=1443&bih=858&dpr=1"
TICKER = 'GOOGL'
ARTICLE_LIMIT = 20
SCROLL_PAUSE_TIME = 2

# Set up the web driver (you need to install a driver for your preferred browser, e.g., ChromeDriver)
driver = webdriver.Chrome()
# Navigate to the Google News search results page
driver.get(search_url_Google)

def analyze_sentiment(title):
    blob = TextBlob(title)
    sentiment = blob.sentiment.polarity
    return sentiment

def convert_date(days, date_measure):
    date_of_article = datetime.now()
    if (date_measure == 'weeks' or date_measure == 'week'):
        num_days =days * 7
        date_of_article = datetime.now() - timedelta(days=num_days)
    elif (date_measure == 'days' or date_measure =='day'):
        num_days =days * 1
        date_of_article = datetime.now() - timedelta(days=num_days)
    elif (date_measure == 'month' or date_measure == 'months'):
        num_days = days*30
        date_of_article = datetime.now() - timedelta(days=num_days)
    formatted_date = date_of_article.strftime('%Y-%m-%d')
   
    return formatted_date

def scrape(articles):
    while len(articles) < ARTICLE_LIMIT:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait for the next page button to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Next')]"))
            )
            
            wait = WebDriverWait(driver, 10)
            next_button = wait.until(EC.presence_of_element_located((By.XPATH, "//span[.='Next']")))
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            for article in soup.find_all('div',class_='n0jPhd ynAwRc MBeuO nDgy9d'):
                title = article.get_text()
                # Extract the publication date, assuming it's contained within a specific HTML element
                for date in soup.find_all('div', class_='OSrXXb rbYSKb LfVVr'):
                    article_date = date.get_text()
                    date_format = "%b %d, %Y"
                    try:
                        # if date is in format July 16, 2023 convert to datetime
                        date_object = datetime.strptime(article_date, date_format)
                        formatted_date = date_object.strftime('%Y-%m-%d')
                    except ValueError:
                        # else calculate how many days ago the article was posted, convert to DT object
                        split_date = article_date.split()
                        num_days = int(split_date[0])
                        days_weeks_or_months = split_date[1]
                        formatted_date = convert_date(num_days, days_weeks_or_months)
                   
                    if title not in articles:
                        articles[title] = {'Date': formatted_date}
           
            time.sleep(SCROLL_PAUSE_TIME)
            next_button.click()
        except:
            pass
     
    driver.close()
    return articles

if __name__ == "__main__":
    articles = {}
    crawl = scrape(articles)
    file_path = 'news_articles_google.csv'
    fieldnames = ['Title', 'Date', 'Sentiment Polarity','Symbol']
    # Create a list of dictionaries to store results in
    data_list = []
    for title, data in crawl.items():
        sentiment = analyze_sentiment(title)
        data_list.append({'Title': title, 'Date': data['Date'],'Sentiment Polarity':sentiment,'Symbol':TICKER})
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)
    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)
