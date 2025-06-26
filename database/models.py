from sqlalchemy import Column, Integer, String, Date, Text, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    salary = Column(String)
    description = Column(Text)
    published_at = Column(Date)
    source = Column(String, index=True)  # Источник вакансии: 'hh' или 'superjob'
    link = Column(String)  # Ссылка на вакансию

Index('ix_vacancy_title_location_company', Vacancy.title, Vacancy.location, Vacancy.company) 