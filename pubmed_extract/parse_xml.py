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
from glob import glob
import os
from typing import List, Iterator
import xml.etree.ElementTree as ET

DATA_DIR = "data"
DB = "./data/pubmed.db"


@dataclass
class Author:
    name: str
    affiliation: str


@dataclass
class Reference:
    citation: str
    pmid: str


@dataclass
class Paper:
    title: str
    journal: str
    journal_abbreviation: str
    year: str
    month: str
    day: str
    pub_date: str
    page_numbers: str
    doi: str
    pmc_id: str
    authors: List[Author]
    abstract: str
    mesh_terms: List[str]
    references: List[Reference]
    quick_summary: str
    full_xml: str


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


def create_date_string(year: str, month: str, day: str, medline_date: str) -> str:
    """
    Create a date string from the year, month and day.
    """
    ds = f"{year}" if year else ""
    ds = f"{year}-{month}" if month else ds
    ds = f"{year}-{month}-{day}" if day else ds
    ds = medline_date if medline_date else ds
    return ds


def retrieve_paper(paper_element: ET.Element) -> dict:
    """
        Extract the details of the paper given this XML structure:

    <PubmedArticle>
        <MedlineCitation Status="MEDLINE" IndexingMethod="Automated" Owner="NLM">
            <Article PubModel="Print-Electronic">
                <Journal>
                    <ISSN IssnType="Electronic">1564-0604</ISSN>
                    <JournalIssue CitedMedium="Internet">
                        <Volume>100</Volume>
                        <Issue>1</Issue>
                        <PubDate>
                            <Year>2022</Year>
                            <Month>Jan</Month>
                            <Day>01</Day>
                        </PubDate>
                    </JournalIssue>
                    <Title>Bulletin of the World Health Organization</Title>
                    <ISOAbbreviation>Bull World Health Organ</ISOAbbreviation>
                </Journal>
                <ArticleTitle>Achieving sustainable health equity.</ArticleTitle>
                <Pagination>
                    <MedlinePgn>81-83</MedlinePgn>
                </Pagination>
                <ELocationID EIdType="doi" ValidYN="Y">10.2471/BLT.21.286523</ELocationID>
                <Language>eng</Language>
                <PublicationTypeList>
                    <PublicationType UI="D016428">Journal Article</PublicationType>
                </PublicationTypeList>
                <ArticleDate DateType="Electronic">
                    <Year>2021</Year>
                    <Month>11</Month>
                    <Day>25</Day>
                </ArticleDate>
            </Article>
            <MedlineJournalInfo>
                <Country>Switzerland</Country>
                <MedlineTA>Bull World Health Organ</MedlineTA>
                <NlmUniqueID>7507052</NlmUniqueID>
                <ISSNLinking>0042-9686</ISSNLinking>
            </MedlineJournalInfo>
            <MeshHeadingList>
                <MeshHeading>
                    <DescriptorName UI="D000069576" MajorTopicYN="Y">Health Equity</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D006291" MajorTopicYN="N">Health Policy</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D006801" MajorTopicYN="N">Humans</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName UI="D000076502" MajorTopicYN="N">Sustainable Development</DescriptorName>
                </MeshHeading>
            </MeshHeadingList>
        </MedlineCitation>
        <PubmedData>
            <ArticleIdList>
                <ArticleId IdType="pubmed">35017761</ArticleId>
                <ArticleId IdType="doi">10.2471/BLT.21.286523</ArticleId>
                <ArticleId IdType="pii">BLT.21.286523</ArticleId>
                <ArticleId IdType="pmc">PMC8722628</ArticleId>
            </ArticleIdList>
            <ReferenceList>
                <Reference>
                    <Citation>Science. 2015 Feb 13;347(6223):1259855</Citation>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">25592418</ArticleId>
                    </ArticleIdList>
                </Reference>
                <Reference>
                    <Citation>Lancet. 2020 Feb 22;395(10224):605-658</Citation>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">32085821</ArticleId>
                    </ArticleIdList>
                </Reference>
                <Reference>
                    <Citation>Lancet. 2020 May 30;395(10238):1690-1691</Citation>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">32419711</ArticleId>
                    </ArticleIdList>
                </Reference>
                <Reference>
                    <Citation>Annu Rev Public Health. 2021 Apr 1;42:381-403</Citation>
                    <ArticleIdList>
                        <ArticleId IdType="pubmed">33326297</ArticleId>
                    </ArticleIdList>
                </Reference>
            </ReferenceList>
        </PubmedData>
    </PubmedArticle>
    """
    # Get the title of the paper
    title = (
        paper_element.find("MedlineCitation").find("Article").find("ArticleTitle").text
    )
    # Get the journal details
    journal = (
        paper_element.find("MedlineCitation")
        .find("Article")
        .find("Journal")
        .find("Title")
        .text
    )
    journal_abbreviation = (
        paper_element.find("MedlineCitation")
        .find("Article")
        .find("Journal")
        .find("ISOAbbreviation")
        .text
    )
    # Get the date of publication element
    pub_date_element = (
        paper_element.find("MedlineCitation")
        .find("Article")
        .find("Journal")
        .find("JournalIssue")
        .find("PubDate")
    )
    # Get the year of publication testing for AttributeError
    try:
        year = pub_date_element.find("Year").text
    except AttributeError:
        year = None
    # Get the month of publication testing for AttributeError
    try:
        month = pub_date_element.find("Month").text
    except AttributeError:
        month = None
    # Get the day of publication testing for AttributeError
    try:
        day = pub_date_element.find("Day").text
    except AttributeError:
        day = None
    # Get the MedlineDate inside the PubmedData element, testing for AttributeError
    try:
        medline_date = pub_date_element.find("MedlineDate").text
    except AttributeError:
        medline_date = None
    # Create a date object from the year, month and day ensuring that all are not None
    pub_date = create_date_string(year, month, day, medline_date)
    # Get the page numbers of the paper, testing for AttributeError
    try:
        page_numbers = (
            paper_element.find("MedlineCitation")
            .find("Article")
            .find("Pagination")
            .find("MedlinePgn")
            .text
        )
    except AttributeError:
        page_numbers = None
    # Get the DOI of the paper testing for AttributeError
    try:
        doi = paper_element.find("MedlineCitation")
        doi = doi.find("Article")
        doi = doi.find("ELocationID")
        doi = doi.text
    except AttributeError:
        doi = None
    # Get the PMC ID of the paper
    pmc_id = paper_element.find("MedlineCitation").find("PMID").text
    # Get the authors of the paper
    authors = []
    for author in (
        paper_element.find("MedlineCitation")
        .find("Article")
        .find("AuthorList")
        .findall("Author")
    ):
        authors.append(
            Author(retrieve_name_of_author(author), retrieve_author_affiliation(author))
        )
    # Get the abstract of the paper if it exists returning empty string in case of AttributeError
    try:
        abstract = (
            paper_element.find("MedlineCitation")
            .find("Article")
            .find("Abstract")
            .find("AbstractText")
            .text
        )
    except AttributeError:
        abstract = ""
    # Get the mesh terms of the paper returning empty list in case of AttributeError
    try:
        mesh_terms = []
        for mesh_term in (
            paper_element.find("MedlineCitation")
            .find("MeshHeadingList")
            .findall("MeshHeading")
        ):
            mesh_terms.append(mesh_term.find("DescriptorName").text)
    except AttributeError:
        mesh_terms = []
    # Get the references of the paper returns empty list in case of AttributeError
    try:
        references = []
        for reference in (
            paper_element.find("PubmedData").find("ReferenceList").findall("Reference")
        ):
            references.append(
                Reference(
                    reference.find("Citation").text,
                    reference.find("ArticleIdList").find("ArticleId").text,
                )
            )
    except AttributeError:
        references = []
    # Convert the full XML of the paper to a string
    full_xml = ET.tostring(paper_element)
    # display the ID, title, and date of the paper
    quick_summary = f"{pmc_id} - {pub_date} - {title} - {journal_abbreviation}"
    # Return the paper
    record = Paper(
        title,
        journal,
        journal_abbreviation,
        year,
        month,
        day,
        pub_date,
        page_numbers,
        doi,
        pmc_id,
        authors,
        abstract,
        mesh_terms,
        references,
        quick_summary,
        full_xml,  # added so full record of the paper may be stored in the database
    )
    return record


def extract_data_from_file(file_name: str) -> Iterator[Paper]:
    """
    Parse each record from a file containing an
    XML object representing the results of a PubMed search.
    """
    root = load_xml_file(file_name)
    for paper_element in root.findall("PubmedArticle"):
        yield retrieve_paper(paper_element)


def main(list_of_files: List[str]) -> None:
    """
    Main function.
    """
    for fn in list_of_files:
        print(f"Processing {fn}")
        for record in extract_data_from_file(fn):
            print(record.title)


if __name__ == "__main__":
    # glob the XML files in the data directory
    list_of_files = glob(os.path.join(DATA_DIR, "*.xml"))
    main(list_of_files)
