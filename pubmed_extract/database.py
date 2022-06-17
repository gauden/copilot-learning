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
import sqlite3
from dataclasses import dataclass
import xml.etree.ElementTree as ET

DB = "./data/pubmed.db"


def create_tables():
    """
    Create the tables in the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE author (
        id INTEGER PRIMARY KEY,
        name TEXT,
        affiliation TEXT,
        email TEXT,
        homepage TEXT,
        orcid TEXT,
        pubmed_id TEXT
    )"""
    )
    c.execute(
        """CREATE TABLE paper (
        id INTEGER PRIMARY KEY,
        title TEXT,
        abstract TEXT,
        pubmed_id TEXT,
        pubdate TEXT,
        journal TEXT,
        volume TEXT,
        issue TEXT,
        pages TEXT,
        authors TEXT,
        doi TEXT,
        pmc_id TEXT,
        pmc_url TEXT,
        pubmed_url TEXT,
        pubmed_id TEXT
    )"""
    )
    c.execute(
        """CREATE TABLE author_paper (
        author_id INTEGER,
        paper_id INTEGER,
        FOREIGN KEY (author_id) REFERENCES author(id),
        FOREIGN KEY (paper_id) REFERENCES paper(id)
    )"""
    )
    conn.commit()
    conn.close()


def insert_author(author):
    """
    Insert an author into the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """INSERT INTO author (
        name,
        affiliation,
        email,
        homepage,
        orcid,
        pubmed_id
    ) VALUES (?, ?, ?, ?, ?, ?)""",
        (
            author.name,
            author.affiliation,
            author.email,
            author.homepage,
            author.orcid,
            author.pubmed_id,
        ),
    )
    conn.commit()
    conn.close()


def insert_paper(paper):
    """
    Insert a paper into the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """INSERT INTO paper (
        title,
        abstract,
        pubmed_id,
        pubdate,
        journal,
        volume,
        issue,
        pages,
        authors,
        doi,
        pmc_id,
        pmc_url,
        pubmed_url,
        pubmed_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            paper.title,
            paper.abstract,
            paper.pubmed_id,
            paper.pubdate,
            paper.journal,
            paper.volume,
            paper.issue,
            paper.pages,
            paper.authors,
            paper.doi,
            paper.pmc_id,
            paper.pmc_url,
            paper.pubmed_url,
            paper.pubmed_id,
        ),
    )
    conn.commit()
    conn.close()


def insert_author_paper(author_id, paper_id):
    """
    Insert a link between an author and a paper into the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """INSERT INTO author_paper (
        author_id,
        paper_id
    ) VALUES (?, ?)""",
        (author_id, paper_id),
    )
    conn.commit()
    conn.close()


def get_author_id(author):
    """
    Get the id of an author from the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT id FROM author WHERE pubmed_id = ?""", (author.pubmed_id,))
    author_id = c.fetchone()
    conn.close()
    return author_id[0]


def get_paper_id(paper):
    """
    Get the id of a paper from the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT id FROM paper WHERE pubmed_id = ?""", (paper.pubmed_id,))
    paper_id = c.fetchone()
    conn.close()
    return paper_id[0]


def get_author_paper_id(author_id, paper_id):
    """
    Get the id of a link between an author and a paper from the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT id FROM author_paper WHERE author_id = ? AND paper_id = ?""",
        (author_id, paper_id),
    )
    author_paper_id = c.fetchone()
    conn.close()
    return author_paper_id[0]


def get_author_by_id(author_id):
    """
    Get an author from the database by id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT * FROM author WHERE id = ?""", (author_id,))
    author = c.fetchone()
    conn.close()
    return author


def get_paper_by_id(paper_id):
    """
    Get a paper from the database by id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT * FROM paper WHERE id = ?""", (paper_id,))
    paper = c.fetchone()
    conn.close()
    return paper


def get_author_paper_by_id(author_paper_id):
    """
    Get a link between an author and a paper from the database by id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT * FROM author_paper WHERE id = ?""", (author_paper_id,))
    author_paper = c.fetchone()
    conn.close()
    return author_paper


