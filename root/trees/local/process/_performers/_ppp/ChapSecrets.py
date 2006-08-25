import csv


# Format
# [client,                  server,  secret,  IP addresses]
# ['ryan@uanywhere.com.au', 'pptpd', 'xyzzy', '192.168.1.2']

class ChapSecrets(object):
    fieldnames = ['client', 'server', 'secret', 'ip']
    def __init__(self, path = '/etc/ppp/chap-secrets'):
        self.path = path
        self.items = {}
        for line in csv.DictReader(open(path, 'r'),
                                   delimiter=' ',
                                   fieldnames = self.fieldnames):
            if not line['client'] or line['client'] == '#': continue
            if line['server'] not in self.items: self.items[line['server']] = {}
            self.items[line['server']][line['client']] = line
    
    def save(self, path = None):
        path = path or self.path
        f = csv.DictWriter(open(path, 'w'), delimiter=' ', fieldnames = self.fieldnames)
        for perserver in self.items.itervalues():
            for item in perserver.itervalues():
                f.writerow(item)

chapSecrets = ChapSecrets()
