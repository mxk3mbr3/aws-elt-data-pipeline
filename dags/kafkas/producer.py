# Web scrape variables

import requests
from bs4 import BeautifulSoup
import random
from random import randint
from time import sleep
import math
import json
import traceback
from concurrent.futures import ThreadPoolExecutor

# Kafka variables
from kafka import KafkaProducer

# Kafka variables
topic = "malta_activities"

producer = KafkaProducer(
    value_serializer=lambda msg: json.dumps(msg).encode(
        "utf-8"
    ),  # we serialize our data to json for efficent transfer
    bootstrap_servers=["kafka:9092"],
    api_version=(1, 4, 6),
)

# Region and Country to extract data from
country = "Malta"

# List of user-agents to rotate
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
]
# User Agent request header - using random to rotate user agents
headers = {"User-Agent": random.choice(user_agents)}

# Number of items per page - Default is 30
noipp = 30

# Number of reviews per page - Default is 10
norpp = 10


# Getting total number of items (activities)
def total_number_activities():
    tnoi_url = "https://www.tripadvisor.com/Attractions-g190320-Activities-c42-Island_of_Malta.html"

    try:
        res_tnoi = requests.get(
            tnoi_url, headers=headers, timeout=6
        )  # proxies=proxies,
        soup_tnoi = BeautifulSoup(res_tnoi.text, "lxml")
        tnoi = int(
            soup_tnoi.find(name="div", attrs={"class": "Ci"})
            .text.split()[-1]
            .replace(",", "")
        )
    except Exception:
        print("The error is:", traceback.format_exc())

    return tnoi


