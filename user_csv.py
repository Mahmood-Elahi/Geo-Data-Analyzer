"""
CSV utility functions for reading and writing simple comma-separated files.
"""


def _convert_cell(cell):
    """
    Attempt to convert a cell value to a float when possible.

    Parameters:
        cell (str): Raw text from a CSV cell.

    Returns:
        float | str: Numeric value if conversion succeeds, otherwise cleaned text.
    """
    text = cell.strip().lstrip("\ufeff")

    if text == "":
        return ""

    try:
        return float(text)
    except ValueError:
        return text


def read_csv(filename, include_headers=True):
    """
    Read a CSV file into a 2D list.

    Parameters:
        filename (str): Path to the CSV file.
        include_headers (bool): If False, skip the first row.

    Returns:
        list[list]: File contents as a 2D list.
    """
    data = []

    with open(filename, "r", encoding="utf-8-sig") as file:
        first_row = True

        for line in file:
            cells = line.rstrip("\n").split(",")

            if first_row and not include_headers:
                first_row = False
                continue

            row = [_convert_cell(cell) for cell in cells]
            data.append(row)
            first_row = False

    return data


def write_csv(filename, data, overwrite=True):
    """
    Write a 2D list to a CSV file.

    Parameters:
        filename (str): Path to the output CSV file.
        data (list[list]): Rows to write.
        overwrite (bool): If True, overwrite the file; otherwise append.

    Returns:
        None
    """
    mode = "w" if overwrite else "a"

    with open(filename, mode, encoding="utf-8") as file:
        for row in data:
            file.write(",".join(str(value) for value in row) + "\n")