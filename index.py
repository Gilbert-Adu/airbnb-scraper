import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

#this is a helper function that returns the average rating of a listing
def ratings_processor(item):
    
    if len(item) == 0:
        return [0,0]
    if len(item.split(" ")) <= 1:
        return [0,0]
    return item.split(" ")

#this is a helper function that returns the number of reviews a listing has received
def brackets_helper(item):
    item = str(item)
    if len(item) == 0:
        return [0,0]
    return item[1:len(item)-1]

#this is a helper that extracts the number of beds a listing has
def beds_processor(item):
    if " " in item:
        space_pos = item.index(" ")
        return item[:space_pos]
    else:
        return 0

#this is a helper function that extracts the cost of a listing per night from the main page
def cost_processor(item):

    space_pos = item.index(" ")
    return item[:space_pos]

#this function scrapes the text from a web page
def scrape_page(page_url):
    res = requests.get(page_url)
    content = res.content
    soup = BeautifulSoup(content, 'html.parser')

    return soup


#this is a helper that helps in extracting the cleaning fees and service fees
def details_processor(detail):
    return detail.replace("Show price breakdown", " ")


#this function extracts more details about a listing such as cleaning fees and service fees
def extract_detail_page(href):
    
    url = "https://www.airbnb.com" + href
    res = []

    driver = webdriver.Chrome()
    driver.get(url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    details = soup.find_all('div', {'class':'_tr4owt'})


    for detail in details:
        res.append(details_processor(detail.text))
    driver.quit()
    return res


#the preferred name of your csv file
csv_file_path = "ithaca.csv"

#this function writes data to an already created csv file 
def write_to_csv(csv_file_path, data):

    with open(csv_file_path, 'a', newline='') as csv_file:

        fieldnames = ["title", "description", "num_beds", "dates", "cost_per_night", "average_rating", "num_of_reviews", "cleaning_fee", "airbnb_service_fee"]
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            csv_writer.writeheader()
        csv_writer.writerows(data)


#this is a helper function to extract the dollar amount
def process_fees(item):
    dollar = item.index('$')
    return item[dollar:]


#this function extracts data from the frontpage of a particular city
def extract_listing(page_url):

    """
    This is the format of what this function returns:

    [title, desc, num_beds, date, cost, rating, num_reviews, details]
    """
    
    page_soup = scrape_page(page_url)
    listings = page_soup.findAll("div", {"class": "c4mnd7m atm_9s_11p5wf0 atm_dz_1osqo2v dir dir-ltr"})

    data = []

    for listing in listings:
        if len(listing) != 0:
            temp = {}
            
            title = listing.findAll('div', attrs={'data-testid': 'listing-card-title'})[0].get_text()
            name = listing.findAll('span', attrs={'data-testid': 'listing-card-name'})[0].get_text()
            beds = listing.findAll('div', attrs={'data-testid': 'listing-card-subtitle'})[1].get_text()
            dates = listing.findAll('div', attrs={'data-testid': 'listing-card-subtitle'})[2].get_text()
            pre_reviews = listing.findAll('span', {'class': 'r1dxllyb atm_7l_18pqv07 atm_cp_1ts48j8 dir dir-ltr'})
            reviews = ""
            if pre_reviews == [] or pre_reviews[0] == 'No reviews yet':
                reviews = ""
            else:
                reviews = pre_reviews[0].get_text()

            
            cost = listing.findAll('span', {'class': 'a8jt5op atm_3f_idpfg4 atm_7h_hxbz6r atm_7i_ysn8ba atm_e2_t94yts atm_ks_zryt35 atm_l8_idpfg4 atm_mk_stnw88 atm_vv_1q9ccgz atm_vy_t94yts dir dir-ltr'})[0].get_text()
            detail_href = listing.find('a')

            """
            
            """
            temp["title"] = title
            temp["description"] = name
            temp["num_beds"]= beds_processor(beds)
            temp["dates"] = dates
            temp["cost_per_night"] = cost_processor(cost)
            temp["average_rating"] = ratings_processor(reviews)[0]
            temp["num_of_reviews"] = brackets_helper(ratings_processor(reviews)[1])
            the_detail = extract_detail_page(detail_href['href'])
            if len(the_detail) == 3:
                the_detail = the_detail[1:]
                temp["cleaning_fee"] = process_fees(the_detail[0])
                temp["airbnb_service_fee"] = process_fees(the_detail[1])

            elif len(the_detail) == 4:
                the_detail = the_detail[2:]
                temp["cleaning_fee"] = process_fees(the_detail[0])
                temp["airbnb_service_fee"] = process_fees(the_detail[1])

            else:
                temp["cleaning_fee"] = "0"
                temp["airbnb_service_fee"] = "0"
    
            data.append(temp)

    write_to_csv(csv_file_path, data)


#this function gets the next pages that contain listings for a particular city
def get_next_page(url):
    soup = scrape_page(url)

    limit = 18
    next_link = soup.findAll('a', {'class': 'l1ovpqvx atm_1y33qqm_1ggndnn_10saat9 atm_17zvjtw_zk357r_10saat9 atm_w3cb4q_il40rs_10saat9 c1ackr0h atm_c8_fkimz8 atm_g3_11yl58k atm_fr_4ym3tx atm_cs_qo5vgd atm_9s_1txwivl atm_h_1h6ojuz atm_fc_1h6ojuz atm_bb_idpfg4 atm_3f_glywfm atm_5j_1ssbidh atm_26_1j28jx2 atm_7l_18pqv07 atm_vy_1vi7ecw atm_e2_1vi7ecw atm_gi_idpfg4 atm_gz_logulu atm_h0_logulu atm_l8_idpfg4 atm_uc_1dtz4sb atm_kd_glywfm atm_uc_glywfm__p88qr9 atm_26_1nh1gcj_1nos8r_uv4tnr atm_tr_kv3y6q_csw3t1 atm_26_1nh1gcj_csw3t1 atm_9j_73adwj_1o5j5ji atm_3f_glywfm_jo46a5 atm_l8_idpfg4_jo46a5 atm_gi_idpfg4_jo46a5 atm_3f_glywfm_1icshfk atm_kd_glywfm_19774hq atm_uc_x37zl0_1w3cfyq atm_26_1nh1gcj_1w3cfyq atm_70_1o9v3ru_1w3cfyq atm_uc_glywfm_1w3cfyq_p88qr9 atm_uc_x37zl0_18zk5v0 atm_26_1nh1gcj_18zk5v0 atm_70_1o9v3ru_18zk5v0 atm_uc_glywfm_18zk5v0_p88qr9 dir dir-ltr'})
    total_num = int(next_link[len(next_link)-1].get_text())
    all_links = []
    for i in range(1, total_num + 1):
        offset = limit * i
        pagination = url + f'&items_offset={offset}'
        all_links.append(pagination)

    return all_links
    



#a list of cities with shorthand of their states
#add more cities in the format eg ["New York", "NY"]
cities = [["Ithaca", "NY"]]

#this function creates links to the airbnb page of a particular city
def process_cities_links(cities):
    res = []
    for city in cities:
        link = "https://www.airbnb.com/s/" + city[0] +"--" + city[1] + "--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-02-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&date_picker_type=flexible_dates&flexible_trip_dates%5B%5D=april&flexible_trip_dates%5B%5D=august&flexible_trip_dates%5B%5D=december&flexible_trip_dates%5B%5D=february&flexible_trip_dates%5B%5D=january&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=march&flexible_trip_dates%5B%5D=may&flexible_trip_dates%5B%5D=november&flexible_trip_dates%5B%5D=october&flexible_trip_dates%5B%5D=september&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=5&search_mode=flex_destinations_search"
        res.append(link)
    return res


#function to run the entire program
def run(cities):
    urls = process_cities_links(cities)
    for url in urls:
        extract_listing(url)
        the_next_links = get_next_page(url)
        for link in the_next_links:
            extract_listing(link)

run(cities)

"""
good link format

https://www.airbnb.com/s/Rochester--New-York--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-02-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&date_picker_type=flexible_dates&flexible_trip_dates%5B%5D=april&flexible_trip_dates%5B%5D=august&flexible_trip_dates%5B%5D=december&flexible_trip_dates%5B%5D=february&flexible_trip_dates%5B%5D=january&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=march&flexible_trip_dates%5B%5D=may&flexible_trip_dates%5B%5D=november&flexible_trip_dates%5B%5D=october&flexible_trip_dates%5B%5D=september&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=5&search_mode=flex_destinations_search
https://www.airbnb.com/s/Rochester--New-York--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-02-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&date_picker_type=flexible_dates&flexible_trip_dates%5B%5D=april&flexible_trip_dates%5B%5D=august&flexible_trip_dates%5B%5D=december&flexible_trip_dates%5B%5D=february&flexible_trip_dates%5B%5D=january&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=march&flexible_trip_dates%5B%5D=may&flexible_trip_dates%5B%5D=november&flexible_trip_dates%5B%5D=october&flexible_trip_dates%5B%5D=september&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=5&query=Rochester%2C%20New%20York%2C%20United%20States&place_id=ChIJU7MUlgWz1okRHuYlQfwfAFo&federated_search_session_id=e5d2334f-ee37-419e-8be0-6e6aff49304c&pagination_search=true&cursor=eyJzZWN0aW9uX29mZnNldCI6MiwiaXRlbXNfb2Zmc2V0IjoxOCwidmVyc2lvbiI6MX0%3D

https://www.airbnb.com/s/Salt Lake City--UT--United-States/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-02-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&date_picker_type=flexible_dates&flexible_trip_dates%5B%5D=april&flexible_trip_dates%5B%5D=august&flexible_trip_dates%5B%5D=december&flexible_trip_dates%5B%5D=february&flexible_trip_dates%5B%5D=january&flexible_trip_dates%5B%5D=july&flexible_trip_dates%5B%5D=june&flexible_trip_dates%5B%5D=march&flexible_trip_dates%5B%5D=may&flexible_trip_dates%5B%5D=november&flexible_trip_dates%5B%5D=october&flexible_trip_dates%5B%5D=september&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=5&search_mode=flex_destinations_search

"""


