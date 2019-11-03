import sys
sys.path.insert(0, '../')

from database_service.db import GoodDB

db = GoodDB('../data/')

db.startMongo(run_option="manual")