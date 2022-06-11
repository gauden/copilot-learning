from typing import Dict, List


tea = """
Tea temperature breakdown

Black tea: 212 degrees

Green tea: 175 to 180 degrees

White tea: 175 to 180 degrees

Oolong tea: 195 degrees

Pu-erh tea: 212 degrees

Purple tea: 175 to 180 degrees

Herbal tea: 212 degrees

Rooibos tea: 212 degrees
"""


def extract_temps_in_celsius(temp: str) -> List[int]:
    """Extract temperatures in Celsius."""
    temps = []
    for t in temp.split():
        if t.isdigit():
            # convert Fahrenheit to Celsius
            temps.append(int(round((int(t) - 32) * 5 / 9)))
    return temps


def create_dict_of_teas_and_temperature(text: str) -> Dict[str, List[int]]:
    """Create table of teas and temperature."""
    table = dict()
    for line in text.splitlines():
        if line == "" or ":" not in line:
            continue
        tea, temp = line.split(": ")
        temps = extract_temps_in_celsius(temp)
        table[tea] = temps
    return table


def print_table(table: Dict[str, List[int]]):
    """Print table of teas and temperature in a Markdown format with headers 'Tea' and 'Temperature'."""
    print("| Tea | Temperature |")
    print("| --- | --- |")
    for tea, temps in table.items():
        print("| {} | {} |".format(tea, ", ".join(str(t) for t in temps)))


if __name__ == "__main__":
    table = create_dict_of_teas_and_temperature(tea)
    print_table(table)
