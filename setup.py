from setuptools import setup, find_packages

setup(
    name="smartripscraper",
    version="0.1",
    description="Scrape WMATA SmarTrip usage history into a SQLite database",
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords="",
    author="Kurt Raschke",
    author_email='kurt@kurtraschke.com',
    url='http://github.com/kurtraschke/WMATA-SmarTrip-Scraper',
    #license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'SQLAlchemy>=0.7.2',
        'mechanize>=0.2.5',
        'BeautifulSoup>=3.2.0'
    ],
    entry_points="""
    [console_scripts]
    smartripscraper = smartripscraper.scraper:main
    """,
)
