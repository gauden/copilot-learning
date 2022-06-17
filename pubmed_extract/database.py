"""
Import sqlite as the database to hold Pubmed searches.
Read the file called "tmp.xml" into an XML object. 
Set up a sqlite database called "pubmed.db" in the data folder.
Recursively run through the first child of the root element of the xml file.
Create two data classes that represent an author and a paper. 
Create another data class that represents a link 
between a specific author and a specific paper. 
Use these as the basis for creating the two tables (author and paper) 
and the relation between them (one author can write multiple papers 
and one paper can have multiple authors).
"""

from dataclasses import dataclass
import xml.etree.ElementTree as ET
from pprint import pprint

DB = "./data/pubmed.db"
FN = "./data/michael_marmot_2022_2022.xml"


@dataclass
class Author:
    name: str
    affiliation: str


def load_xml_file(file_name: str) -> ET.Element:
    """
    Load the XML file.
    """
    tree = ET.parse(file_name)
    return tree.getroot()


def retrieve_name_of_author(author_element: ET.Element) -> str:
    """
    Retrieve the name of the author given this XML structure:

    <Author ValidYN="Y">
        <LastName>Marmot</LastName>
        <ForeName>Michael</ForeName>
        <Initials>M</Initials>
        <AffiliationInfo>
            <Affiliation>Department of Epidemiology and Public Health, University College London Institute of Health Equity, London, England.</Affiliation>
        </AffiliationInfo>
    </Author>

    or this XML structure:

    <Author ValidYN="Y">
        <CollectiveName>Sustainable Health Equity Movement</CollectiveName>
    </Author>
    """
    name = ""
    for child in author_element:
        if child.tag == "LastName":
            name = child.text
        if child.tag == "ForeName":
            name += " " + child.text
        if child.tag == "Initials":
            name += " " + child.text
        if child.tag == "CollectiveName":
            name = f"{child.text} (Collective)"
    return name


def retrieve_author_affiliation(author_element: ET.Element) -> str:
    """
    Retrieve the affiliation of the author given this XML structure:

    <Author ValidYN="Y">
        <LastName>Marmot</LastName>
        <ForeName>Michael</ForeName>
        <Initials>M</Initials>
        <AffiliationInfo>
            <Affiliation>Department of Epidemiology and Public Health, University College London Institute of Health Equity, London, England.</Affiliation>
        </AffiliationInfo>
    </Author>

    or this XML structure:

    <Author ValidYN="Y">
        <CollectiveName>Sustainable Health Equity Movement</CollectiveName>
    </Author>
    """
    affiliation = ""
    for child in author_element:
        if child.tag == "AffiliationInfo":
            affiliation = child.find("Affiliation").text
    return affiliation


def get_authors(root: ET.Element) -> list:
    """
        Get the name and affiliation of each author from
        AuthorList in each PubmedArticle given this XML structure:

    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation Status="MEDLINE" Owner="NLM">
                <Article PubModel="Electronic">
                    <AuthorList CompleteYN="Y">
                        <Author ValidYN="Y">
                            <LastName>Marmot</LastName>
                            <ForeName>Michael</ForeName>
                            <Initials>M</Initials>
                            <AffiliationInfo>
                                <Affiliation>UCL Institute of Health Equity, UCL.</Affiliation>
                            </AffiliationInfo>
                        </Author>
                    </AuthorList>
                </Article>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    authors = []
    for article in root:
        for author in (
            article.find("MedlineCitation")
            .find("Article")
            .find("AuthorList")
            .findall("Author")
        ):
            authors.append(
                Author(
                    retrieve_name_of_author(author), retrieve_author_affiliation(author)
                )
            )
    return authors


def main(file_name: str) -> None:
    """
    Main function.
    """
    root = load_xml_file(file_name)
    authors = get_authors(root)
    pprint(authors)


if __name__ == "__main__":
    main(file_name=FN)
