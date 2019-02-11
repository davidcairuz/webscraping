import requests
from bs4 import BeautifulSoup as soup

class KabumBot:

	def get_categories(self):

		# going to homepage
		mess = requests.get('https://www.kabum.com.br/').text
		html = soup(mess, "html.parser")

		# finding where all categories are
		categories_container = html.findAll("div", {"class":"texto_categoria"})

		# retrieving categories
		categories = {}
		for block in categories_container:
			for categorie in block.findAll('a'):
				categories[categorie.text] = categorie['href']

		return categories

	def get_products_by_url(self, categorie, base_url):
		products = []
		
		# assuming 1000 is the maximum number of pages (could be while True)
		for page in range(1, 1000):
			
			# going to the i-th page
			url = base_url + '?ordem=5&limite=100&pagina={}&string='.format(page)
			mess = requests.get(url).text
			html = soup(mess, "html.parser")

			# finding where all products are
			products_container = html.findAll("div", {"class":"listagem-box"})
			if len(products_container) == 0:
				break

			# retrieving products title and price
			products_title = [product.div.span.text for product in products_container if product != None]
			products_price = [product.find("div", {"class":"listagem-preco"}) for product in products_container]
			products_price = [product.text if product is not None else "-" for product in products_price]

			# adding current page products to 'products' list
			for i in range(len(products_title)):
				row = [products_title[i], products_price[i]]
				products.append(row)

		# writing all products to file
		with open('products.csv', 'a') as f:
			for product in products:

				# cleaning title and price
				product[0] = product[0].replace('\x96', '').replace('\x94', '').replace(',', ' -')
				product[1] = product[1].replace('R$ ', '').replace('.', '')
				f.write("{};{};{}\n".format(categorie, product[0], product[1]))

if __name__ == '__main__':
	
	# creating instance of the scraper
	bot = KabumBot()

	# reading all categories
	categories = bot.get_categories()

	# retrieving all products of each category
	for categorie, url in categories.items():
		bot.get_products_by_url(categorie, url)