def get_author_papers(author_id):
    """
    Get all papers written by an author from the database.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT * FROM paper WHERE id IN (SELECT paper_id FROM author_paper WHERE author_id = ?)""",
        (author_id,),
    )
    papers = c.fetchall()
    conn.close()
    return papers


def get_author_by_pubmed_id(pubmed_id):
    """
    Get an author from the database by pubmed id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT * FROM author WHERE pubmed_id = ?""", (pubmed_id,))
    author = c.fetchone()
    conn.close()
    return author


def get_paper_by_pubmed_id(pubmed_id):
    """
    Get a paper from the database by pubmed id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT * FROM paper WHERE pubmed_id = ?""", (pubmed_id,))
    paper = c.fetchone()
    conn.close()
    return paper


def get_author_paper_by_pubmed_id(pubmed_id):
    """
    Get a link between an author and a paper from the database by pubmed id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""SELECT * FROM author_paper WHERE pubmed_id = ?""", (pubmed_id,))
    author_paper = c.fetchone()
    conn.close()
    return author_paper


def get_author_papers_by_pubmed_id(pubmed_id):
    """
    Get all papers written by an author from the database by pubmed id.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT * FROM paper WHERE id IN (SELECT paper_id FROM author_paper WHERE pubmed_id = ?)""",
        (pubmed_id,),
    )
    papers = c.fetchall()
    conn.close()
    return papers


def get_author_papers_by_pubmed_id_and_year(pubmed_id, year):
    """
    Get all papers written by an author from the database by pubmed id and year.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT * FROM paper WHERE id IN (SELECT paper_id FROM author_paper WHERE pubmed_id = ?) AND pubdate LIKE ?""",
        (pubmed_id, "%" + str(year) + "%"),
    )
    papers = c.fetchall()
    conn.close()
    return papers


def get_author_papers_by_pubmed_id_and_year_and_month(pubmed_id, year, month):
    """
    Get all papers written by an author from the database by pubmed id and year and month.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT * FROM paper WHERE id IN (SELECT paper_id FROM author_paper WHERE pubmed_id = ?) AND pubdate LIKE ?""",
        (pubmed_id, "%" + str(year) + "-" + str(month) + "%"),
    )
    papers = c.fetchall()
    conn.close()
    return papers


def load_xml_file_and_yield_papers(xml_file):
    """
    Load an xml file and yield all papers in it.
    """
    with open(xml_file, "r") as f:
        xml = f.read()
    root = ET.fromstring(xml)
    for paper in root.findall("PubmedArticle"):
        yield Paper(paper)


# create Paper dataclass and initialize it with the xml data for one paper
class Paper:
    def __init__(self, xml):
        self.xml = xml
        self.title = xml.find("ArticleTitle").text
        self.pubdate = xml.find("PubDate").text
        self.pubmed_id = xml.find("PMID").text
        self.authors = []
        for author in xml.findall("AuthorList/Author"):
            self.authors.append(Author(author))
        self.abstract = xml.find("Abstract").text
        self.journal = xml.find("Journal").text
        self.volume = xml.find("Journal").find("JournalIssue").find("Volume").text
        self.issue = xml.find("Journal").find("JournalIssue").find("Issue").text
        self.pages = xml.find("Pagination").find("MedlinePgn").text
        self.doi = xml.find("Article").find("ELocationID").text
        self.url = xml.find("Article").find("ELocationID").attrib["EIdType"]
        self.abstract = xml.find("Abstract").text
        self.abstract_html = xml.find("Abstract").find("AbstractText").text
        self.abstract_text = (
            xml.find("Abstract").find("AbstractText").text.replace("\n", " ")
        )
        self.abstract_text = self.abstract_text.replace("\t", " ")
        self.abstract_text = self.abstract_text.replace("\r", " ")
        self.abstract_text = self.abstract_text.replace("  ", " ")

    def __str__(self):
        return self.title


# create Author dataclass and initialize it with the xml data for one author
class Author:
    def __init__(self, xml):
        self.xml = xml
        self.last_name = xml.find("LastName").text
        self.first_name = xml.find("ForeName").text
        self.initials = xml.find("Initials").text
        self.suffix = xml.find("Suffix").text
        self.middle_name = xml.find("MiddleName").text
