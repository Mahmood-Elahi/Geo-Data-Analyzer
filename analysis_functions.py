"""
Analysis functions for country, population, and threatened-species datasets.
"""

import numpy as np


def get_countries_in_subregion(country_rows, subregion_name):
    """
    Return an alphabetically sorted list of countries in a given UN sub-region.

    Parameters:
        country_rows (list[list]): Rows from Country_Data.csv.
        subregion_name (str): Name of the UN sub-region.

    Returns:
        list[str]: Sorted country names in the sub-region.
    """
    target_subregion = subregion_name.strip().lower()
    countries = []

    for row in country_rows[1:]:
        if len(row) < 4:
            continue

        if str(row[2]).strip().lower() == target_subregion:
            countries.append(str(row[0]).strip())

    return sorted(countries)


def build_country_metadata(country_rows):
    """
    Build a metadata dictionary for each country.

    Parameters:
        country_rows (list[list]): Rows from Country_Data.csv.

    Returns:
        dict: Dictionary keyed by lowercase country name with metadata values.
    """
    metadata = {}

    for row in country_rows[1:]:
        if len(row) < 4:
            continue

        country_name = str(row[0]).strip()

        try:
            area = float(row[3])
        except ValueError:
            area = 0.0

        metadata[country_name.lower()] = {
            "country": country_name,
            "region": str(row[1]).strip(),
            "subregion": str(row[2]).strip(),
            "area": area,
        }

    return metadata


def get_population_series(pop_rows, country_name):
    """
    Extract population values for a specific country as a NumPy array.

    Parameters:
        pop_rows (list[list]): Rows from Population_Data.csv.
        country_name (str): Country to search for.

    Returns:
        numpy.ndarray: Population values for the country, or an empty array.
    """
    target_country = country_name.strip().lower()

    for row in pop_rows[1:]:
        if not row:
            continue

        if str(row[0]).strip().lower() == target_country:
            values = []

            for cell in row[1:]:
                try:
                    values.append(float(cell))
                except ValueError:
                    values.append(0.0)

            return np.array(values)

    return np.array([])


def population_change_and_average(pop_series):
    """
    Compute population change and average population.

    Parameters:
        pop_series (numpy.ndarray): Population values for one country.

    Returns:
        tuple[float, float]:
            - population change = first value - last value
            - average population across the dataset period
    """
    if pop_series.size == 0:
        return 0.0, 0.0

    change = pop_series[0] - pop_series[-1]
    average = float(pop_series.mean())

    return change, average


def build_threatened_matrix(species_rows, countries):
    """
    Build a threatened-species matrix for selected countries.

    Parameters:
        species_rows (list[list]): Rows from Threatened_Species.csv.
        countries (list[str]): Countries to include.

    Returns:
        tuple[list[str], numpy.ndarray]:
            - sorted country names
            - N x 4 matrix of threatened plants, fish, birds, and mammals
    """
    wanted_countries = {country.lower() for country in countries}
    names = []
    values = []

    for row in species_rows[1:]:
        if len(row) < 5:
            continue

        country_name = str(row[0]).strip()

        if country_name.lower() not in wanted_countries:
            continue

        row_values = []
        for cell in row[1:5]:
            try:
                row_values.append(float(cell))
            except ValueError:
                row_values.append(0.0)

        names.append(country_name)
        values.append(row_values)

    if not values:
        return [], np.empty((0, 4))

    sort_order = np.argsort(np.array(names, dtype=str))
    sorted_names = [names[index] for index in sort_order]
    sorted_matrix = np.array(values)[sort_order, :]

    return sorted_names, sorted_matrix


def threatened_averages_and_totals(matrix):
    """
    Compute row-wise averages and totals for a threatened-species matrix.

    Parameters:
        matrix (numpy.ndarray): N x 4 matrix of threatened-species counts.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]:
            - row-wise averages
            - row-wise totals
    """
    if matrix.size == 0:
        return np.array([]), np.array([])

    averages = matrix.mean(axis=1)
    totals = matrix.sum(axis=1)

    return averages, totals