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
    location = Column(String(256))  # Добавлено поле локации
    description = Column(Text)  # Добавлено поле описания
    requirements = Column(Text)  # Добавлено поле требований
    source = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vacancy {self.title} at {self.company}>'

    def to_dict(self):
        """Конвертация объекта в словарь"""
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
            'company': self.company,
            'salary': self.salary,
            'location': self.location,
            'description': self.description,
            'requirements': self.requirements,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db():
    """Инициализация базы данных"""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///vacancies.db')
    engine = create_engine(db_path)

    # Создаем все таблицы
    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)


# Создаем глобальную сессию
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///vacancies.db'))
Session = sessionmaker(bind=engine)