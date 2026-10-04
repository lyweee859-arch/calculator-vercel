import os
from functools import lru_cache

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from .models import Base, CalculationHistory, from_row


def normalize_database_url(value):
    if not value:
        raise ValueError("DATABASE_URL is required")
    if value.startswith("postgresql+psycopg://"):
        return value
    if value.startswith("postgresql://"):
        return "postgresql+psycopg://" + value[len("postgresql://"):]
    if value.startswith("postgres://"):
        return "postgresql+psycopg://" + value[len("postgres://"):]
    raise ValueError("DATABASE_URL must be a PostgreSQL connection URL")


@lru_cache(maxsize=1)
def _engine_for_url(url):
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"prepare_threshold": None},
    )


def get_engine():
    url = normalize_database_url(os.environ.get("DATABASE_URL"))
    return _engine_for_url(url)


def initialize_database():
    Base.metadata.create_all(get_engine())


def save_calculation(expression, result):
    with Session(get_engine()) as session, session.begin():
        record = CalculationHistory(expression=expression, result=result)
        session.add(record)
        session.flush()
        return record.id


def list_history():
    with Session(get_engine()) as session:
        records = session.scalars(
            select(CalculationHistory).order_by(CalculationHistory.id.desc())
        ).all()
        return [from_row(record) for record in records]


def delete_history_record(record_id):
    with Session(get_engine()) as session, session.begin():
        record = session.get(CalculationHistory, record_id)
        if record is None:
            return False
        session.delete(record)
        return True


def clear_history():
    with Session(get_engine()) as session, session.begin():
        result = session.execute(delete(CalculationHistory))
        return result.rowcount or 0
