import os

if hasattr(os, 'lstat'):
    lstat = os.lstat
else:
    lstat = os.stat

if hasattr(os, 'lchown'):
    lchown = os.lchown
else:
    lchown = os.chown
