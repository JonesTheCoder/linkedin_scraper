import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .objects import Scraper
from .person import Person
import time
import os
import sqlite3
import pandas as pd


conn = sqlite3.connect("linkedIn_Companies.db")
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")

#creating table2 with employee info tied to each company_name
#need to do an if statment here



class CompanySummary(object):
    linkedin_url = None
    name = None
    followers = None

    def __init__(self, linkedin_url = None, name = None, followers = None):
        self.linkedin_url = linkedin_url
        self.name = name
        self.followers = followers

    def __repr__(self):
        if self.followers == None:
            return """ {name} """.format(name = self.name)
        else:
            return """ {name} {followers} """.format(name = self.name, followers = self.followers)

class Company(Scraper):
    linkedin_url = None
    name = None
    about_us =None
    website = None
    headquarters = None
    founded = None
    company_type = None
    company_size = None
    specialties = None
    showcase_pages =[]
    affiliated_companies = []

    def __init__(self, linkedin_url = None, name = None, about_us =None, website = None, headquarters = None, founded = None, company_type = None, company_size = None, specialties = None, showcase_pages =[], affiliated_companies = [], driver = None, scrape = True, get_employees = True, close_on_complete = False):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about_us = about_us
        self.website = website
        self.headquarters = headquarters
        self.founded = founded
        self.company_type = company_type
        self.company_size = company_size
        self.specialties = specialties
        self.showcase_pages = showcase_pages
        self.affiliated_companies = affiliated_companies

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(os.path.dirname(__file__), 'drivers/chromedriver')
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        driver.get(linkedin_url)
        self.driver = driver

        if scrape:
            self.scrape(get_employees=True, close_on_complete=False)

    ### REMOVED def __get_text_under_subtitle(self, elem): ###
    ### REMOVED  __get_text_under_subtitle_by_class(self, driver, class_name): ###


    def scrape(self, get_employees = True, close_on_complete = False):
        if self.is_signed_in():
            self.scrape_logged_in(get_employees = get_employees, close_on_complete = close_on_complete)
        else:
            self.scrape_not_logged_in(get_employees = get_employees, close_on_complete = close_on_complete)

    def __parse_employee__(self, employee_raw):
        driver = self.driver
        #try:
        print("Found them! Let's parse...\n")
        linkedin_url = employee_raw.find_element_by_class_name("search-result__result-link").get_attribute("href")
        name = employee_raw.find_elements_by_class_name("search-result__result-link")[1].text


        # GETTING PROFILE PICTURE AND NAME

        profile_picture_name = employee_raw.find_elements_by_class_name("search-result__image")[0].text
        xCodeURL = ("//div[@aria-label=" + "'" + str(profile_picture_name) + "'" + "]")

        # This locates the correct DOM element using XPATH, the aria-label class, and the employee name
        if profile_picture_name != "":

            print("Company name: " + str(self.name))
            print("Name: " + profile_picture_name + "\n")
            print("LinkedIn_url: " + linkedin_url + "\n")


            attribute = employee_raw.find_element_by_xpath(str(xCodeURL))

            ##### PROFILE PICTURE URL ######
            #this gets the style attribute of the div
            print("Profile Picture URL: ")

            if attribute.get_attribute("style"):
                attribute_2 = attribute.get_attribute("style")
                #just getting url
                profile_picture_url = attribute_2.split(' url("')[1].replace('");', '')
                print(profile_picture_url + "\n")
            #Just incase there is an XPATH issue OR there is no profile picture, it gets set to n/a in database
            else:
                print("Error: couldn't find DOM element...maybe no profile picture")
                profile_picture_url = "n/a"


            # GETS ROLE and LOCATION

            #need to add if Headline, if not headline
            elements = employee_raw.find_elements_by_tag_name("p")

            print("length of elements: " + str(len(elements)))

            if len(elements) == 3:
                print("This is the first element (skip): ")
                print(elements[0].text)
                print("\n")

                print("This is the second element, the location: ")
                location = elements[1].text
                print(location)
                print("\n")


                print("This is the third element, the role: ")
                role = elements[2].text
                #role= role.split(' :("')[1].replace('");', '')
                print(role)
                print("\n")

            else:
                print("This is the first element, the role: ")
                role = elements[0].text
                print(role)
                print("\n")

                print("This is the second element, the location: ")
                location = elements[1].text
                print(location)
                print("\n")

            company_name = self.name
            cursor = cur.execute("SELECT * FROM company_info WHERE company_name=?", (company_name,))
            record = cursor.fetchone()
            company_id = record[0]
            print("and here is company_id: " + str(record[0]))



            print("company id for " + str(self.name) + ":" + str(company_id))

            cur.execute("INSERT INTO employee_info VALUES(NULL, ?, ?, ?, ?, ?);", (company_id, profile_picture_name, profile_picture_url, location, role,))
            conn.commit()




        # PRIVATE ACCOUNT DON'T ADD TO DATABASE
        else:
            print("This employee has no name!")
            print("LinkedIn_url: " + linkedin_url + "\n")
            print("Moving on...")



    def get_employees(self, wait_time=10):

        conn = sqlite3.connect("linkedIn_Companies.db")
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        #### CHECKING SQLITE FOR COMPANY NAME ####
        company_name = self.name
        print("Checking database for company name...")

        cursor = cur.execute("SELECT EXISTS(SELECT 1 FROM company_info WHERE company_name=? LIMIT 1)", (company_name,))
        record = cursor.fetchone()
        if record[0] == 1:
            print("Company_name already exists!... this is it: ")
            print(self.name)

            cursor = cur.execute("SELECT * FROM company_info WHERE company_name=?", (company_name,))
            record = cursor.fetchone()
            company_id = record[0]
            print("Company ID: " + str(record[0]))

            ### todo RETURN INFO ###
            print(pd.read_sql_query("SELECT * FROM employee_info WHERE company_id={0}".format(company_id), conn))
            return

        print("New company found... adding to database now...\n")
        company_name = self.name

        print("Name not in table, adding company to database")
        cur.execute("INSERT INTO company_info VALUES(NULL , ?);", (company_name,))
        conn.commit()

        print("company successfully added... now let's add employees")
        print("Okay getting employees...\n")
        driver = self.driver

        try:
            see_all_employees = driver.find_element_by_xpath('//span[@data-control-name="topcard_see_all_employees"]')

        except:
            print("Sorry, this company has hidden their employee list.")
            return

        driver.get(see_all_employees.find_elements_by_css_selector("*")[0].get_attribute("href"))

        _ = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME, "results-list")))

        total = []
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4));")
        results_list = driver.find_element_by_class_name("results-list")
        results_li = results_list.find_elements_by_tag_name("li")
        for res in results_li:
            self.__parse_employee__(res)


        while self.__find_element_by_class_name__("next"):
            driver.find_element_by_class_name("next").click()
            _ = WebDriverWait(driver, wait_time).until(EC.staleness_of(driver.find_element_by_class_name("search-result")), 'visible')

            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/4));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/3));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*2/3));")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/4));")

            results_list = driver.find_element_by_class_name("results-list")
            results_li = results_list.find_elements_by_tag_name("li")
            for res in results_li:
                _ = WebDriverWait(driver, wait_time).until(EC.visibility_of(res))
                total.append(self.__parse_employee__(res))



    def scrape_logged_in(self, get_employees = True, close_on_complete = False):
        driver = self.driver

        driver.get(self.linkedin_url)

        _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'nav-main__content')))
        _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//h1[@dir="ltr"]')))

        self.name = driver.find_element_by_xpath('//h1[@dir="ltr"]').text


        self.about_us = driver.find_element_by_class_name("org-about-us-organization-description__text").text

        self.specialties = "\n".join(driver.find_element_by_class_name("org-about-company-module__specialities").text.split(", "))
        self.website = driver.find_element_by_class_name("org-about-us-company-module__website").text
        self.headquarters = driver.find_element_by_class_name("org-about-company-module__headquarters").text
        self.industry = driver.find_element_by_class_name("company-industries").text
        self.company_size = driver.find_element_by_class_name("org-about-company-module__company-staff-count-range").text

        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")


        try:
            _ = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'company-list')))
            showcase, affiliated = driver.find_elements_by_class_name("company-list")
            driver.find_element_by_id("org-related-companies-module__show-more-btn").click()

            # get showcase
            for showcase_company in showcase.find_elements_by_class_name("org-company-card"):
                companySummary = CompanySummary(
                        linkedin_url = showcase_company.find_element_by_class_name("company-name-link").get_attribute("href"),
                        name = showcase_company.find_element_by_class_name("company-name-link").text,
                        followers = showcase_company.find_element_by_class_name("company-followers-count").text
                    )
                self.showcase_pages.append(companySummary)

            # affiliated company

            for affiliated_company in showcase.find_elements_by_class_name("org-company-card"):
                companySummary = CompanySummary(
                         linkedin_url = affiliated_company.find_element_by_class_name("company-name-link").get_attribute("href"),
                        name = affiliated_company.find_element_by_class_name("company-name-link").text,
                        followers = affiliated_company.find_element_by_class_name("company-followers-count").text
                        )
                self.affiliated_companies.append(companySummary)

        except:
            pass

        if get_employees:
            self.get_employees()

        driver.get(self.linkedin_url)

        if close_on_complete:
            driver.close()

    #### REMOVED if_not_logged_in_function for now ####

    def __repr__(self):
        return """
{name}

{about_us}

Specialties: {specialties}

Website: {website}
Industry: {industry}
Type: {company_type}
Headquarters: {headquarters}
Company Size: {company_size}
Founded: {founded}

Showcase Pages
{showcase_pages}

Affiliated Companies
{affiliated_companies}
    """.format(
        name = self.name,
        about_us = self.about_us,
        specialties = self.specialties,
        website= self.website,
        industry= self.industry,
        company_type= self.company_type,
        headquarters= self.headquarters,
        company_size= self.company_size,
        founded= self.founded,
        showcase_pages = self.showcase_pages,
        affiliated_companies = self.affiliated_companies
    )
