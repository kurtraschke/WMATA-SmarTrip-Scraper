import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smartripscraper.models import metadata, Transaction, PurseTransaction

engine = create_engine("sqlite:///" + "card.sqlite", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
metadata.bind = engine
metadata.create_all()

entries = session.query(Transaction.entry.label('station')).filter(Transaction.entry != None).filter(Transaction.operator == 'Metrorail')

exits = session.query(Transaction.exit.label('station')).filter(Transaction.exit != None).filter(Transaction.operator == 'Metrorail')

stations = [r[0] for r in entries.union(exits).all()]

out = []

for row_station in stations:
    row = []
    for col_station in stations:
        val = session.query(Transaction).filter(Transaction.operator=='Metrorail').filter(Transaction.entry==row_station).filter(Transaction.exit==col_station).count()
        #print row_station, col_station, val
        row.append(val)
    out.append(row)

print json.dumps(out)
print json.dumps(stations)
