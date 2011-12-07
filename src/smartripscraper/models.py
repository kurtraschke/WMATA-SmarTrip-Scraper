from decimal import *
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer(), primary_key=True)
    card_id = Column(Text())
    card_serial = Column(Text())
    sequence = Column(Integer())
    timestamp = Column(DateTime())
    description = Column(Text())
    operator = Column(Text())
    entry = Column(Text())
    exit = Column(Text())

    purse_transactions = relationship("PurseTransaction", backref="transaction")

    def __init__(self, sequence, timestamp, description, operator, entry, exit, purses):
        super(Transaction, self).__init__()
        self.sequence = int(sequence)
        self.timestamp = datetime.strptime(timestamp, "%m/%d/%y %I:%M  %p")
        self.description = description
        self.operator = operator
        self.entry = entry
        self.exit = exit
        self.purse_transactions = [PurseTransaction(*pt) for pt in purses]

class PurseTransaction(Base):
    __tablename__ = 'purse_transactions'

    id = Column(Integer(), primary_key=True)
    transaction_id = Column(Integer(), ForeignKey('transactions.id'))
    name = Column(Text())
    change = Column(Numeric(precision=6, scale=2))
    balance = Column(Numeric(precision=6, scale=2))

    def __init__(self, purse, change, balance):
        super(PurseTransaction, self).__init__()
        self.name = purse
        self.change = Decimal(change)
        self.balance = Decimal(balance)
