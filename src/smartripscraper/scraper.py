# Simple python screen scraper for WMATA SmarTrip Card Usage History Data
# Scrapes data from WMATA's website and returns clean SQLite database of SmarTrip card usage history.
# Written by Justin Grimes (@justgrimes) & Josh Tauberer (@joshdata) 

# Works perfectly, uses mechanize to navigate pages and beautiful soup to extract data

# importing libs
import re
from argparse import ArgumentParser
import getpass

import BeautifulSoup
import mechanize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import metadata, Transaction, PurseTransaction

def login(br, username, password):
    br.open("https://smartrip.wmata.com/Account/AccountLogin.aspx") #login page

    br.select_form(name="aspnetForm") #form name
    br["ctl00$MainContent$txtUsername"] = username
    br["ctl00$MainContent$txtPassword"] = password
    response1 = br.submit().read()
    return response1

def getCards(cardList):
    soup = BeautifulSoup.BeautifulSoup(cardList)
    cards = {}
    matchID = re.compile(r"CardSummary.aspx\?card_id=(\d+)")
    
    for card in soup.findAll('a', href=matchID):
        cardID = matchID.findall(card['href'])[0]
        (cardName, cardSerial) =  re.findall(r"(.+) \((\d+)\)", card.find(text=True))[0]
        cards[cardID] = {'cardName': cardName, 'cardSerial': cardSerial}

    return cards

def listCards(cards):
    print "Card ID\tCard Serial\tCard Name"
    for cardID, cardData in cards.items():
        print "\t".join((cardID, cardData['cardSerial'], cardData['cardName']))


def scrapeCard(br, session, cardID, cardSerial):
    #follows link to View Card Summary page for a particular card
    response1 = br.follow_link(url_regex=r"CardSummary.aspx\?card_id=" + cardID).read()
    #follows link to View Usage History page for a particular card
    response1 = br.follow_link(text_regex=r"View Usage History").read()
    br.select_form(name="aspnetForm")
    response1 = br.submit().read()
    br.select_form(name="aspnetForm")
    
    #transaction status either 'All' or 'Successful' or 'Failed Autoloads';
    #'All' includes every succesful transaction including failed (card didn't swipe or error)  
    br["ctl00$MainContent$ddlTransactionStatus"] = ["All"]

    br.submit()
    
    #wmata only started posting data in 2010, pulls all available months
    for year in xrange(2010, 2011+1):
        for month in xrange(1, 12+1):
            time_period = ("%d%02d" % (year, month))
            print "\t", time_period

            #opens link to 'print' version of usage page for easier extraction 
            br.open("https://smartrip.wmata.com/Card/CardUsageReport2.aspx?card_id=" +
                    cardID + "&period=M&month=" + time_period)
            response1 = br.follow_link(text_regex=r"Print Version").read()
           
            #extracts data from html table, writes to csv
            soup = BeautifulSoup.BeautifulSoup(response1)
            table = soup.find('table', {'class': 'reportTable'})
            if table is None:
                continue
            rows = table.findAll('tr')
            it = iter(rows)    
            try:
                while True:
                    cols = it.next().findAll('td')
                    if len(cols) == 0:
                        continue #ignore blank rows
                    rowspan = int(cols[0].get('rowspan', '1'))

                    parsedCols = [td.find(text=True) for td in cols]
                    (sequence, timestamp, description, operator, entry, exit) = parsedCols[0:6]

                    purses = []
                    purses.append(parsedCols[6:9])

                    if rowspan > 1:
                        for i in xrange(1, rowspan):
                            cols = it.next().findAll('td')
                            purses.append([td.find(text=True) for td in cols])

                    txn = Transaction(sequence, timestamp, description, operator, entry, exit, purses)
                    txn.card_id = cardID
                    txn.card_serial = cardSerial
                    session.add(txn)
            except StopIteration:
                pass

            session.commit()

def main():
    parser = ArgumentParser(description='Scrape WMATA SmarTrip usage data.')
    parser.add_argument('username', metavar='USER', help='SmarTrip username')
    parser.add_argument('--password', dest='password', metavar='PASSWORD', help='SmarTrip password')
    parser.add_argument('--card-id', dest='cardID', type=int, help='card ID to fetch, defaults to first card')
    parser.add_argument('--db', dest='outFile', default="smartrip.sqlite", help='SQLite output file') 
    parser.add_argument('--list', dest='list', default=False,
                        action='store_true', help='List available SmarTrip cards')

    args = vars(parser.parse_args())

    if args['password'] is None:
        args['password'] = getpass.getpass('Enter SmarTrip password: ')

    br = mechanize.Browser()
    response = login(br, args['username'], args['password'])
    cards = getCards(response)

    if args['list']:
        listCards(cards)
    else:
        engine = create_engine("sqlite:///" + args['outFile'])
        Session = sessionmaker(bind=engine)
        session = Session()
        metadata.bind = engine
        metadata.create_all()

        if args['cardID'] is not None:
            scrapeCard(br, session, str(args['cardID']), cards[str(args['cardID'])]['cardSerial'])
        else:
            cardID = cards.keys()[0]
            scrapeCard(br, session, str(cardID), cards[cardID]['cardSerial'])
        
if __name__=="__main__":
    main()
