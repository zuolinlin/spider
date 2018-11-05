# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider


class TestSpider(CrawlSpider):
    """
    Example searches:
    check for exact word like "crosswords": crosswords
    three letter word, ending in "r": --r
    six letter word, first two letters "pu", last letter "e": pu---e
    ten letter word, middle two letters "sw": ----sw----
    words containing the sequence "sswo" anywhere: *sswo*
    words of any length starting with "cross": cross*
    words of any length ending with "zzle": *zzle
    word starts with "a", ends with "z": a*z
    starts with "b", "c" somewhere within, ends with "d": b*c*d
    words starting with "ab" that don't contain an "e" or "o": ab* ^eo
    Use a hyphen (dash) to give the location of a missing letter: w-rd or -are
    Use an asterisk (star) for any number of unknown letters: lett* or *gry or ar*ct
    Exclude words containing the letters that follow a caret (hat): ma-e ^kt
    Or enter a few letters (without hyphens or asterisks) to see if they make any words.
    """
    name = "test"
    allowed_domains = ["morewords.com"]

    # def parse(self, response):
    #     items = response.xpath("/html/body/table[2]/tr[4]/td/table/tr[position()>1]")
    #     words = []
    #     for item in items:
    #         words.append(item.xpath("td[2]/text()").extract_first())
    #     print(words)

    def start_requests(self):
        form_data = {
            "w": "a-----",
            "submit": "Search for words"
        }
        yield scrapy.FormRequest(
            url="https://www.morewords.com/",
            formdata=form_data,
            callback=self.parse
        )

    def parse(self, response):
        items = response.xpath("/html/body/div/big/ul/li")
        words = []
        for item in items:
            words.append(item.xpath("a/text()").extract_first())
        print(words)
