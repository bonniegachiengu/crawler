from setuptools import setup, find_packages

setup(
    name='Crawler',
    version='0.1.0',
    author='Bonnie Gachiengu',
    author_email='bonniegachiengu@gmail.com',
    description='A package for crawling and classifying movie metadata.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bonniegachiengu/crawler',  # Update with your repository URL
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)