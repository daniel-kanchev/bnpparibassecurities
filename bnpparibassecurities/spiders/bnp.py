import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bnpparibassecurities.items import Article


class BnpSpider(scrapy.Spider):
    name = 'bnp'
    start_urls = ['https://securities.bnpparibas.com/about-us/news.html']

    def parse(self, response):

        articles = response.xpath('//div[@class="CardItem  "]')
        for article in articles:
            link = article.xpath('.//div[@class="CardItem__text"]/a/@href').get()
            date = article.xpath('.//div[@class="CardItem__date"]/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[text()="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get() or response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        if date:
            date = datetime.strptime(date.strip(), '%d/%m/%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[3:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
