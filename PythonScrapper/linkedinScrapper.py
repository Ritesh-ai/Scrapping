'''-SCRAPER FOR THE LINKEDIN PROFILES OF THE DATASCIENTIST -'''
try:
    # MAKE ALL THE MODULES AVAILABLE
    import selenium
    from selenium import webdriver
    import time
    from selenium.webdriver.common.keys import Keys
    import csv
    import sys
    #reload(sys)
    #sys.setdefaultencoding('utf8')

except:
    # PLEASE IMPORT THE MODULES FIRST
    print("Please import all the modules  successfully")

# MAIN SCRAPER TO SCRAP THE PROFILES OF THE DIFFERENT CATEGORIES
class LinkedinScraper():
    #CALL THE INITIAL FUNCTION TO SCRAPER
    def __init__(self,username,password,category):

        # CALL THE WEBDRIVER TO OPEN THE BROWSER
        self.driver= webdriver.Chrome("C:\\Users\\Ritesh\\PycharmProjects\\MyPro\\drivers\\"
                                      "\\chromedriver.exe")
        print("driver :",self.driver)

        # GET THE LINKEDIN PROFILE PAGE
        self.driver.get("https://in.linkedin.com/")

        # MAKE THE VARIABLE AS GLOBLE AND CALL THE MAIN FUNCTION TO HANDLE THE CLASSES
        self.username=username
        self.password=password

        # self.category=category
        self.main(category)


    '''Make login for the linkedin account'''
    def login(self):
        #ENTER THE EMAIL OF ACCOUNT
        email=self.driver.find_element_by_class_name("login-email").send_keys(self.username)
        time.sleep(2)
        #PASSWORD FOR THE ACCOUNT
        password=self.driver.find_element_by_class_name("login-password").send_keys(self.password)
        time.sleep(2)
        # PRESS ENTER TO MAKE ENTER
        self.driver.find_element_by_id("login-submit").click()


    '''SEARCH THE TOTAL PAGES PROFILE HERE AND RETURENS THE URLS FOR THE PROFILE '''

    def search_profiles(self,category="datascientist"):

        # SEARCH THE CATEGORY
        self.driver.find_element_by_xpath('//*[@id="ember30"]/input').send_keys(category)
        self.driver.find_element_by_xpath('//*[@id="ember30"]/input').send_keys(Keys.RETURN)
        time.sleep(4)

        # FIND TOTAL PAGES FOR THE PROFILE
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # page_urls=[]

        # DEFINE A CONTAINER FOR THE PROFILE LINKS
        links=[]

        # MAKE ITERATIONS THROUGH THE PAGES
        for page in range(1,11):
            current_url=self.driver.current_url+"&page=%s"%page
            # page_urls.append(current_url)
            print("current_url : ",current_url)

            #FIND THE CURRENT PAGE
            self.driver.get(current_url)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            data=self.driver.find_elements_by_xpath('//*[@data-control-name="search_srp_result"]')
            print("data :",data)

            # COLLECT THE PROFILE LINKS OF SPECIFIC CATEGORY
            for y in data:
                w=y.get_attribute("href")
                if(w not in links):
                    links.append(w)
                else:
                    pass
                print("profile :",w)
            # break

        # RETURN THE UNIQUE LINKS FROM HERE
        return links


    '''GET THE PROFILE DETAILS WITH THE FUNCTION BELOW'''
    def get_profile_details(self,links):
        # MAKE ALL THE LINKS AVAILABLE
        complete_profiles=[]
        for link in links:
            profile_details={}

            self.driver.get(link)
            #FIND NAME OF USER
            try :
                name = self.driver.find_element_by_xpath('//div[@class="pv-top-card-v2-section__info mr5"]//h1').text
                profile_details["name"]=name
            except :
                name=None
                profile_details["name"]=name

            # GET THE USER PROFILE
            try:
                profile = self.driver.find_element_by_xpath('//div[@class="pv-top-card-v2-section__info mr5"]//h2').text
                profile_details["profile"]=profile

            except:
                profile=None
                profile_details["profile"]=profile

            # GET THE CITY FROM WHERE USER BELONGS"
            try:
                city = self.driver.find_element_by_xpath('//div[@class="pv-top-card-v2-section__info mr5"]//h3').text
                profile_details["city"]=city

            except:
                city=None
                profile_details["city"]=city


            print("name :", name, "profile :", profile, "city :", city)
            print("profile details :",profile_details)
            # MAKE A SCROLLER FOR USER PROFILE
            self.driver.execute_script("window.scrollTo(0, 1500);")
            time.sleep(3)
            #GET THE EDUCATION DETAILS OF THE USER FROM HERE
            education=self.driver.find_elements_by_xpath('//section[@id="experience-section"]/ul//li')

            education_list=[]
            for edu in education:
                details={}
                print("edu  ==> ",edu.text.split('\n'))
                edu=edu.text.split('\n')

                details["desiganation"] =edu[0]

                # COLLECT COMPANY DETAILS
                if ('Company Name' in edu):
                    company = edu.index("Company Name")
                    details["company"] = (edu[company + 1])
                else:
                    pass
                # COLLECT DATE EMPLOYED DETAILS
                if ('Dates Employed' in edu):
                    DatesEmployed = edu.index("Dates Employed")
                    details["DatesEmployed"] = (edu[DatesEmployed + 1])
                else:
                    pass
                # COLLECT TOTAL DURATION DETAILS
                if ('Employment Duration' in edu):
                    EmploymentDuration = edu.index('Employment Duration')
                    details["EmploymentDuration"] = (edu[EmploymentDuration + 1])
                else:
                    pass
                # COLLECT LOCATION DETAILS
                if ('Location' in edu):
                    Location = edu.index('Location')
                    details['Location'] = (edu[Location + 1])

                else:pass
                education_list.append(details)

                print("details : ",details)

            profile_details["education_details"]=education_list

            print("profile  : ==> ",profile_details)
            complete_profiles.append(profile_details)

        print("complete profile : ==> ",complete_profiles)
        return complete_profiles


    '''WRITE INTO CSV FILE WITH THE FOLLOWING FUNCTION'''
    def csv_writter(self,data):
        # field names
        fields = ['name', 'profile', 'city', 'education_details']
        # name of csv file
        filename = "linkedin_profile.csv"

        # writing to csv file
        with open(filename, 'w') as csvfile:
            # creating a csv dict writer object
            writer = csv.DictWriter(csvfile, fieldnames=fields)

            # writing headers (field names)
            writer.writeheader()

            # writing data rows
            writer.writerows(data)



    '''MAIN FUNCTION TO HANDLE THE OTHER FUNCTIONS'''
    def main(self,category):
        #MAKE THE USER LOGIN FROM HERE
        self.login()

        #SCRAP ALL THE PAGES PROFILE LINKS FOR THE INFORMATION
        profile_links=self.search_profiles(category=category)

        #GET DETAILS OF EACH OF THE PROFILE
        data=self.get_profile_details(profile_links)

        file=self.csv_writter(data)


'''CALL THE CLASSES '''

username=str(input("please Enter the user name for the linked profile : "))
password=str(input("Please Enter The Password For Your linkedin profile : "))
category=str(input("Please Enter The category to be searched : "))
print("username :",username,"password :",password ,"category : ",category)

'''call the crawler'''
#call_scraper=LinkedinScraper(username=username.strip(),password=password.strip(),category=category.strip())
call_scraper=LinkedinScraper(username=username,password=password,category=category)


