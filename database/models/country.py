import sqlalchemy as sa

from database.base import Base


class Country(Base):

    __tablename__ = 'country'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, nullable=False)
    iso_code = sa.Column(sa.Text, nullable=False)
    population = sa.Column(sa.Integer, nullable=False)
    total_vaccinated = sa.Column(sa.Integer, default=0)
    percentage_vaccinated = sa.Column(sa.REAL, default=0)

    def __repr__(self) -> str:
        return f'Country({self.name=}, {self.iso_code=}, {self.population}, {self.total_vaccinated})'
