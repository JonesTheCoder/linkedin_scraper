

Initial code/module credit to joeism
github link: https://github.com/joeyism/linkedin_scraper/blob/master/README.md

Notes on additions: I fixed and built upon the get_employees and parse_employee functions
and modified most of the code in the company.py file to achieve intended goal of scraping
certain employee information and then adding it to a database.

Installation for MacOSX:

A. Make a note of where you place folder entitled Util_DE_task, which holds the contents of the program.

B. Make sure to install chromedriver:

1. To install chromedriver using cask:
	- brew tap homebrew/cask
	- brew cask install chromedriver

2. Download the ChromeDriver executable: https://sites.google.com/a/chromium.org/chromedriver/downloads

3. Place the downloaded file wherever you want (I put my in documents)
4. Go back to terminal and run:
						sudo nano /etc/paths
5. Add this path at the bottom of the file, with your username where it says [NAME]:
						/Users/[NAME]/Documents/
6. Close the file and save changes.


C. Open a Jupyter Notebook

1. Open a terminal and cd into Util_DE_task, then type "jupyter notebook"
2. This will open the ipython notebook titled "UTIL_DE_2", where you can follow the directions
	to use the scraping program.


	NOTES ON TODO/IMPROVEMENTS

	- formatting problem when returning pandas_formatted_sql tables.
	- lots of cleaning up, optimization
	- issue when user is not prime and gets close to view-limit.
	- Returning data table after adding new company/employees needs to be added so you don't have to go back and search for company_id
	- add ability to run in terminal
	- informational issues if employee is private/has "LinkedIn Member" name.
	- once company is added, program doesn't add new employees. This needs to be fixed so the program looks for new employees and adds them.
	- add more exceptions/error codes so program is less likely to break.
	- add credentials so user doesn't have to login every time (security issues?)

	NOTES ON PROCESS

	- I decided to have 2 tables, company_info and employee_info, because I thought this would increase scalability and long-term
	functionality of program. In the future you could save more data about the company (industry, size, market value, areas of investment, etc)
	and optimize searches that way.
