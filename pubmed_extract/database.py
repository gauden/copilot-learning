"""
Import sqlite as the database to hold Pubmed searches.
Read the file called "tmp.xml" into an XML object. 
Set up a sqlite database called "pubmed.db" in the data folder.
Recursively run through the first child of the root element of the xml file.
Extract the field names as a nested data structure.
Set up tables in the database that correspond to the elements in the XML file.
Insert the data from the XML file into the database.
"""
import sqlite3
import xml.etree.ElementTree as ET

DB = "./data/pubmed.db"


def create_database(db_name: str) -> None:
    """
    Create a database.
    """
    conn = sqlite3.connect(db_name)
    conn.close()


def create_tables(db_name: str, xml_file: str) -> None:
    """
    Create tables in the database.
    """
    conn = sqlite3.connect(db_name)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    child = root[0]
    table_name = child.tag
    table_columns = [column.tag for column in child]
    table_columns_string = ", ".join(table_columns)
    table_columns_string = "id INTEGER PRIMARY KEY, " + table_columns_string
    conn.execute("CREATE TABLE {} ({})".format(table_name, table_columns_string))
    conn.close()


def insert_data(db_name: str, xml_file: str) -> None:
    """
    Insert data into the database.
    """
    conn = sqlite3.connect(db_name)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for child in root:
        table_name = child.tag
        table_columns = [column.tag for column in child]
        table_columns_string = ", ".join(table_columns)
        table_columns_string = "id INTEGER PRIMARY KEY, " + table_columns_string
        for record in child:
            record_values = [record.find(column.tag).text for column in child]
            record_values_string = ", ".join(record_values)
            record_values_string = "NULL, " + record_values_string
            conn.execute(
                "INSERT INTO {} VALUES ({})".format(table_name, record_values_string)
            )
    conn.close()


def main(db: str = DB, xml_file: str = "./data/tmp.xml") -> None:
    """
    Main function.
    """
    create_database(db)
    create_tables(db, xml_file)
    insert_data(db, xml_file)


if __name__ == "__main__":
    main()
