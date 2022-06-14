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
    count = root.find("Count").text
    logging.info("Found {} publications".format(count))
    return root, int(count)


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


def retrieve_all_records_in_batches(
    query_string: str, email: str = EMAIL, tool: str = TOOL
) -> list:
    """
    Loop through all publications and collect the records for all papers in the search results.
    """

    # retrieve the search results and count using esearch
    search_results_as_XML, count = get_count_of_papers_using_esearch(query_string)

    # get webenv and querykey from search results
    webenv = search_results_as_XML.find("WebEnv").text
    querykey = search_results_as_XML.find("QueryKey").text

    # retrieve the records in batches using efetch
    batch_size = 100
    batches = [
        search_results_as_XML.find("IdList").findall("Id")[i : i + batch_size]
        for i in range(0, count, batch_size)
    ]
    records = []
    for batch in batches:
        ids = [id.text for id in batch]
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
    records = retrieve_all_records_in_batches(query_string)
    # log the number of records found
    logging.info("Found {} records".format(len(records)))
    with open(args.output, "w") as f:
        for record in records:
            # convert record from ET Element to string ready for writing to file
            f.write(ET.tostring(record, encoding="unicode", method="xml"))
            f.write("\n")


if __name__ == "__main__":
    main()
