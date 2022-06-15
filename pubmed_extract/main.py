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

# set global EMAIL from environment variable
EMAIL = os.environ.get("EMAIL_ADDRESS")
TOOL = "pubmed_extract"


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


def create_url_for_esearch(query_string: str) -> str:
    """
    Create the URL for the pubmed search with usehistory=y.
    """
    return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}&usehistory=y".format(
        query_string
    )


def get_count_of_papers_using_esearch(query_string: str) -> int:
    """
    Get the count of papers using esearch.
    """
    url = create_url_for_esearch(query_string)
    logging.info("URL: {}".format(url))
    response = urllib.request.urlopen(url)
    xml = response.read()
    root = ET.fromstring(xml)

    # extract count, webenv, and querykey from the search results
    count = root.find("Count").text
    logging.info("Found {} publications".format(count))
    webenv = root.find("WebEnv").text
    querykey = root.find("QueryKey").text
    return int(count), webenv, querykey


def get_records_for_ids(
    ids: list, email: str, tool: str, webenv: str, querykey: str
) -> list:
    """
    Get the records for the given ids using efetch with the webenv and querykey.
    """
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&rettype=abstract&id={}&tool={}&email={}&WebEnv={}&query_key={}".format(
        ",".join(ids), tool, email, webenv, querykey
    )
    logging.info("URL: {}".format(url))
    response = urllib.request.urlopen(url)
    xml = response.read()
    root = ET.fromstring(xml)
    return root.findall("PubmedArticle")


def get_ids_for_batch(i: int, batch_size: int, webenv: str, querykey: str) -> list:
    """
    Get the ids for a batch of records.
    """
    core_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=xml"
    url = "{}&rettype=abstract&retstart={}&retmax={}&tool={}&email={}&WebEnv={}&query_key={}".format(
        core_url, i, batch_size, TOOL, EMAIL, webenv, querykey
    )
    logging.info("URL: {}".format(url))
    response = urllib.request.urlopen(url)
    xml = response.read()
    root = ET.fromstring(xml)
    ids = [id.text for id in root.findall("IdList/Id")]
    return ids


def retrieve_all_records_in_batches(
    query_string: str, email: str = EMAIL, tool: str = TOOL
) -> list:
    """
    Loop through all publications and collect the records for all papers in the search results.
    """

    # retrieve the search results and count using esearch
    count, webenv, querykey = get_count_of_papers_using_esearch(query_string)

    # retrieve the records in batches using efetch
    batch_size = 100
    records = []
    for i in range(0, count, batch_size):
        ids = get_ids_for_batch(i, batch_size, webenv, querykey)
        records.extend(get_records_for_ids(ids, email, tool, webenv, querykey))
    return records


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


def create_output_file_name(args: argparse.Namespace) -> None:
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
    create_output_file_name(args)

    query_string = prepare_query_string(args.author, args.start_year, args.end_year)
    records = retrieve_all_records_in_batches(query_string)
    # log the number of records found
    logging.info("Found {} records".format(len(records)))
    # create root XML element called "PubmedArticleSet" and add records to it
    root = ET.Element("PubmedArticleSet")
    for record in records:
        root.append(record)
    # write the XML to the output file
    with open(args.output, "w") as f:
        f.write(ET.tostring(root, encoding="unicode"))


if __name__ == "__main__":
    main()
