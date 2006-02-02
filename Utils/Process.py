import os, pty

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

# Should we inherit peopen2.Popen3 or something? But anyway, that
# module is quite flawed, so we'd better do it all ourseleves if
# making an object at some time in teh future...
def popen(binary, args = [], env = None, pathLookUp = True, bindstdinout = True, bindpty = True, preExec = None):
    if bindstdinout:
        if bindpty:
            res = ptyFork()
        else:
            res = pipeFork()
    else:
        res = (os.fork(),)
    if res[0] == 0:
        preExec and preExec()
        execBinary(binary, args, env, pathLookUp)
    return res
