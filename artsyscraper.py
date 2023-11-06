# this artsy scraping file will BATCH the artwork so there will be multiple folders per batch (artsy_images/batch1, artsy_images/batch2, etc), and each batch is 3 pages.
# the reason for the batching is so that when there is an error, the code will skip to the next batch instead of getting stuck

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from datetime import datetime

import csv
import requests
import os
import time
import re

PATH = "C:\Program Files (x86)\chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

driver.get("https://www.artsy.net/collect")
driver.maximize_window()

wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed

# Initialize a counter and relative path variable
counter = 1
relative_path = "artsy_images/"

batch_size = 3

# Count the number of pages
nav_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'nav[aria-label="Pagination"]'))
)
page_links = nav_element.find_elements(By.CSS_SELECTOR, 'a.Pagination__PageLink-sc-1r2jw01-0')

# Find the last page number, excluding "Next" link
last_page = page_links[-2].text
if last_page.isdigit():
    num_pages = int(last_page)
    print("Number of Pages:", num_pages)

# Base URL for Artsy collect pages
base_url = "https://www.artsy.net/collect?page="

# Start page count at 1
current_page = 1


#set empty list variables
id = []
date_created = []
artist = []
date_scraped = []
text_type = []
text = []
image_path = []
image_type = []
text_author = []
auction_price = []

batch_counter = 0

def create_batch_folder(batch_counter):
    batch_folder = os.path.join(relative_path, f"batch{batch_counter}")
    os.makedirs(batch_folder, exist_ok=True)  # Create the folder if it doesn't exist
    return batch_folder

