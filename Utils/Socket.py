import socket

class _fileobject(socket._fileobject):
    # Fix-subclass for slow _get_wbuf_len()
    
    def __init__(self, *arg, **kw):
        super(_fileobject, self).__init__(*arg, **kw)
        self._wbuflen = 0

    def flush(self):
        super(_fileobject, self).flush()
        self._wbuflen = 0

    def write(self, data):
        data = str(data) # XXX Should really reject non-string non-buffers
        if not data:
            return
        self._wbuf.append(data)
        self._wbuflen += len(data)
        if (self._wbufsize == 0 or
            self._wbufsize == 1 and '\n' in data or
            self._wbuflen >= self._wbufsize):
            self.flush()

    def writelines(self, list):
        # XXX We could do better here for very long lists
        # XXX Should really reject non-string non-buffers
        datas = filter(None, map(str, list))
        self._wbuf.extend(datas)
        self._wbuflen += reduce(lambda x, y: x + len(y), datas, 0)
        if (self._wbufsize <= 1 or
            self._wbuflen >= self._wbufsize):
            self.flush()

socket._fileobject = _fileobject
