# Crawler

## Usage

### WebScraper

The `WebScraper` class is used to fetch actors, writers, and directors from the `filemetadata` table and classify them in their respective tables with foreign keys to the movies they are found in.

#### Example

```python
from webscraper import WebScraper

scraper = WebScraper(db_path='path_to_your_database.db')
scraper.classify_metadata()
scraper.close()
```