# Iterate through batches of pages
while current_page <= num_pages:
    batch_counter += 1 # We are currently on batch 1
    batch_start = current_page
    batch_end = min(current_page + batch_size - 1, num_pages)

    batch_folder = create_batch_folder(batch_counter)


    try:
        # Iterate through pages within the current batch
        for page in range(batch_start, batch_end+1):
            try:
                # Execute JavaScript to hide the cookie banner
                print("Successfully navigated to page (within page loop): " + str(page))

                driver.execute_script('document.querySelector(".Box-sc-15se88d-0.cgchZM").style.display = "none";')

                elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.Box-sc-15se88d-0.Text-sc-18gcpao-0.ilQWRL'))
                )
                num_elements = len(elements)
                print("Num of Elements:", num_elements)

                elements = driver.find_elements(By.CSS_SELECTOR, '.Box-sc-15se88d-0.Text-sc-18gcpao-0.ilQWRL')
                element=elements[0]

                #iterate through elements in page
                for i in range(num_elements):
                    try:
                        elements = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.Box-sc-15se88d-0.Text-sc-18gcpao-0.ilQWRL'))
                        )   

                        
                        element = elements[i]
                        driver.execute_script("arguments[0].click()", element)

                        #ID
                        image_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'transitionFrom--ViewInRoom'))
                        )

                        # Get the image URL from the src attribute
                        image_url = image_element.get_attribute("src")

                        # Generate the filename with the desired format
                        filename = f"artsy-{str(counter).zfill(7)}.jpg"
                        id.append(filename)

                        # Modify the full_path to save images in the batch folder
                        full_path = os.path.join(batch_folder, filename)

                        # Download the image and save it to the "artsy_images" directory
                        image_response = requests.get(image_url).content
                        with open(full_path, "wb") as img_file:
                            img_file.write(image_response)

                        #DATE CREATED
                        try:
                            date_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.Box-sc-15se88d-0.Text-sc-18gcpao-0.caIGcn.bhlKfb'))
                            )
                            date_text = date_element.text
                            numeric_date = re.sub(r'\D', '', date_text[-4:])  # Remove non-numeric characters
                            if numeric_date:
                                date_created.append(numeric_date)
                            else:
                                date_created.append(None)
                        except:
                            date_created.append(None)

                        #ARTIST
                        try:
                            artist_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.RouterLink__RouterAwareLink-sc-1nwbtp5-0.dikvRF.ArtworkSidebarArtists__StyledArtistLink-eqhzb8-0.jdgrPD'))
                            )
                            artist.append(artist_element.text)
                        except:
                            artist.append(None)

                        #DATE SCRAPED

                        date_scraped.append(datetime.now().strftime('%m-%d-%Y'))

                        #TEXT TYPE

                        text_type_element = "Description"

                        text_type.append(text_type_element)

                        # TEXT

                        try:
                            text_element = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.Box-sc-15se88d-0.Text-sc-18gcpao-0.HTML__Container-sc-1im40xc-0.cgchZM.fxdlkC'))
                            )
                            text.append(text_element.text)
                        except:
                            text.append(None)

                        # IMAGE_PATH

                        last_occurrence_index = full_path.rfind("ArtsyScrape")
                        relative_full_path = full_path[last_occurrence_index:]
                        fixed_full_path = full_path.replace("/", "\\")
                        fixed_full_path = ("ArtsyScrape\\"+fixed_full_path)
                        image_path.append(fixed_full_path)

                        try:
                            # Find the "dt" element with the text "Medium"
                            medium_dt = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//dt[text()="Medium"]'))
                            )

                            # Find the associated "dd" element
                            medium_dd = medium_dt.find_element(By.XPATH, './following-sibling::dd')

                            # Get the value of the "Medium" attribute
                            medium_value = medium_dd.text

                            # Append the medium value to your list
                            image_type.append(medium_value)
                        except NoSuchElementException:
                            # Handle the case when "Medium" element is not present
                            image_type.append(None)

                        #TEXT AUTHOR

                        try:
                            parent_author_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '.Box-sc-15se88d-0.Flex-cw39ct-0.bFxEdP'))
                            )
                            author_element = parent_author_element.find_element(By.CSS_SELECTOR, '.Box-sc-15se88d-0.Text-sc-18gcpao-0.bTYDYt')
                            author_name = author_element.text
                            
                            text_author.append(author_name)
                        except:
                            text_author.append(None)

                        #AUCTION PRICE

                        try:
                            # Find elements with the specified classes
                            price_elements = driver.find_elements(By.CSS_SELECTOR, '.Box-sc-15se88d-0.Flex-cw39ct-0.jhymrA, .Box-sc-15se88d-0.Text-sc-18gcpao-0.eXbAnU.drBoOI')

                            for prices in price_elements:
                                pricetext = prices.text
                                match = re.search(r'\$\d[\d,.]*', pricetext)

                                if match:
                                    price = match.group(0).replace('$', '').replace(',', '')
                                    auction_price.append(float(price))
                                    break  # Stop after the first price is found

                            else:
                                auction_price.append(None)

                        except NoSuchElementException:
                            # Handle the case when the elements are not present
                            auction_price.append(None)
                    
                        # Increment the counter
                        counter += 1

                        driver.back()








                    except Exception as err:
                        print("An error occurred: Art could not be scraped", str(err))
                        # Increment the counter
                        counter += 1 #go up the counter anyways

                        driver.back() #hoping the error always happens at the artwork
                        break  # break out of loop , need to go to next batch asap (hoping the xception propogates)


                nextPage = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.Pagination__PageLink-sc-1r2jw01-0.iPdAKY'))
                )

                driver.execute_script("arguments[0].click()", nextPage)
                time.sleep(5) #just wait

            except Exception as err:
                print("An error occurred within the batched for loop. Skipping to next batch...:", str(err))
                break
    except Exception as e:
        print("An error occurred. Proceeding to next batch.:", str(e))
        break

    driver.get(base_url + str(batch_end)) #hopefully will always do this after all the for loop stuff is done
    print("Successfully navigated to page: " + str(batch_end))
    current_page = batch_end + 1



filename = "artsy_data.csv"
data = zip(id, date_created, artist, date_scraped, text_type, text, image_path, image_type, text_author, auction_price)
header = ["ID", "Date Created", "Artist", "Date Scraped", "Text Type", "Text", "Image Path", "Image Type", "Text Author", "Auction Price"]
with open(filename, mode='w', newline='', encoding='utf-8') as file:  # Specify encoding as UTF-8
    writer = csv.writer(file)
    
    # Write the header row
    header = ["ID", "Date Created", "Artist", "Date Scraped", "Text Type", "Text", "Image Path", "Image Type", "Text Author", "Auction Price"]
    writer.writerow(header)
    
    # Write the data rows
    for row in data:
        writer.writerow(row)
    
driver.quit()