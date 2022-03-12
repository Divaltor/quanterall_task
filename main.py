import logging

import pandas as pd
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy
from pydantic import ValidationError
from sqlalchemy import insert

from config import PD_CHUNK_SIZE
from database.base import Base, engine
from database.models.country import Country
from schema.models import CountrySchema
from utils import exclude_owid_values

logger = logging.getLogger(__name__)

# We are resetting the database every time (in this case 1 table, so we can do a "drop_all"),
# because the data source does not change, and we can do a "full load" process
Base.metadata.drop_all()
Base.metadata.create_all()

Countries = dict[str, CountrySchema]


def parse_countries(file: str) -> Countries:
    """
    Parse file with countries and population data.

    Args:
        file: path to file which need to parse

    Returns:
        dict with keys as country code and values as parsed country schema (name, code, population)
    """
    df = pd.read_csv(file, usecols=['Country Name', 'Country Code', '2020'])
    parsed_countries = {}

    # Remove NaN values, like population in Eritrea country for 2020 year
    df = df.fillna(0)

    # Exclude OWID_ prefix rows
    df = exclude_owid_values(
        dataframe=df,
        column_name='Country Code'
    )

    # Parse every row into pydantic schema (validation process)
    for _, row in df.iterrows():
        try:
            country = CountrySchema.from_pd(row)
        except ValidationError as ex:
            logger.warning(ex)
            continue

        parsed_countries[country.iso_code] = country

    return parsed_countries


def fill_matches(parsed_countries: Countries):
    """
    Find most actual count for vaccinated population and modify passed data.

    Args:
        parsed_countries: dict with keys as country code and values as parsed country schema (name, code, population)

    Returns:
        The same data with information about vaccinated population
    """
    with pd.read_csv(
        'data/vaccinations.csv',
        chunksize=PD_CHUNK_SIZE,
        usecols=['iso_code', 'date', 'people_fully_vaccinated']
    ) as df:
        chunk: DataFrame | DataFrameGroupBy
        for chunk in df:
            # Remove values with OWID_ prefix
            chunk = exclude_owid_values(chunk, 'iso_code')

            # Convert column values to datetime for ordering by date column
            chunk['date'] = pd.to_datetime(chunk['date'])
            # Order by actual date in descending order
            chunk.sort_values(by='date', ascending=False, inplace=True)
            # Group values by country
            chunk = chunk.groupby(by=['iso_code'])

            # Get first values in group (most fresh date and vaccinated population)
            for iso_code, row in chunk.first().iterrows():
                # noinspection PyTypeChecker
                country = parsed_countries.get(iso_code)

                if country is None:
                    logger.warning(f'Country {iso_code} is not present in dataframe.')
                    continue

                try:
                    country.total_vaccinated = row['people_fully_vaccinated']
                except ValidationError:
                    logger.warning(f'Vaccinated count is missed for country {iso_code}.')

        return parsed_countries


def load_into_database(matches: list[CountrySchema]):
    """Load parsed data into database (bulk insert)."""
    converted_data = [
        {**match.dict(), 'percentage_vaccinated': match.vaccinated_percent}
        for match in matches]

    # We can split it also to small chunks, but in this case we have small data
    stmt = insert(Country).values(converted_data)

    with engine.begin() as conn:
        conn.execute(stmt)


def main():
    # For first, parse file with countries and population
    parsed_countries = parse_countries('data/country_populations.csv')

    # Then, find actual date about vaccinated population and assign this data to parsed countries above
    matches = fill_matches(parsed_countries)

    # Load whole parsed data into database with bulk insert
    load_into_database(list(matches.values()))


if __name__ == '__main__':
    main()
