from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

import config

engine = create_engine(config.DATABASE_URI, future=True)

Base = declarative_base(engine)
