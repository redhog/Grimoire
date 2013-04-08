import csv, os, os.path

# Format
# [option, value]
# ['maxfail', 0]

class Peer(object):
    def __init__(self, path = '/etc/ppp/peers/provider', new = False):
        self.path = path
        self.properties = {}
        if not new:
            for line in csv.reader(open(path, 'r'), delimiter=' '):
                if not line or line[0] == '#': continue
                if len(line) < 2: line.append(None)
                self.properties[line[0]] = line[1]
    
    def save(self, path = None):
        path = path or self.path
        f = csv.writer(open(path, 'w'), delimiter=' ')
        f.writerows(self.properties.items())

class Peers(object):
    def __init__(self, path = '/etc/ppp/peers'):
        self.path = path
        self.peers = {}
        for name in os.listdir(self.path):
            self.peers[name] = Peer(os.path.join(self.path, name))
        self.peernames = set(self.peers.keys())
    
    def save(self, path = None):
        path = path or self.path
        for name, peer in self.peers.iteritems():
            peer.save(os.path.join(path, name))
        for name in self.peernames - set(self.peers.keys()):
            os.unlink(os.path.join(path, name))
            self.peernames.remove(name)

peers = Peers()
