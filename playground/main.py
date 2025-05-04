from scraper import BSoupRecipeScraper

scraper = BSoupRecipeScraper()
result = scraper.scrape("https://www.allrecipes.com/recipe/46822/indian-chicken-curry-ii/")
# result = scraper.scrape("https://www.recipetineats.com/thai-coconut-pumpkin-soup/")

if result['status'] == 'success':
    for ing in result['ingredients']:
        print(ing + '\n')
        pass
else:
    print("Scraping failed:", result['message'])
