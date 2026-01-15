from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Instrument(Base):
    __tablename__ = 'instruments'
    
    id = Column(Integer, primary_key=True)
    isin = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    currency = Column(String(3), nullable=False)
    instrument_type = Column(String)
    ticker = Column(String)
    source = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    holdings = relationship("Holding", back_populates="instrument")
    prices = relationship("Price", back_populates="instrument")

class Portfolio(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String)
    currency = Column(String(3), default='HUF')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    holdings = relationship("Holding", back_populates="portfolio")

class Holding(Base):
    __tablename__ = 'holdings'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    quantity = Column(Numeric, nullable=False)
    acquisition_date = Column(Date)
    acquisition_price = Column(Numeric)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="holdings")
    instrument = relationship("Instrument", back_populates="holdings")

class Price(Base):
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    price_date = Column(Date, nullable=False)
    price = Column(Numeric, nullable=False)
    currency = Column(String(3), nullable=False)
    source = Column(String)
    retrieved_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    instrument = relationship("Instrument", back_populates="prices")

class FxRate(Base):
    __tablename__ = 'fx_rates'
    
    id = Column(Integer, primary_key=True)
    rate_date = Column(Date, nullable=False)
    base_currency = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    rate = Column(Numeric, nullable=False)
    source = Column(String)
    retrieved_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class PortfolioValueDaily(Base):
    __tablename__ = 'portfolio_values_daily'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    quantity = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    instrument_currency = Column(String(3), nullable=False)
    fx_rate = Column(Numeric, nullable=False)
    value_huf = Column(Numeric, nullable=False)
    value_huf_usd = Column(Numeric)
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class DataSource(Base):
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    endpoint = Column(String)
    last_success = Column(DateTime(timezone=True))
    last_failure = Column(DateTime(timezone=True))
    notes = Column(Text)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL, ADJUST
    quantity = Column(Numeric, nullable=False)
    price = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(String)
    
    portfolio = relationship("Portfolio")
    instrument = relationship("Instrument")

class ManualPrice(Base):
    __tablename__ = 'manual_prices'
    
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    override_date = Column(Date, nullable=False)
    price = Column(Numeric, nullable=False)
    currency = Column(String(3), nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(String)
    
    instrument = relationship("Instrument")

class WealthCategory(Base):
    __tablename__ = 'wealth_categories'
    
    id = Column(Integer, primary_key=True)
    category_type = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    currency = Column(String(3), nullable=False)
    is_liability = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    values = relationship("WealthValue", back_populates="category", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('category_type', 'name', name='unique_wealth_category'),
    )

class WealthValue(Base):
    __tablename__ = 'wealth_values'
    
    id = Column(Integer, primary_key=True)
    wealth_category_id = Column(Integer, ForeignKey('wealth_categories.id'), nullable=False)
    value_date = Column(Date, nullable=False)
    present_value = Column(Numeric(20, 2), nullable=False)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("WealthCategory", back_populates="values")
    
    __table_args__ = (
        UniqueConstraint('wealth_category_id', 'value_date', name='unique_wealth_value'),
    )

class TotalWealthSnapshot(Base):
    __tablename__ = 'total_wealth_snapshots'
    
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(Date, nullable=False, unique=True)
    portfolio_value_huf = Column(Numeric(20, 2), nullable=False)
    other_assets_huf = Column(Numeric(20, 2), nullable=False)
    total_liabilities_huf = Column(Numeric(20, 2), nullable=False)
    net_wealth_huf = Column(Numeric(20, 2), nullable=False)
    cash_huf = Column(Numeric(20, 2), default=0)
    property_huf = Column(Numeric(20, 2), default=0)
    pension_huf = Column(Numeric(20, 2), default=0)
    other_huf = Column(Numeric(20, 2), default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
