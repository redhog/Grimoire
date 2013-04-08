import os, pty, select, sys

def execBinary(binary, args = [], env = None, pathLookUp = True):
    if pathLookUp:
        if env is not None:
            os.execvpe(binary, args, env)
        else:
            os.execvp(binary, args)
    else:
        if env is not None:
            os.execve(binary, args, env)
        else:
            os.execv(binary, args)

def ptyFork():
    pid, fd = pty.fork()
    return (pid, os.fdopen(fd, 'rw'))

def pipeFork():
    stdinchild, stdinparent = os.pipe()
    stdoutparent, stdoutchild = os.pipe()
    stderrparent, stderrchild = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.dup2(stdinchild, 0)
        os.dup2(stdoutchild, 1)
        os.dup2(stderrchild, 2)
    os.close(stdinchild)
    os.close(stdoutchild)
    os.close(stderrchild)
    if pid == 0:
        return (pid, os.fdopen(0, 'r'), os.fdopen(1, 'w'), os.fdopen(2, 'w'))
    else:
        return (pid, os.fdopen(stdinparent, 'w'), os.fdopen(stdoutparent, 'r'), os.fdopen(stderrparent, 'r'))

def nullFork():
    stdinchild = open('/dev/zero', 'r')
    stdoutchild = open('/dev/null', 'w')
    stderrchild = open('/dev/null', 'w')
    pid = os.fork()
    if pid == 0:
        os.dup2(stdinchild.fileno(), 0)
        os.dup2(stdoutchild.fileno(), 1)
        os.dup2(stderrchild.fileno(), 2)
    stdinchild.close()
    stdoutchild.close()
    stderrchild.close()
    if pid == 0:
        return (pid, os.fdopen(0, 'r'), os.fdopen(1, 'w'), os.fdopen(2, 'w'))
    else:
        return (pid,)

# Should we inherit peopen2.Popen3 or something? But anyway, that
# module is quite flawed, so we'd better do it all ourseleves if
# making an object at some time in teh future...
def popen(binary, args = [], env = None, pathLookUp = True, nullstdinout = False, bindstdinout = True, bindpty = True, preExec = None):
    if nullstdinout:
        res = nullFork()
    else:
        if bindstdinout:
            if bindpty:
                res = ptyFork()
            else:
                res = pipeFork()
        else:
            res = (os.fork(),)
    if res[0] == 0:
        try:
            preExec and preExec()
            execBinary(binary, args, env, pathLookUp)
        except:
            stderr = os.fdopen(2, 'w')
            stderr.write("Unable to execute binary")
            stderr.flush()
            os.close(0)
            os.close(1)
            os.close(2)
            os._exit(1)
    return res

def system(binary, args = [], env = None, pathLookUp = True, preExec = None, onlyOkStatus = False):
    cpid, cstdin, cstdout, cstderr = popen(binary = binary, args = args, env = env, pathLookUp = pathLookUp, preExec = preExec, bindpty = False)
    poll = select.poll()
    cstdinfh = cstdout.fileno()
    cstdoutfh = cstdout.fileno()
    cstderrfh = cstderr.fileno()
    poll.register(cstdinfh, select.POLLOUT | select.POLLERR)
    poll.register(cstdoutfh, select.POLLIN | select.POLLHUP | select.POLLERR)
    poll.register(cstderrfh, select.POLLIN | select.POLLHUP | select.POLLERR)
    res = {cstdoutfh:'', cstderrfh:''}
    handles = {cstdinfh:cstdin, cstdoutfh:cstdout, cstderrfh:cstderr}
    names = {cstdinfh:'in', cstdoutfh:'out', cstderrfh:'err'}
    fds = 2
    while fds:
        for fd, event in poll.poll():
            if event & select.POLLIN:
                res[fd] += os.read(fd, 1)
            elif event & select.POLLHUP:
                poll.unregister(fd)
                fds -= 1
            elif event & select.POLLOUT or event & select.POLLERR:
                raise Exception(names[fd], event, res[cstdoutfh], res[cstderrfh])
    cstdin.close()
    cstdout.close()
    cstderr.close()
    status = os.waitpid(cpid, 0)[1]
    if onlyOkStatus:
        if status != 0:
            raise Exception(status, res[cstdoutfh], res[cstderrfh])
        else:
            return res[cstdoutfh], res[cstderrfh]
    return status, res[cstdoutfh], res[cstderrfh]
    
