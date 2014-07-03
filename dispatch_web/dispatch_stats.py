#!/usr/bin/env python

from datetime import datetime

from prettytable import PrettyTable

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from table_def import Poller, TransferLog, ErrorMgr

def connect_to_db(host, db, user, password):
    db_uri = 'mysql://{user}:{password}@{host}/{db}'
    engine = create_engine(db_uri.format(
        user        = user,
        password    = password,
        host        = host,
        db          = db)
        )
    Session = sessionmaker(bind=engine)
    return Session()

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def space(num):
    return ' ' * num

if __name__ == "__main__":

    session = connect_to_db('localhost', 'sems', 'sems', 'sems')

    with open('/var/www/sems/dispatch_web/dispatch_stats.txt', 'w') as f:

        f.write("Stats collected at: %s\n\n" % datetime.now())

        # Number of total transfers
        all_transfers = session.query(TransferLog)
        f.write("Total Transfers: %d\n" % all_transfers.count())

        # total size of all successful transfers
        transfers = all_transfers.filter(TransferLog.status=="Complete").all()
        f.write("Total Sent: %s\n\n" % sizeof_fmt(sum([t.filesize for t in transfers])))

        # Number of successful transfers
        f.write("Successful Transfers: %d\n" % all_transfers.filter(TransferLog.status=="Complete").count())

        # Number of failed transfers
        f.write("Errored Transfers: %d\n\n" % all_transfers.filter(TransferLog.status=="Error").count())

        # Number of total pollere
        pollers = session.query(Poller).order_by(Poller.name)
        f.write("Total pollers: %d\n" % pollers.count())

        # Number of enabled pollers
        f.write("Enabled pollers: %d\n" % pollers.filter(Poller.enabled == True).count())

        # Number of disabled pollers
        f.write("Disabled pollers: %d\n" % pollers.filter(Poller.enabled == False).count())

        # List all servers and statuses

        x = PrettyTable(["Poller", "Success", "Error", "Total Sent"])
        x.align["Poller"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for p in pollers:
            x.add_row([
                p.name,
                all_transfers.filter(TransferLog.name == p.name).filter(TransferLog.status == "Complete").count(),
                all_transfers.filter(TransferLog.name == p.name).filter(TransferLog.status == "Error").count(),
                sizeof_fmt(sum([t.filesize for t in all_transfers.filter(TransferLog.status=="Complete").filter(TransferLog.name == p.name).all()]))
                ])

        f.write('\n' + x.get_string() + '\n')
