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
import urllib.request
import xml.etree.ElementTree as ET


def prepare_query_string(author: str, start_year: int, end_year: int) -> str:
    """
    Prepare the query string for the pubmed search.

    """
    query_string = (
        '({}) AND (("{}"[Date - Publication] : "{}"[Date - Publication]))'.format(
            author, start_year, end_year
        )
    )
    # url encode the query string
    query_string = urllib.parse.quote(query_string)
    return query_string


def create_url(query_string: str) -> str:
    """
    Create the URL for the pubmed search.
    """
    return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}".format(
        query_string
    )


def loop_through_all_publications_and_collect_ids(url: str, query_string: str) -> list:
    """
    Loop through all publications and collect the ids for all pages in the dataset
    using the count, retmax, and retstart parameters from the XML file.
    """
    ids = []
    while url:
        response = urllib.request.urlopen(url)
        xml = response.read()
        tree = ET.fromstring(xml)
        for child in tree:
            if child.tag == "IdList":
                for id in child:
                    ids.append(id.text)
        url = None
        for child in tree:
            if child.tag == "QueryResult":
                for child2 in child:
                    if child2.tag == "WebEnv":
                        webenv = child2.text
                    if child2.tag == "Count":
                        count = int(child2.text)
                    if child2.tag == "RetMax":
                        retmax = int(child2.text)
                    if child2.tag == "RetStart":
                        retstart = int(child2.text)
            if retstart + retmax < count:
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}&retmax={}&retstart={}&WebEnv={}".format(
                    query_string, retmax, retstart + retmax, webenv
                )
    return ids


def parse_and_validate_args(args: list) -> argparse.Namespace:
    """
    Parse and validate the command line arguments.
    """
    parser = argparse.ArgumentParser(description="Pubmed Extractor")
    parser.add_argument("--output", "-o", default="output.txt", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("author", help="Author to search for")
    parser.add_argument("start_year", type=int, help="Start year")
    parser.add_argument("end_year", type=int, nargs="?", default=None, help="End year")
    return parser.parse_args(args)


def create_output_file(args: argparse.Namespace) -> None:
    """
    Create the output file.
    """
    if not args.output:
        args.output = "./data/{}_{}_{}.xml".format(
            args.author, args.start_year, args.end_year
        )
    if os.path.exists(args.output):
        logging.error("Output file already exists: {}".format(args.output))
        sys.exit(1)


def main():
    """
    Main function.
    """
    args = parse_and_validate_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    create_output_file(args)
    query_string = prepare_query_string(args.author, args.start_year, args.end_year)
    url = create_url(query_string)
    logging.info("URL: {}".format(url))
    ids = loop_through_all_publications_and_collect_ids(url, query_string)
    logging.info("Found {} publications".format(len(ids)))
    with open(args.output, "w") as f:
        f.write("\n".join(ids))


if __name__ == "__main__":
    main()