# Scraping function
def scraper(page):
    url_list_activities = f"https://www.tripadvisor.com/Attractions-g190320-Activities-c42-oa{noipp*page}-Island_of_Malta.html"

    try:
        res_list_activities = requests.get(
            url_list_activities, headers=headers, timeout=6
        )  # , proxies=proxies
        soup_list_activities = BeautifulSoup(res_list_activities.text, "lxml")
        activities_urls = soup_list_activities.find_all(
            name="div", attrs={"class": "alPVI eNNhq PgLKC tnGGX"}
        )
        # For loop to get variables required for each url
        for href_url in activities_urls:
            # Activity url
            activity_url = "https://www.tripadvisor.com" + href_url.a["href"]
            try:
                res_activity = requests.get(
                    activity_url, headers=headers, timeout=6
                )  # , proxies=proxies
                soup_activity = BeautifulSoup(res_activity.text, "lxml")

                ########## Variables relating to activity ##########

                # Activity name
                activitiy_name = soup_activity.select_one(
                    "h1.biGQs._P.fiohW.ncFvv.EVnyE"
                ).text
                # Activity organizer
                activitiy_organizer = soup_activity.select_one(
                    "span.biGQs._P.XWJSj.Wb div"
                ).text
                # Activity price (per person or per group)
                activity_price = soup_activity.select_one(
                    "div.biGQs._P.fiohW.avBIb.uuBRH"
                ).text
                # Activity max number of people
                activity_max_group_no = soup_activity.select(
                    "span.biGQs._P.pZUbB.egaXP.KxBGd"
                )[0].text
                # Activity duration
                activity_duration = soup_activity.select(
                    "span.biGQs._P.pZUbB.egaXP.KxBGd"
                )[1].text

                # Randomly changing the sleeping amount
                sleep(randint(1, 4))

                ########## Variables relating to reviews ##########

                # Getting total number of reviews - There are 3 cases
                # 1. There are more than 10 reviews
                # 2. There are 10 or less reviews
                # 3. There are no reviews

                # Getting total number of reviews
                total_reviews_check = int(
                    soup_activity.find(
                        name="span",
                        attrs={
                            "class": "biGQs _P pZUbB KxBGd",
                        },
                    )
                    .text.split()[0]
                    .replace(",", "")
                )

                # 3. There are no reviews
                if total_reviews_check == 0:
                    # Setting equal to norpp to access for loop and then set values to None
                    tnor = norpp

                # 2. There are 10 or less reviews
                if len(soup_activity.select(".Ci")) == 0 and total_reviews_check != 0:
                    # Setting equal to norpp to access 1st (and only) page of reviews
                    tnor = norpp

                # 1. There are more than 10 reviews
                if len(soup_activity.select(".Ci")) != 0 and total_reviews_check != 0:
                    # tnor = int(soup_reviews.select(".Ci")[-1].text.split()[-1].replace(",", ""))
                    tnor = total_reviews_check

                # For loop to get review variables for each review for the specific activity
                for review_page in range(math.ceil(tnor / norpp)):
                    # To get the URL for reviews, first split the url where you have "-"
                    split_url = activity_url.split("-")
                    # insert f"or{review_page*norpp}" at the 3rd element as per URL structure
                    split_url.insert(3, f"or{review_page*norpp}")
                    # join split elements to form reviews_url
                    reviews_url = "-".join(split_url)

                    try:
                        if total_reviews_check != 0:
                            r_reviews = requests.get(
                                reviews_url,
                                headers=headers,
                                timeout=6,
                            )  # proxies=proxies,
                            r_soup_reviews = BeautifulSoup(r_reviews.text, "lxml")

                            # Reviewer username
                            reviewer_usernames = r_soup_reviews.select(
                                "div.zpDvc.Zb span.biGQs._P.fiohW.fOtGX a"
                            )

                            # Reviewer rating
                            reviewer_ratings = r_soup_reviews.find_all(
                                name="svg",
                                attrs={
                                    "class": "UctUV d H0",
                                },
                            )

                            # Review date
                            review_dates = r_soup_reviews.find_all(
                                name="div",
                                attrs={
                                    "class": "biGQs _P pZUbB ncFvv osNWb",
                                },
                            )

                            for username, rating, date_review in zip(
                                reviewer_usernames,
                                reviewer_ratings,
                                review_dates,
                            ):
                                reviewer_username = username.text
                                reviewer_rating = rating.get("aria-label")
                                review_date = date_review.text

                                # Final data in json format - With reviews case
                                extracted_data = {
                                    "Activitiy_Name": activitiy_name,
                                    "Activitiy_Organizer": activitiy_organizer,
                                    "Activitiy_Duration": activity_duration,
                                    "Activitiy_Price": activity_price,
                                    "Activitiy_Max_Number_Group": activity_max_group_no,
                                    "Country": country,
                                    "Reviews": {
                                        "Reviewer_Username": reviewer_username,
                                        "Reviewer_Rating": reviewer_rating,
                                        "Review_Date": review_date,
                                    },
                                }

                                # Send to consumer
                                producer.send(topic=topic, value=extracted_data)

                                # Randomly changing the sleeping amount
                                sleep(randint(1, 4))

                        else:
                            reviewer_username = None
                            reviewer_rating = None
                            review_date = None

                            # Final data in json format - No reviews case
                            extracted_data = {
                                "Activitiy_Name": activitiy_name,
                                "Activitiy_Organizer": activitiy_organizer,
                                "Activitiy_Duration": activity_duration,
                                "Activitiy_Price": activity_price,
                                "Activitiy_Max_Number_Group": activity_max_group_no,
                                "Country": country,
                                "Reviews": {
                                    "Reviewer_Username": reviewer_username,
                                    "Reviewer_Rating": reviewer_rating,
                                    "Review_Date": review_date,
                                },
                            }

                            # Send to consumer
                            producer.send(topic=topic, value=extracted_data)

                            # Randomly changing the sleeping amount
                            sleep(randint(1, 4))

                        print(extracted_data)

                    except Exception:
                        print("The error is:", traceback.format_exc())
            except:
                print("The error is:", traceback.format_exc())

    except Exception:
        print("The error is:", traceback.format_exc())


# Use multithreading with kafka producer
def produce_activities():
    tnoi = total_number_activities()
    pages = set(range(math.floor(tnoi / noipp)))
    with ThreadPoolExecutor() as executor:
        executor.map(scraper, pages)
