"""Pubmed Extractor.

Given an author, and a start and end year, collect a set of records from pubmed and save them to a file.
Using the local data, count the number of papers per year.
Present a Markdown table of the results: year, number of papers.

`usage: main.py [-h] [--output OUTPUT] [--verbose] author start_year [end_year]
"""
import argparse
import logging
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET


def prepare_query_string(author: str, start_year: int, end_year: int) -> str:
    """
    Prepare the query string for the pubmed search.
    """
    query_string = '"{}" AND "{}"'.format(author, start_year)
    if end_year:
        query_string += ' AND "{}"'.format(end_year)
    return query_string


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract records from pubmed")
    parser.add_argument("author", help="Author to search for")
    parser.add_argument("start_year", type=int, help="Start year to search for")
    parser.add_argument(
        "end_year", type=int, nargs="?", default=None, help="End year to search for"
    )
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.output:
        args.output = "{}_{}_{}.xml".format(args.author, args.start_year, args.end_year)
    if os.path.exists(args.output):
        logging.error("Output file already exists: {}".format(args.output))
        sys.exit(1)

    query_string = prepare_query_string(args.author, args.start_year, args.end_year)
    logging.info("Query string: {}".format(query_string))
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}".format(
        query_string
    )
    logging.info("URL: {}".format(url))
    with urllib.request.urlopen(url) as response:
        xml = response.read()
    logging.info("Response: {}".format(xml))
    root = ET.fromstring(xml)
    logging.info("Root: {}".format(root))
    uid_list = root.find("IdList").findall("Id")
    logging.info("UID list: {}".format(uid_list))
    uid_list = [uid.text for uid in uid_list]
    logging.info("UID list: {}".format(uid_list))
    uid_list = ",".join(uid_list)
    logging.info("UID list: {}".format(uid_list))
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml".format(
        uid_list
    )
    logging.info("URL: {}".format(url))
    with urllib.request.urlopen(url) as response:
        xml = response.read()
    logging.info("Response: {}".format(xml))
    with open(args.output, "wb") as f:
        f.write(xml)
    logging.info("Saved to: {}".format(args.output))

    # Count the number of papers per year
    tree = ET.parse(args.output)
    root = tree.getroot()
    logging.info("Root: {}".format(root))
    year_counts = {}
    for article in root.findall("Article"):
        year = article.find("ArticleDate").find("Year").text
        if year not in year_counts:
            year_counts[year] = 0
        year_counts[year] += 1
    logging.info("Year counts: {}".format(year_counts))
    # Present a Markdown table of the results
    print("| Year | Number of papers |")
    print("| ---- | --------------- |")
    for year, count in year_counts.items():
        print("| {} | {} |".format(year, count))
    print("| Total | {} |".format(sum(year_counts.values())))
    print("|")
