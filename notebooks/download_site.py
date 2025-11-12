import os

from peterbot.jobs.download_site import crawl_site

output_dir = os.path.join("notebooks", "data_download_site")
BASE_URL = "https://recipes.joemay.net/"
# crawl_site(BASE_URL, output_dir=output_dir)
crawl_site(BASE_URL)
