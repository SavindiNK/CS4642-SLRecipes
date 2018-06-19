import scrapy

class RecipesSpider(scrapy.Spider):
	name = "recipes"

	def start_requests(self):
		urls = [
			"https://www.yamu.lk/recipe",
		]
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		for link in response.css('a.front-group-item.item::attr(href)').extract() :
			yield response.follow(link, self.parse_recipe)

		next_page = response.css('ul.pagination a[rel="next"]::attr(href)').extract_first()
		if next_page is not None:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse)

	def parse_recipe(self, response):
		title = response.css('div.place-title-box h1::text').extract_first().strip()
		overview = response.css('div.place-title-box ul.list-inline li::text').extract_first()
		if overview is not None:
			overview = overview.strip()

		tags = response.css('div.place-title-box h4 span.label.label-success::text').extract()

		try:
			difficulty = int(tags[0].split(" ")[-1].split("/")[0])
		except:
			difficulty = None

		try:
			serving = int(tags[1].split(" ")[-1])
		except:
			serving = None

		try:
			time = tags[2].split(" ")[-1]
		except:
			time = None

		author_url = response.css('div.author-body a[rel="author"]::attr(href)').extract_first()
		author_username = response.css('div.author-body a[rel="author"] span[itemprop="author"]::text').extract_first().strip()

		youtube_url = response.css('div.embed-responsive iframe.embed-responsive-item::attr(src)').extract_first()

		ingredients_and_equipment = response.css('div.col-md-6 ul')
		try:
			ingredients_quantity = [q[q.index('(')+1:q.index(')')] for q in ingredients_and_equipment[0].css('li b[ng-bind-html]').extract()]
			ingredients_conjunction = [c.strip() for c in ingredients_and_equipment[0].css('li b::text').extract()]
			ingredients_name = [n.strip() for n in ingredients_and_equipment[0].css('li::text').extract()]
			ingredients_name = list(filter(('').__ne__, ingredients_name))
			ingredients = []
			for i in range(len(ingredients_name)):
				ingredients.append(ingredients_quantity[i]+" "+ingredients_conjunction[i]+" "+ingredients_name[i])
		except:
			ingredients = None

		try:
			equipment = [e.strip() for e in ingredients_and_equipment[1].css('li::text').extract()]
		except:
			equipment = None

		try:
			method = [step.strip() for step in response.css('li.rcp-step::text').extract()]
		except:
			method = None

		yield {
			'title':title,
			'overview':overview,
			'difficulty':difficulty,
			'serving':serving,
			'time':time,
			'author_url':author_url,
			'author_username':author_username,
			'youtube_url':youtube_url,
			'ingredients':ingredients,
			'equipment':equipment,
			'method':method
		}