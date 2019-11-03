import os
import sys
import pymongo
import subprocess

class GoodDB():
    def __init__(self, db_location):
        self.path = db_location
    
    def startMongo(self, run_option=''):
        ## force restart
        if run_option == "manual":
            os.system("sudo service mongodb stop")
            os.system(f"mongod --config ../mongodb.conf")
            return True
        
        ## check if mongo running, restart if it is.
        service = "mongodb.service"
        p =  subprocess.Popen(["systemctl", "is-active",  service], stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        output = output.decode('utf-8')
        if not err:
            if output == "active":
                return True
            else:
                os.system("sudo service mongodb stop")
                os.system(f"mongod --config ../mongodb.conf")
                return True
        return False
        
        

    def startClient(self):
        self.client = pymongo.MongoClient()
        return self.client

if __name__ == "__main__":
    import systemd.daemon
    db = GoodDB('../data/')
    db.startMongo('manual')
    systemd.daemon.notify('READY=1')
