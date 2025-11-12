import os
from urllib.parse import urlparse
import scrapy
from scrapy.crawler import CrawlerProcess


DEFAULT_OUTPUT_DIR = os.path.join("data", "jobs")


class FullSiteSpider(scrapy.Spider):
    name = "full_site"

    def __init__(self, start_url, output_dir=DEFAULT_OUTPUT_DIR, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parsed = urlparse(start_url)
        self.start_urls = [start_url.rstrip("/")]
        self.allowed_domains = [parsed.netloc]
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.output_dir = output_dir

    def parse(self, response):
        # Determine save path
        rel_path = response.url.replace(self.base_url, "").rstrip("/")
        if rel_path == "":
            rel_path = "/"
        save_path = os.path.join(self.output_dir, rel_path.lstrip("/"), "index.html")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        self.logger.info(f"Saving: {save_path}")

        with open(save_path, "wb") as f:
            f.write(response.body)

        # Follow internal links
        for href in response.css("a::attr(href)").getall():
            url = response.urljoin(href)
            if url.startswith(self.base_url):
                yield scrapy.Request(url, callback=self.parse)


def crawl_site(start_url, output_dir=DEFAULT_OUTPUT_DIR, depth_limit=5):
    """
    Crawl an entire site from within Python and save HTML files locally.

    Args:
        start_url (str): The URL to start crawling from.
        output_dir (str): Where to save HTML files.
        depth_limit (int): Maximum crawl depth (to avoid infinite crawling).
    """
    process = CrawlerProcess(
        settings={
            "ROBOTSTXT_OBEY": True,
            "DOWNLOAD_DELAY": 0.5,
            "DEPTH_LIMIT": depth_limit,
            "LOG_LEVEL": "INFO",
        }
    )

    process.crawl(FullSiteSpider, start_url=start_url, output_dir=output_dir)
    process.start(stop_after_crawl=True, install_signal_handlers=False)
