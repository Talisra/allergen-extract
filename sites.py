from dataclasses import dataclass

@dataclass
class Site:
    def __init__(self, domain: str, name: str, ingredient_selector: str):
        self.domain = domain
        self.name = name
        self.ingredient_selector = ingredient_selector


class SiteRegistry:
    sites = {
        'allrecipes.com': Site(
            domain='allrecipes.com',
            name='AllRecipes',
            ingredient_selector='[class*="ingredient"], .ingredients li'
        )
    }
    default_selector = '[class*="ingredient"], .ingredients li'