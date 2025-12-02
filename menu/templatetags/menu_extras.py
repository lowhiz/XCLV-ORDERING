from django import template

register = template.Library()

@register.filter
def category_icon(category):
    """Map category names to icon filenames"""
    icon_map = {
        'BEERS': 'beers.png',
        'COCKTAILS': 'cocktails.png',
        'SHOOTERS': 'shooters.png',
        'SINGLE SHOTS': 'shot.png',
        'MOCKTAILS': 'cocktail.png',
        'FRUITS': 'fruit.png',
        'BEVERAGES': 'soda.png',
        'FOOD': 'restaurant.png',
        'RUM': 'rum.png',
        'TEQUILA': 'tequila.png',
        'VODKA': 'vodka.png',
        'GIN': 'gin.png',
        'WINE': 'wine.png',
        'WHISKY/SCOTCH': 'vodka.png',
        'BRANDY/COGNAC': 'rum.png',
        'LIQUERS': 'rum.png',
    }
    return icon_map.get(category.upper(), 'cocktail.png')
