"""
SQL queries for the pubmed_extract database.

Import the dataclasses from the parse_xml module.
Create tables to mirror the dataclasses: author, reference, and paper.
Create a table to connect the author and paper tables.
Create a table to connect the reference and paper tables.
Create a table to connect the paper with Mesh Terms.
"""

from glob import glob
import os
import sqlite3
from typing import Iterator, List, Tuple
from parse_xml import Paper, extract_data_from_file

DATA_DIR = "./data"
DB = f"{DATA_DIR}/test.db"


def create_database_and_tables(db_name):
    """Create the pubmed_extract database and tables if not already existing.

    Note the fields in the Paper dataclass are:
        pmc_id: str
        title: str
        journal: str
        journal_abbreviation: str
        year: str
        month: str
        day: str
        pub_date: str
        page_numbers: str
        doi: str
        authors: List[Author]
        abstract: str
        mesh_terms: List[str]
        references: List[Reference]
        quick_summary: str
        full_xml: str
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS author (
        name TEXT PRIMARY KEY,
        affiliation TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS reference (
        pmid INTEGER PRIMARY KEY,
        citation TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS paper (
        pmc_id INTEGER PRIMARY KEY,
        title TEXT,
        journal TEXT,
        journal_abbreviation TEXT,
        year TEXT,
        month TEXT,
        day TEXT,
        pub_date TEXT,
        page_numbers TEXT,
        doi TEXT,
        abstract TEXT,
        quick_summary TEXT,
        full_xml TEXT
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS author_paper (
        name TEXT,
        pmc_id INTEGER,
        FOREIGN KEY(name) REFERENCES author(name),
        FOREIGN KEY(pmc_id) REFERENCES paper(pmc_id)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS reference_paper (
        pmid INTEGER,
        pmc_id INTEGER,
        FOREIGN KEY(pmid) REFERENCES reference(pmid),
        FOREIGN KEY(pmc_id) REFERENCES paper(pmc_id)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS mesh_term (
        term TEXT PRIMARY KEY
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS paper_mesh_term (
        pmc_id INTEGER,
        term TEXT,
        FOREIGN KEY(pmc_id) REFERENCES paper(pmc_id),
        FOREIGN KEY(term) REFERENCES mesh_term(term)
        )"""
    )
    conn.commit()
    conn.close()


def prepare_batch_of_papers_for_insert(batch: Iterator[Paper]) -> Tuple[tuple]:
    """Prepare a batch of papers for insertion into the database.

    From each paper extract tuples that will be used to insert into the database:
    - Record into paper table
    - Records into author table
    - Record into author_paper table
    - Records into reference table
    - Record into reference_paper table
    - Records into mesh_term table
    - Record into paper_mesh_term table

    """

    paper_tuple = []
    author_tuple = []
    author_paper_tuple = []
    reference_tuple = []
    reference_paper_tuple = []
    mesh_term_tuple = []
    paper_mesh_term_tuple = []

    for paper in batch:
        paper_tuple.append(
            (
                paper.pmc_id,
                paper.title,
                paper.journal,
                paper.journal_abbreviation,
                paper.year,
                paper.month,
                paper.day,
                paper.pub_date,
                paper.page_numbers,
                paper.doi,
                paper.abstract,
                paper.quick_summary,
                paper.full_xml,
            )
        )
        for author in paper.authors:
            author_tuple.append((author.name, author.affiliation))
            author_paper_tuple.append((author.name, paper.pmc_id))
        for reference in paper.references:
            reference_tuple.append((reference.pmid, reference.citation))
            reference_paper_tuple.append((reference.pmid, paper.pmc_id))
        for mesh_term in paper.mesh_terms:
            mesh_term_tuple.append((mesh_term,))
            paper_mesh_term_tuple.append((paper.pmc_id, mesh_term))

    return (
        paper_tuple,
        author_tuple,
        author_paper_tuple,
        reference_tuple,
        reference_paper_tuple,
        mesh_term_tuple,
        paper_mesh_term_tuple,
    )


def insert_papers_into_db(db_name, papers: Tuple[tuple]):
    """Insert papers into the database.

    Insert a batch of papers into the database as an ACID transaction.
    """
    batch = prepare_batch_of_papers_for_insert(papers)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.executemany(
        """INSERT INTO paper (
        pmc_id,
        title,
        journal,
        journal_abbreviation,
        year,
        month,
        day,
        pub_date,
        page_numbers,
        doi,
        abstract,
        quick_summary,
        full_xml,
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        batch[0],
    )
    c.executemany(
        """INSERT INTO author (
        name,
        affiliation,
        ) VALUES (?, ?)""",
        batch[1],
    )
    c.executemany(
        """INSERT INTO author_paper (
        name,
        pmc_id,
        ) VALUES (?, ?)""",
        batch[2],
    )
    c.executemany(
        """INSERT INTO reference (
        pmid,
        citation,
        ) VALUES (?, ?)""",
        batch[3],
    )
    c.executemany(
        """INSERT INTO reference_paper (
        pmid,
        pmc_id,
        ) VALUES (?, ?)""",
        batch[4],
    )
    c.executemany(
        """INSERT INTO mesh_term (
        term,
        ) VALUES (?)""",
        batch[5],
    )
    c.executemany(
        """INSERT INTO paper_mesh_term (
        pmc_id,
        term,
        ) VALUES (?, ?)""",
        batch[6],
    )
    conn.commit()
    conn.close()


def main(list_of_files: List[str], db_name: str) -> None:
    """Main function."""
    print(db_name)
    create_database_and_tables(db_name)
    for fn in list_of_files:
        print(f"Processing {fn}")
        batch = extract_data_from_file(fn)
        prepared_batch = prepare_batch_of_papers_for_insert(batch)
        insert_papers_into_db(db_name, prepared_batch)


if __name__ == "__main__":
    # glob the XML files in the data directory
    list_of_files = glob(os.path.join(DATA_DIR, "*.xml"))
    main(list_of_files, DB)
