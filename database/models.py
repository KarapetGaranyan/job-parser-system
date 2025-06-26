from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    link = Column(Text, nullable=False, unique=True)
    company = Column(String(256))
    salary = Column(String(256))
    source = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vacancy {self.title} at {self.company}>'


def init_db():
    """Инициализация базы данных"""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///vacancies.db')
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


# Создаем глобальную сессию
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///vacancies.db'))
Session = sessionmaker(bind=engine)
