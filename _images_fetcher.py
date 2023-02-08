import os
from icrawler.builtin import GoogleImageCrawler, FlickrImageCrawler
from icrawler.builtin import GreedyImageCrawler
import csv
import time
import urllib
from urllib.request import urlopen
import time

#import flickrapi
#from api_keys import FLICKR_KEY, FLICKR_SECRET
#flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET, format='parsed-json')

#resp = flickr.urls.lookupGroup(api_key = FLICKR_KEY, url = "https://www.flickr.com/groups/architecturelab/")
#print(resp)
shiki_dir = os.path.join(os.getcwd(), "shikimori_images")
shikimori_urls = []
#shikimori_urls.append("https://shikimori.org/animes/2246")
#shikimori_urls.append("https://shikimori.org/animes/1")
shikimori_urls.append("https://www.igdb.com/games/grand-theft-auto-san-andreas")
shikimori_urls.append("https://www.igdb.com/games/the-talos-principle-road-to-gehenna")
#shikimori_urls.append("https://shikimori.org/animes/820")
#shikimori_urls.append("https://shikimori.org/animes/x578")
# shikimori_urls.append("https://shikimori.org/animes/431")
# shikimori_urls.append("https://shikimori.org/animes/33")
# shikimori_urls.append("https://shikimori.org/animes/z486")
# shikimori_urls.append("https://shikimori.org/animes/z31758")
# shikimori_urls.append("https://shikimori.org/animes/z31757")
# shikimori_urls.append("https://shikimori.org/animes/z32949")
# shikimori_urls.append("https://shikimori.org/animes/474")
# shikimori_urls.append("https://shikimori.org/animes/x17074")
# shikimori_urls.append("https://shikimori.org/animes/457")
# shikimori_urls.append("https://shikimori.org/animes/24701")
# shikimori_urls.append("https://shikimori.org/animes/28957")
# shikimori_urls.append("https://shikimori.org/animes/30")
# shikimori_urls.append("https://shikimori.org/animes/z9253")
# shikimori_urls.append("https://shikimori.org/animes/3091")
# shikimori_urls.append("https://shikimori.org/animes/6864")
# shikimori_urls.append("https://shikimori.org/animes/y5081")
# shikimori_urls.append("https://shikimori.org/animes/5")
# shikimori_urls.append("https://shikimori.org/animes/z790")
# shikimori_urls.append("https://shikimori.org/animes/24765")
# shikimori_urls.append("https://shikimori.org/animes/35557")
# shikimori_urls.append("https://shikimori.org/animes/12189")
# shikimori_urls.append("https://shikimori.org/animes/31933")
# shikimori_urls.append("https://shikimori.org/animes/3783")
# shikimori_urls.append("https://shikimori.org/animes/5205")
# shikimori_urls.append("https://shikimori.org/animes/32281")
# shikimori_urls.append("https://shikimori.org/animes/z9260")
# shikimori_urls.append("https://shikimori.org/animes/33206")
# shikimori_urls.append("https://shikimori.org/animes/y32937")
# shikimori_urls.append("https://shikimori.org/animes/x16782")
# shikimori_urls.append("https://shikimori.org/animes/19")
#
#shikimori_urls = [_+"/screenshots/" for _ in shikimori_urls]

#for i in range(len(shikimori_urls)):
    #print(shikimori_urls[i])
    #req = urllib.request(url=shikimori_urls[i])
    #resp = urlopen(shikimori_urls[i], timeout=3)
    #redirected = resp.geturl()
    #print(redirected)
    #if "screenshots" not in redirected:
        #redirected+="/screenshots/"
    #shikimori_urls[i] = redirected
    #print(shikimori_urls[i])
    #time.sleep(1)
    #resp = urlopen(shikimori_urls[i], timeout=3)
    #redirected = resp.geturl()
    #print(redirected)
    #print()


greedy_crawler = GreedyImageCrawler(storage={'root_dir': shiki_dir})
greedy_crawler.crawl(domains=shikimori_urls, max_num=0,
                         min_size=(1280,720), max_size=None)
exit()

for ani_url in shikimori_urls:
    ani_url += "/screenshots"
    len_existing = len([name for name in os.listdir(shiki_dir) if os.path.isfile(name)])

    greedy_crawler = GreedyImageCrawler(storage={'root_dir': shiki_dir})
    greedy_crawler.crawl(domains=ani_url, max_num=0,
                         min_size=(1280, 720), max_size=None, file_idx_offset=len_existing+1)
exit()
streets_flickr_group = "1468642@N24"


#google_crawler = GoogleImageCrawler(
    #feeder_threads=1,
    #parser_threads=2,
    #downloader_threads=4,
    #storage={'root_dir': os.path.join(os.getcwd(), "images")})
#filters = dict(
    #type= "photo",
    #size='=1920x1080')
pools = {}
pools["silence"] = "1425976@N24"
pools["architecture"] = "1468642@N24"
pools["lonecity"] = "91283770@N00"
pools["pure_landscaped"] = "1191681@N23"
pools["empty_houses"] = "51594024@N00"
pools["parks"] = "72717767@N00"
pools["vanishing"] = "55475894@N00"
flickr_crawler = FlickrImageCrawler(FLICKR_KEY,
                            storage={'root_dir': os.path.join(os.getcwd(), "images_6_byhand_to_delete")})
flickr_crawler.crawl(max_num=5000, group_id=pools["vanishing"], file_idx_offset=0)
exit()

#with open(os.path.join(os.getcwd(), "datasets", "cities_list.csv")) as sources_file:
#initial_offset = 1222
#with open(os.path.join(os.getcwd(), "datasets", "coutries_list.csv")) as sources_file:
p1 = 100000
p2 = 250000
p3 = 500000
p4 = 1000000
p5 = 2500000
with open(os.path.join(os.getcwd(), "datasets", "world_cities_parsed.csv")) as sources_file:
    reader = csv.reader(sources_file)
    for i, line in enumerate(reader):
        print(line)
        #city, country = line
        city, country, population = line
        population = int(population)
        images_to_fetch = 1 if population < p1 else 2 if population < p2 else 3 if population < p3 else 4 if population < p4 else 5
        google_crawler.crawl(keyword=f'{city} {country}', filters=filters, offset=0, max_num=5, file_idx_offset=initial_offset)
        initial_offset += images_to_fetch
        #if i == 10:
            #break

# import flickrapi
# from api_keys import FLICKR_KEY, FLICKR_SECRET
# flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET)
#
# lat = 48.83417
# lon = 12.221111
# photo_list = flickr.photos.search(api_key=FLICKR_KEY, lat=lat, lon=lon, accuracy=11, format='parsed-json')
# print(photo_list)
# first_photo = photo_list["photos"]["photo"][0]
# first_photo_id = first_photo["id"]
# shorturl = flickrapi.shorturl.url(first_photo_id)
#
