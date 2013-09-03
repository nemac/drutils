import os, json

class NapplMeta:
    def __init__(self, appName):
        self.appName = appName
        self.dir = "/var/nappl/%s" % self.appName
        self.datafile = "/var/nappl/%s/metadata.json" % self.appName
        self.data = {}
        if os.path.exists(self.datafile):
            self.load()
    def load(self):
        with open(self.datafile, 'r') as f:
            self.data = json.loads(f.read())
    def save(self):
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        with open(self.datafile, 'w') as f:
            f.write(json.dumps(self.data, sort_keys=True, indent=2, separators=(',', ': ')))
