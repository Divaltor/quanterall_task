from pandas import Series
from pydantic import BaseModel, Field, validator


class CountrySchema(BaseModel):
    name: str = Field(alias='Country Name')
    iso_code: str = Field(alias='Country Code')
    population: int
    total_vaccinated: int = 0

    class Config:
        allow_population_by_field_name = True
        validate_assignment = True

    @validator('population', pre=True)
    def validate_population(cls, population: int | None) -> int:
        if population is None:
            return 0

        return population

    @validator('total_vaccinated')
    def validate_vaccinated_population(cls, vaccinated_population: int, values: dict) -> int:
        population = values.get('population')

        if vaccinated_population > population:
            raise ValueError("Vaccinated population can't be more than common population.")

        return vaccinated_population

    @classmethod
    def from_pd(cls, row: Series) -> 'CountrySchema':
        """Create country schema object from pandas row."""
        return cls(
            name=row['Country Name'],
            iso_code=row['Country Code'],
            population=row['2020']
        )

    @property
    def vaccinated_percent(self) -> float:
        if self.population > 0:
            return self.total_vaccinated / self.population

        return 0
