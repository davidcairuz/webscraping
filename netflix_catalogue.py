from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as soup
from selenium import webdriver
import requests
import time

class NetflixScraper:

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.driver = webdriver.Firefox(executable_path="C:\geckodriver.exe")

	def close_browser(self):
		driver = self.driver
		driver.close()

	def login(self):
		driver = self.driver
		driver.get("https://www.netflix.com/br/")
		time.sleep(1)

		login_button = driver.find_element_by_xpath("//a[@class='authLinks signupBasicHeader']")
		login_button.click()
		time.sleep(1)

		username_box = driver.find_element_by_xpath("//input[@id='id_userLoginId']")
		username_box.send_keys(self.username)

		password_box = driver.find_element_by_xpath("//input[@id='id_password']")
		password_box.send_keys(self.password)

		password_box.send_keys(Keys.RETURN)
		time.sleep(6)

		select_user = driver.find_element_by_xpath("//div[@class='profile-icon']")
		select_user.click()

	def get_ids(self, categorie):

		driver = self.driver
		url = "https://www.netflix.com/browse/genre/83?so=az" if categorie == 'Series' else "https://www.netflix.com/browse/genre/34399?so=az"
		driver.get(url)
		time.sleep(3)

		get_height = lambda:driver.execute_script("return window.pageYOffset;")
		
		last_height = -5
		current_height = get_height()

		while(current_height != last_height):
			last_height = current_height
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(2)
			current_height = get_height()

		urls = driver.find_elements_by_xpath("//div[@class='slider-item slider-item-1']//a")

		title_ids = []
		for url in urls:
			try:
				url = url.get_attribute('href')
				start_point = url.find('/watch/') + 7
				end_point = url.find('?', start_point)
				title_ids.append(url[start_point:end_point])
			except Exception as e:
				print(e)
				continue

		return title_ids

	
	def get_title_info(self, title_id, categorie):

		url = "https://www.netflix.com/br/title/{}".format(title_id)
		response_text = requests.get(url).text

		html = soup(response_text, "html.parser")
		information_block = html.find("div", {'id':'appMountPoint'})
		
		name = html.h1.text
		year = information_block.find('span', {'class':'year'}).text.replace(' ', '')
		age = information_block.find('span', {'class':'maturity-number'}).text.replace(' ', '')
		genre_list = information_block.find('span', {'class':'genre-list'}).text.replace('\xa0', '')
		duration = information_block.find('span', {'class':'duration'}).text
		
		try:
			creators = information_block.find('span', {'class':'creator-name'}).text.replace('\xa0', '')
		except Exception:
			creators = 'Not found'

		try:
			directors = information_block.find('span', {'class':'director-name more-details-content'}).text.replace('\xa0', '')
		except Exception:
			directors = 'Not found'

		try:
			actors = information_block.find('span', {'class':'actors-list'}).text.replace('\xa0', '')
		except Exception:
			actors = 'Not found'

		synopsis = information_block.find('p', {'class':'synopsis'}).text

		row = [categorie, name, duration, year, actors, creators, directors, genre_list, age, synopsis]
		return row


username = 'EMAIL'
password = 'PASSWORD'

bot = NetflixScraper(username, password)
bot.login()
series_ids = bot.get_ids('Series')
movies_ids = bot.get_ids('Movies')
bot.close_browser()

title_infos = []  # list of titles with name, year, duration, episodes etc.

series_remaining = len(series_ids)
movies_remaining = len(movies_ids)

for title_id in series_ids:
	info = bot.get_title_info(title_id, 'Series')
	title_infos.append(info)
	print("{} done. {} series remaining...".format(info[1], series_remaining))
	series_remaining -= 1

for title_id in movies_ids:
	info = bot.get_title_info(title_id, 'Movies')
	title_infos.append(info)
	print("{} done. {} movies remaining...".format(info[1], movies_remaining))
	movies_remaining -= 1

with open ('netflix_catalogue.csv', 'a', encoding="utf-8") as file:
	
	file.write("Categorie;Name;Duration;Year;Starring;Creators;Directors;Genres;Maturity;Synopsis\n")
	
	for title in title_infos:
		to_write = ";".join(title) + '\n'
		print(to_write)
		file.write(to_write)