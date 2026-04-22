"""
Terminal-based data analysis and visualization program for population and
threatened-species data.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import analysis_functions as analysis
import user_csv


DATA_FOLDER = Path("data_files")
COUNTRY_FILE = DATA_FOLDER / "Country_Data.csv"
POPULATION_FILE = DATA_FOLDER / "Population_Data.csv"
SPECIES_FILE = DATA_FOLDER / "Threatened_Species.csv"
OUTPUT_SUMMARY_FILE = DATA_FOLDER / "threatened_summary.csv"
OUTPUT_PLOT_FILE = Path("threatened_species_plot.png")


def load_datasets():
    """
    Load all required CSV datasets.

    Returns:
        tuple: (country_rows, pop_rows, species_rows)
    """
    country_rows = user_csv.read_csv(COUNTRY_FILE)
    pop_rows = user_csv.read_csv(POPULATION_FILE)
    species_rows = user_csv.read_csv(SPECIES_FILE)

    return country_rows, pop_rows, species_rows


def get_user_selection():
    """
    Prompt the user for a UN sub-region and a country name.

    Returns:
        tuple[str, str]: Entered sub-region and country.
    """
    print("ENDG 233 - Final Project Output\n")

    subregion = input("Please enter a UN sub-region (e.g., Polynesia): ").strip()
    country = input("Please enter a country within the specified sub-region: ").strip()

    return subregion, country


def validate_selection(subregion, country, country_rows):
    """
    Validate that the selected country belongs to the selected sub-region.

    Parameters:
        subregion (str): User-entered sub-region.
        country (str): User-entered country.
        country_rows (list[list]): Country metadata rows.

    Returns:
        tuple[bool, list[str]]: Validation result and all countries in the sub-region.
    """
    countries_in_subregion = analysis.get_countries_in_subregion(country_rows, subregion)

    if not countries_in_subregion:
        print("No countries found in that sub-region.\n")
        return False, countries_in_subregion

    normalized_country = country.strip().lower()
    normalized_countries = [name.lower() for name in countries_in_subregion]

    if normalized_country not in normalized_countries:
        print("That country is not in the specified sub-region.\n")
        return False, countries_in_subregion

    return True, countries_in_subregion


def compute_population_and_density(country, pop_rows, country_metadata):
    """
    Compute population change, average population, and current population density.

    Parameters:
        country (str): Selected country.
        pop_rows (list[list]): Population dataset rows.
        country_metadata (dict): Metadata dictionary for countries.

    Returns:
        tuple[float, float, float]: Population change, average population, density.
    """
    metadata = country_metadata.get(country.lower())

    if metadata is None:
        print("No metadata found for that country.\n")
        return 0.0, 0.0, 0.0

    print("\nCalculating change in population and latest density...\n")

    population_series = analysis.get_population_series(pop_rows, country)
    change, average = analysis.population_change_and_average(population_series)

    if population_series.size == 0 or metadata["area"] <= 0:
        density = 0.0
    else:
        density = population_series[0] / metadata["area"]

    print(f"The change in population over the dataset period in {country} is: {int(change)} people")
    print(f"The average population over the dataset period in {country} is: {int(average)} people")
    print(f"The current population density in {country} is: {density} people per sq km\n")

    return change, average, density


def build_threatened_stats(subregion, species_rows, country_metadata, countries_in_subregion):
    """
    Build threatened-species statistics for all countries in the selected sub-region.

    Parameters:
        subregion (str): Selected UN sub-region.
        species_rows (list[list]): Threatened species dataset rows.
        country_metadata (dict): Metadata dictionary with region/subregion/area info.
        countries_in_subregion (list[str]): Countries in the selected sub-region.

    Returns:
        tuple: (
            names,
            averages,
            totals,
            regions,
            subregions,
            species_per_sq_km
        )
    """
    names, matrix = analysis.build_threatened_matrix(species_rows, countries_in_subregion)
    averages, totals = analysis.threatened_averages_and_totals(matrix)

    regions = []
    subregions = []

    for name in names:
        info = country_metadata.get(name.lower(), {})
        regions.append(info.get("region", ""))
        subregions.append(info.get("subregion", subregion))

    species_per_sq_km = []
    for name, total in zip(names, totals):
        area = country_metadata.get(name.lower(), {}).get("area", 0.0)
        species_per_sq_km.append(total / area if area > 0 else 0.0)

    return (
        names,
        averages,
        totals,
        regions,
        subregions,
        np.array(species_per_sq_km),
    )


def save_threatened_summary_csv(names, totals, species_per_sq_km, filename=OUTPUT_SUMMARY_FILE):
    """
    Save a summary CSV of total threatened species and species density.

    Parameters:
        names (list[str]): Country names.
        totals (numpy.ndarray): Total threatened species per country.
        species_per_sq_km (numpy.ndarray): Threatened species density per country.
        filename (Path | str): Output file path.

    Returns:
        None
    """
    output_data = [["Country", "Total Threatened Species", "Species per Sq Km"]]

    for name, total, density in zip(names, totals, species_per_sq_km):
        output_data.append([name, int(total), float(f"{density:.6f}")])

    user_csv.write_csv(str(filename), output_data, overwrite=True)


def print_threatened_tables(regions, subregions, names, averages):
    """
    Print a formatted table of average threatened-species values.

    Parameters:
        regions (list[str]): UN regions.
        subregions (list[str]): UN sub-regions.
        names (list[str]): Country names.
        averages (numpy.ndarray): Average threatened-species values.

    Returns:
        None
    """
    print("The average number of threatened species in each country of the sub-region:\n")
    print(f"{'UN Region':<20}{'UN Sub-Region':<20}{'Country':<20}{'Average'}")

    for region, subregion, name, average in zip(regions, subregions, names, averages):
        print(f"{region:<20}{subregion:<20}{name:<20}{average:.1f}")


def plot_threatened_data(names, totals, species_per_sq_km):
    """
    Create and save a two-subplot figure for threatened-species totals and density.

    Parameters:
        names (list[str]): Country names.
        totals (numpy.ndarray): Total threatened species per country.
        species_per_sq_km (numpy.ndarray): Threatened species density per country.

    Returns:
        None
    """
    if not names:
        return

    x_values = np.arange(len(names))
    figure, (axis_1, axis_2) = plt.subplots(2, 1, figsize=(10, 6))

    axis_1.bar(x_values, totals, label="Total threatened species")
    axis_1.set_xticks(x_values)
    axis_1.set_xticklabels(names, rotation=45, ha="right")
    axis_1.set_title("Total Number of Threatened Species")
    axis_1.set_ylabel("Number of Species")
    axis_1.legend()

    axis_2.bar(x_values, species_per_sq_km, label="Species per sq km")
    axis_2.set_xticks(x_values)
    axis_2.set_xticklabels(names, rotation=45, ha="right")
    axis_2.set_title("Threatened Species Density")
    axis_2.set_xlabel("Country")
    axis_2.set_ylabel("Species / Sq Km")
    axis_2.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT_FILE)
    plt.close(figure)


def run_single_iteration(country_rows, pop_rows, species_rows, country_metadata):
    """
    Execute one full cycle of user input and analysis.

    Parameters:
        country_rows (list[list]): Country dataset rows.
        pop_rows (list[list]): Population dataset rows.
        species_rows (list[list]): Threatened species dataset rows.
        country_metadata (dict): Country metadata dictionary.

    Returns:
        None
    """
    subregion, country = get_user_selection()

    is_valid, countries_in_subregion = validate_selection(subregion, country, country_rows)
    if not is_valid:
        return

    compute_population_and_density(country, pop_rows, country_metadata)

    (
        names,
        averages,
        totals,
        regions,
        subregions,
        species_per_sq_km,
    ) = build_threatened_stats(
        subregion,
        species_rows,
        country_metadata,
        countries_in_subregion,
    )

    save_threatened_summary_csv(names, totals, species_per_sq_km)
    print_threatened_tables(regions, subregions, names, averages)
    plot_threatened_data(names, totals, species_per_sq_km)


def main():
    """
    Control program execution.

    Returns:
        None
    """
    country_rows, pop_rows, species_rows = load_datasets()
    country_metadata = analysis.build_country_metadata(country_rows)

    while True:
        run_single_iteration(country_rows, pop_rows, species_rows, country_metadata)

        again = input("\nWould you like to run the program again? (y/n): ").strip().lower()
        if again != "y":
            print("Thank you for using our program.")
            break


if __name__ == "__main__":
    main()