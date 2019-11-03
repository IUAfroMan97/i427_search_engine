import os, sys

sys.path.insert(0, '../')
from database_service.db import GoodDB

class Crawler(object):
    def __init__(self, name):
        self.name = name
        self.ppid = os.getppid()

    def setPid(self, pid):
        self.pid = pid

    def connect_db(self):
        gdb = GoodDB("../data/")
        client = gdb.startClient()
        db_client = client.crawler
        #print("DB Status : {}".format(db_client.command("serverStatus")))
        return client, db_client
    
    def disconnect_db(self, db):
        db.close()
        return True