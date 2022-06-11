"""
Given a file name, read the file, identify the lines with a given delimiter,
parse the headers (before the delimiter), and return a dictionary of 
the headers and a list of their values.

Print out the dictionary in the form of a markdown table.
"""

from typing import List, Dict

datafile = "./data.txt"


def load_file(filename: str) -> str:
    """Load a file and return the contents."""
    with open(filename, "r") as f:
        return f.read()


def convert_to_celsius(s: str) -> str:
    """ "Find all numbers in the string and convert them to Celsius."""
    for n in s.split():
        if n.isdigit():
            # convert Fahrenheit to Celsius
            c = int(round((int(n) - 32) * 5 / 9))
            s = s.replace(n, str(c))
    return s


def convert_to_markdown(s: Dict[str, str], headings: List[str]) -> str:
    """Convert a dictionary to a markdown table, transposing rows into columns, with headers."""
    output = "| " + " | ".join(headings) + " |\n"
    output += "| " + " | ".join(["---"] * len(headings)) + " |\n"
    for key, value in s.items():
        output += "| {} | {} |\n".format(key, value)
    return output


def extract_headers_and_values_into_table(lines: List[str]) -> Dict[str, str]:
    headers = []
    values = []
    for line in lines:
        if ":" in line:
            header, value = line.split(": ")
            headers.append(header)
            values.append(value)
    values = [convert_to_celsius(v) for v in values]
    table = dict(zip(headers, values))
    return table


def main(datafile: str) -> None:
    """Main function."""
    data = load_file(datafile)
    lines = data.splitlines()
    table = extract_headers_and_values_into_table(lines)
    output = convert_to_markdown(table, ["Tea", "Temperature"])
    print(output)


if __name__ == "__main__":
    main(datafile)
