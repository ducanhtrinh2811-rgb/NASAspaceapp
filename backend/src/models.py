from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Table

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    documents = relationship('Document', back_populates='category')

document_keywords = Table(
    'document_keywords', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('keyword_id', Integer, ForeignKey('keywords.id'))
)

class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    documents = relationship('Document', secondary=document_keywords, back_populates='keywords')

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    link = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    keywords = relationship('Keyword', secondary=document_keywords, back_populates='documents')
