# README.md

# Crawler Package

## Overview

The Crawler package is a Python application designed to fetch and classify metadata for movies, including details about actors, writers, and directors. It interacts with an external API to collect movie details and stores them in a SQLite database.

## Features

- **Media File Finder**: Automatically locates media files in specified directories.
- **API Integration**: Fetches movie details from the OMDb API.
- **Metadata Classification**: Classifies and updates metadata for actors, writers, and directors from a SQLite database and Wikipedia.
- **Unit Testing**: Includes tests to ensure functionality and reliability.

## Installation

To install the package locally, navigate to the project directory and run:

```bash
pip install -e .
```

## Usage

### Running the Crawler

To run the crawler, execute the `crawler.py` script:

```bash
python -m crawler.crawler
```

### Example

The `WebScraper` class can be used to classify metadata as follows:

```python
from crawler.webscraper import WebScraper

scraper = WebScraper(db_path='path_to_your_database.db')
scraper.classify_metadata()
scraper.close()
```

## Requirements

The following dependencies are required:

- requests
- beautifulsoup4

Install them using:

```bash
pip install -r requirements.txt
```

## Testing

To run the tests, use the following command:

```bash
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.