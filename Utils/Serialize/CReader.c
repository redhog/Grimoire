#include <Python.h>
#include "pythread.h"
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include "structmember.h"
#include <stdio.h>

#if 0
# define inline
# define DEBUG_READ
# define DEBUG_THREAD
# define DEBUG_TRAVERSE
# define DEBUG_ALLOC
#endif 

/* Call information:

   Functions marked with +interp should be called with the global
   interpreter lock locked, and ones marked with -interp should be
   called with the global interpreter lock released.

   Functions marked with +buf should be called with the buffer locked,
   and ones marked with -buf should be called with the buffer lock
   released.
*/

#define max(x, y) (x > y ? x : y)

#define NEWREADER_BUFFER_MAXSIZE 8192

typedef struct CReader_BufferT CReader_Buffer;

typedef char    (*CReader_Buffer_Init)(CReader_Buffer *buffer); /* +interp */
typedef void    (*CReader_Buffer_Clear)(CReader_Buffer *buffer); /* +interp */
typedef char    (*CReader_Buffer_Advance)(CReader_Buffer *buffer, size_t nr); /* -interp, +buf */
typedef char    (*CReader_Buffer_Cut)(CReader_Buffer *buffer, char *dst, size_t nr); /* -interp, +buf */
typedef char    (*CReader_Buffer_Contains)(CReader_Buffer *buffer, char *buf, size_t len, size_t at); /* -interp, +buf */
typedef ssize_t (*CReader_Buffer_Read)(CReader_Buffer *buffer, size_t nr); /* -interp, +buf */
typedef char    (*CReader_Buffer_Extend)(CReader_Buffer *buffer, size_t nr); /* -interp, +buf */

typedef struct
 {
  CReader_Buffer_Init init;
  CReader_Buffer_Clear clear;
  CReader_Buffer_Advance advance;
  CReader_Buffer_Cut cut;
  CReader_Buffer_Contains contains;
  CReader_Buffer_Read read;
  CReader_Buffer_Extend extend;
 } CReader_BufferType;

/* Buffers are defined as follows:

   ,---pos---.-------len--------.
   +---------+------------------+------------+
   |Garbage  | Data (lookahead) | Free space |
   +---------+------------------+------------+
	     `-----------size----------------'

   This allways holds for a buffer:

   pos < maxsize
   size >= len
   size < len + maxsize

   We also _try_ to make the following hold as often as possible:
   
   len = maxsize

   So that the total buffer size is as near 3 * maxsize as
   possible. Note that this is only possible for some types of buffers
   (sockets).
*/
struct CReader_BufferT
 {
  PyObject_HEAD
  CReader_BufferType *type;
  char *buf;
  off_t pos;
  size_t len;
  size_t size;
  size_t maxsize;
  int fd;
  PyObject *file;
# ifdef WITH_THREAD
   PyThreadState *state;
   PyThread_type_lock lock;
#  ifdef DEBUG_THREAD
    int interplockings;
    int bufferlockings;
#  endif
# endif
 };

static PyObject *unicodedatalookup;
static PyObject *Extension;
static PyObject *Identifier;
static PyObject *Member;
static PyObject *Application;
static PyObject *ParameterName;

# ifdef WITH_THREAD
static inline void CReader_Buffer_lockInterpreter(CReader_Buffer *buffer)
 {
# ifdef DEBUG_THREAD
   fprintf(stderr, "Interpreter lock ["); fflush(stderr);
# endif
  if (buffer->state)
   PyEval_RestoreThread(buffer->state);
  buffer->state = NULL;
# ifdef DEBUG_THREAD
   fprintf(stderr, " --> %i\n", ++buffer->interplockings); fflush(stderr);
# endif
 }

static inline void CReader_Buffer_releaseInterpreter(CReader_Buffer *buffer)
 {
# ifdef DEBUG_THREAD
   fprintf(stderr, "Interpreter lock ]"); fflush(stderr);
# endif
  if (!buffer->state)
   buffer->state = PyEval_SaveThread();
# ifdef DEBUG_THREAD
   fprintf(stderr, " --> %i\n", --buffer->interplockings); fflush(stderr);
# endif
 }

/* FIXME: While waiting on this lock, it would be much better if we
   could have the global interpreter lock unlocked!!! */
static inline void CReader_Buffer_lock(CReader_Buffer *buffer)
 {
# ifdef DEBUG_THREAD
   fprintf(stderr, "Buffer lock %p [", buffer); fflush(stderr);
# endif
  assert(!buffer->state);
  PyThread_acquire_lock(buffer->lock, 1);
# ifdef DEBUG_THREAD
   fprintf(stderr, " --> %i\n", ++buffer->bufferlockings); fflush(stderr);
# endif
 }

static inline void CReader_Buffer_release(CReader_Buffer *buffer)
 {
# ifdef DEBUG_THREAD
   fprintf(stderr, "Buffer lock %p ]", buffer); fflush(stderr);
# endif
  assert(!buffer->state);
  PyThread_release_lock(buffer->lock);
# ifdef DEBUG_THREAD
   fprintf(stderr, " --> %i\n", --buffer->bufferlockings); fflush(stderr);
# endif
 }
# else
#  define CReader_Buffer_lockInterpreter(buffer) do {} while (0)
#  define CReader_Buffer_releaseInterpreter(buffer) do {} while (0)
#  define CReader_Buffer_lock(buffer) do {} while (0)
#  define CReader_Buffer_release(buffer) do {} while (0)
# endif

static char CReader_Buffer_advance(CReader_Buffer *buffer, size_t nr) 
 {
  if (!buffer->type->extend(buffer, nr))
   return 0;
  buffer->pos += nr;
  buffer->len -= nr;
  return 1;
 }

static char CReader_Buffer_cut(CReader_Buffer *buffer, char *dst, size_t nr)
 {
  if (!nr)
   nr = buffer->len;
  else
   if (!buffer->type->extend(buffer, nr))
    return 0;
  strncpy(dst, buffer->buf + buffer->pos, nr);
  buffer->type->advance(buffer, nr);
  return 1;
 }

static char CReader_Buffer_contains(CReader_Buffer *buffer, char *buf, size_t len, size_t at)
 {
  off_t pos;
  off_t rpos;

  for (pos = 0; pos < len; pos++)
   {
    rpos = at + pos;
    if (!buffer->type->extend(buffer, rpos + 1))
     return 0;
    if (buffer->buf[buffer->pos + rpos] != buf[pos])
     return 0;
   }
  return 1;  
 }

static char CReader_Buffer_extend(CReader_Buffer *buffer, size_t nr)
 {
  ssize_t r;

  if (nr <= buffer->len)
   return 1;
  if (buffer->pos >= buffer->maxsize)
   {
    memmove(buffer->buf, buffer->buf + buffer->pos, buffer->len);
    buffer->pos = 0;
   }
  if (   buffer->size > max(nr, buffer->maxsize) + buffer->maxsize
      || buffer->size < max(nr, buffer->maxsize))
   {
    buffer->size = max(nr, buffer->maxsize) + buffer->maxsize;
    buffer->buf = realloc(buffer->buf, buffer->pos + buffer->size);
   }
  while (nr > buffer->len)
   {
    r = buffer->type->read(buffer, nr);
    if (!r || r == -1)
     break;
    buffer->len += r;
   }
  if (nr > buffer->len)
   {
    CReader_Buffer_lockInterpreter(buffer);
    PyErr_SetString(PyExc_IOError, "Premature end of file reached");
    CReader_Buffer_releaseInterpreter(buffer);
    return 0;
   }
  return 1;
 }


static void CReader_MallocedBuffer_clear(CReader_Buffer *buffer)
 {
  free(buffer->buf);
 }


static char CReader_CSocketBuffer_init(CReader_Buffer *buffer)
 {
  PyObject *fileno;
  int fd;
  struct stat st;

  if (!(fileno = PyObject_CallMethod(buffer->file, "fileno", NULL)))
   return 0;
  fd = (int) PyInt_AsLong(fileno);
  Py_DECREF(fileno);
  if (fstat(fd, &st) == -1)
   return 0;
  if (!S_ISSOCK(st.st_mode))
   return 0;
  buffer->fd = fd;
  fflush(stdout);
  return 1;
 }

static ssize_t CReader_CSocketBuffer_read(CReader_Buffer *buffer, size_t nr)
 {
  ssize_t res;
# ifdef DEBUG_READ
   fprintf(stderr, "read(%i) -> "); fflush(stderr);
# endif
  res = recv(buffer->fd,
	     buffer->buf + buffer->pos + buffer->len,
	     max(nr, buffer->maxsize),
	     0);
# ifdef DEBUG_READ
  if (res < 0)
   perror("returned error");
  else
   {
    fprintf(stderr, "%i >", (int) res);
    fwrite(buffer->buf + buffer->pos + buffer->len, res, 1, stderr);
    fprintf(stderr, "<\n");
    fflush(stderr);
   }
# endif
  return res;
 }

static char CReader_PySocketBuffer_init(CReader_Buffer *buffer)
 {
  if (!PyObject_HasAttrString(buffer->file, "recv"))
   return 0;
  return 1;
 }

static ssize_t CReader_PySocketBuffer_read(CReader_Buffer *buffer, size_t nr)
 {
  PyObject *read;
  char *readbuf;
  int readlen;

  CReader_Buffer_lockInterpreter(buffer);

  if (!(read = PyObject_CallMethod(buffer->file, "recv", "i", max(nr, buffer->maxsize))))
   {
    CReader_Buffer_releaseInterpreter(buffer);
    return -1;
   }
  if (PyString_AsStringAndSize(read, &readbuf, &readlen) == -1)
   {
    Py_DECREF(read);
    CReader_Buffer_releaseInterpreter(buffer);
    return -1;
   }
  memcpy(buffer->buf + buffer->pos + buffer->len, readbuf, readlen);
  Py_DECREF(read);

  CReader_Buffer_releaseInterpreter(buffer);
  return readlen;
 }

static char CReader_CFileBuffer_init(CReader_Buffer *buffer)
 {
  PyObject *fileno;
  int fd;

  if (!(fileno = PyObject_CallMethod(buffer->file, "fileno", NULL)))
   return 0;
  fd = (int) PyInt_AsLong(fileno);
  Py_DECREF(fileno);
  buffer->fd = fd;
  return 1;
 }

static ssize_t CReader_CFileBuffer_read(CReader_Buffer *buffer, size_t nr)
 {
  return read(buffer->fd,
	      buffer->buf + buffer->pos + buffer->len,
	      nr - buffer->len);
 }

static char CReader_PyFileBuffer_init(CReader_Buffer *buffer)
 {
  if (!PyObject_HasAttrString(buffer->file, "read"))
   return 0;
  return 1;
 }

static ssize_t CReader_PyFileBuffer_read(CReader_Buffer *buffer, size_t nr)
 {
  PyObject *read;
  char *readbuf;
  int readlen;

  CReader_Buffer_lockInterpreter(buffer);
  if (!(read = PyObject_CallMethod(buffer->file, "read", "i", nr - buffer->len)))
   {
    CReader_Buffer_releaseInterpreter(buffer);
    return -1;
   }
  if (PyString_AsStringAndSize(read, &readbuf, &readlen) == -1)
   {
    Py_DECREF(read);
    CReader_Buffer_releaseInterpreter(buffer);
    return -1;
   }
  memcpy(buffer->buf + buffer->pos + buffer->len, readbuf, readlen);
  Py_DECREF(read);
  CReader_Buffer_releaseInterpreter(buffer);
  return readlen;
 }

static char CReader_PyStringBuffer_init(CReader_Buffer *buffer)
 {
  if (!PyString_Check(buffer->file))
   return 0;
  if (PyString_AsStringAndSize(buffer->file, &buffer->buf, &buffer->size) == -1)
   return 0;
  buffer->len = buffer->size;
  return 1;
 }

static char CReader_PyStringBuffer_extend(CReader_Buffer *buffer, size_t nr)
 {
  if (nr <= buffer->len)
   return 1;
  CReader_Buffer_lockInterpreter(buffer);
  PyErr_SetString(PyExc_IOError, "Premature end of file reached");
  CReader_Buffer_releaseInterpreter(buffer);
  return 0;
 }


static CReader_BufferType CReader_BufferTypes[] = {
 {
  &CReader_CSocketBuffer_init,
  &CReader_MallocedBuffer_clear,
  &CReader_Buffer_advance,
  &CReader_Buffer_cut,
  &CReader_Buffer_contains,
  &CReader_CSocketBuffer_read,
  &CReader_Buffer_extend
 },
 {
  &CReader_CFileBuffer_init,
  &CReader_MallocedBuffer_clear,
  &CReader_Buffer_advance,
  &CReader_Buffer_cut,
  &CReader_Buffer_contains,
  &CReader_CFileBuffer_read,
  &CReader_Buffer_extend
 },
 {
  &CReader_PySocketBuffer_init,
  &CReader_MallocedBuffer_clear,
  &CReader_Buffer_advance,
  &CReader_Buffer_cut,
  &CReader_Buffer_contains,
  &CReader_PySocketBuffer_read,
  &CReader_Buffer_extend
 },
 {
  &CReader_PyFileBuffer_init,
  &CReader_MallocedBuffer_clear,
  &CReader_Buffer_advance,
  &CReader_Buffer_cut,
  &CReader_Buffer_contains,
  &CReader_PyFileBuffer_read,
  &CReader_Buffer_extend
 },
 {
  &CReader_PyStringBuffer_init,
  NULL,
  &CReader_Buffer_advance,
  &CReader_Buffer_cut,
  &CReader_Buffer_contains,
  NULL,
  &CReader_PyStringBuffer_extend
 },
 { NULL, NULL, NULL, NULL, NULL, NULL, NULL }
};


static int CReader_Buffer_traverse(CReader_Buffer *self, visitproc visit, void *arg)
 {
# ifdef DEBUG_TRAVERSE
   fprintf(stderr, "Traverse: %p\n", (void *) self);
# endif
  if (self->file && visit(self->file, arg) < 0)
   return -1;
  return 0;
 }

static int CReader_Buffer_clear(CReader_Buffer *self)
 {
# ifdef DEBUG_ALLOC
   fprintf(stderr, "Clear: %p\n", (void *) self);
# endif
  Py_XDECREF(self->file);
  self->file = NULL;
# ifdef DEBUG_ALLOC
   fprintf(stderr, "Clear done: %p\n", (void *) self);
# endif
  return 0;
 }

static void CReader_Buffer_dealloc(CReader_Buffer* self)
 {
# ifdef DEBUG_ALLOC
   fprintf(stderr, "Dealloc: %p\n", (void *) self);
# endif
  PyObject_GC_UnTrack((PyObject*) self);
  CReader_Buffer_clear(self);
  if (self->type->clear)
   self->type->clear(self);
# ifdef WITH_THREAD
  PyThread_free_lock(self->lock);
  self->lock = NULL;
# endif
  self->ob_type->tp_free((PyObject*)self);
# ifdef DEBUG_ALLOC
   fprintf(stderr, "Dealloc done: %p\n", (void *) self);
# endif
 }

static PyObject *CReader_Buffer_new(PyTypeObject *type, PyObject *args, PyObject *kws)
 {
  CReader_Buffer *self;
  uint maxsize = NEWREADER_BUFFER_MAXSIZE;
  PyObject *file;
  char *argnames[] = {"file", "maxsize", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kws, "O|I", argnames,
				   &file, &maxsize))
   return NULL;
  if (!(self = (CReader_Buffer *) type->tp_alloc(type, 0)))
   return NULL;
# ifdef DEBUG_ALLOC
   fprintf(stderr, "Alloc: %p\n", (void *) self);
# endif
  self->buf = NULL;
  self->pos = 0;
  self->len = 0;
  self->size = 0;
  self->maxsize = maxsize;
  self->type = CReader_BufferTypes;
  Py_INCREF(file);
  self->file = file;
# ifdef WITH_THREAD
  self->state = NULL;
  self->lock = PyThread_allocate_lock();
#  ifdef DEBUG_THREAD
    self->interplockings = 0;
    self->bufferlockings = 0;
#  endif
# endif
  for (self->type = CReader_BufferTypes;
       self->type->init && !self->type->init(self);
       self->type++);
  if (!self->type->init)
   {
    PyErr_SetString(PyExc_TypeError, "Unsupported file-type");
    Py_DECREF(self);
    return NULL;
   }
  PyErr_Clear();
# ifdef DEBUG_ALLOC
   fprintf(stderr, "Alloc done: %p\n", (void *) self);
# endif
  return (PyObject *) self;
 }

static PyTypeObject CReader_Buffer_Type = {PyObject_HEAD_INIT(NULL)};

# ifdef WITH_THREAD
char CReader_Buffer_unlockedAdvance(CReader_Buffer *buffer, size_t nr)
 {
  char res;

  CReader_Buffer_releaseInterpreter(buffer);
  res = buffer->type->advance(buffer, nr);
  CReader_Buffer_lockInterpreter(buffer);
  return res;
 }

char CReader_Buffer_unlockedCut(CReader_Buffer *buffer, char *dst, size_t nr)
 {
  char res;

  CReader_Buffer_releaseInterpreter(buffer);
  res = buffer->type->cut(buffer, dst, nr);
  CReader_Buffer_lockInterpreter(buffer);
  return res;
 }

char CReader_Buffer_unlockedContains(CReader_Buffer *buffer, char *buf, size_t len, size_t at)
 {
  char res;

  CReader_Buffer_releaseInterpreter(buffer);
  res = buffer->type->contains(buffer, buf, len, at);
  CReader_Buffer_lockInterpreter(buffer);
  return res;
 }

char CReader_Buffer_unlockedExtend(CReader_Buffer *buffer, size_t nr)
 {
  char res;

  CReader_Buffer_releaseInterpreter(buffer);
  res = buffer->type->extend(buffer, nr);
  CReader_Buffer_lockInterpreter(buffer);
  return res;
 }
# else
#  define CReader_Buffer_unlockedAdvance(buffer, nr) buffer->type->advance(buffer, nr);
#  define CReader_Buffer_unlockedCut(buffer, dst, nr) buffer->type->cut(buffer, dst, nr);
#  define CReader_Buffer_unlockedContains(buffer, buf, len, at) buffer->type->contains(buffer, buf, len, at);
#  define CReader_Buffer_unlockedExtend(buffer, nr) buffer->type->extend(buffer, nr);
# endif


#define NEWLINE '\n': case '\r'
#define SPACE '\t': case '\x0b': case '\x0c': case ' '
#define WHITESPACE NEWLINE: case SPACE
#define DIGITS '0': case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': case '9'
#define NUMBERLEADCHARS DIGITS: case '+': case '-'
#define NUMBERCHARS NUMBERLEADCHARS: case '.'
#define KNOWNBEGINSEPARATORS '<': case '{': case '['
#define BEGINSEPARATORS KNOWNBEGINSEPARATORS: case '('
#define ENDSEPARATORS ')': case ']': case '}': case '>'
#define SEPARATORS ',': case ':': case '=': case BEGINSEPARATORS: case ENDSEPARATORS

/* +interp, +buf */
static inline ssize_t CReader_readStr_read_unicodeescape(CReader_Buffer *buffer, off_t *pos, char *dst)
 {
  ssize_t len = 0;
  off_t p = *pos;
  PyObject *u;
  PyObject *s;
  char *sbuffer;
  int slength;

  switch (buffer->buf[buffer->pos + p++])
   {
    case 'N':
     p++; /* skip '{' too */
     {
      size_t namestart = p;

      while (1)
       {
	if (!CReader_Buffer_unlockedExtend(buffer, p + 1)) return -1;
	if (buffer->buf[buffer->pos + p] == '}')
	  break;
	p++;
       }
      {
       size_t namelen = p - namestart;
       char name[namelen + 1];

       memcpy(name, buffer->buf + buffer->pos + namestart, namelen);
       name[namelen] = '\0';
       u = PyObject_CallFunction(unicodedatalookup, "s", name);
      }
      p++; /* skip '}' */
      break;
     }
    case 'u':
     {
      char num[5];

      if (!CReader_Buffer_unlockedExtend(buffer, p + 4)) return -1;
      memcpy(num, buffer->buf + buffer->pos + p, 4);
      num[4] = '\0';
      p += 4;

      u = PyUnicode_FromOrdinal((int) strtol(num, NULL, 16));
      break;
     }
    case 'U':
     {
      char num[9];

      if (!CReader_Buffer_unlockedExtend(buffer, p + 8)) return -1;
      memcpy(num, buffer->buf + buffer->pos + p, 8);
      num[8] = '\0';
      p += 8;

      u = PyUnicode_FromOrdinal((int) strtol(num, NULL, 16));
      break;
     }
   }

  if (!u) return -1;
  s = PyUnicode_AsEncodedString(u, "utf", "strict");
  Py_DECREF(u);
  if (!s) return -1;

  if (PyString_AsStringAndSize(s, &sbuffer, &slength) == -1)
   {
    Py_DECREF(s);
    return -1;
   }

  len += slength;
  p++; /* skip '}' */

  if (dst)
   {
    memcpy(dst, sbuffer, slength);
    dst += slength;
    if (!CReader_Buffer_unlockedAdvance(buffer, p)) return -1;
    p = 0;
   }
  Py_DECREF(s);
  *pos = p;
  return len;
 }

/* -interp, +buf */
static inline ssize_t CReader_readStr_read(CReader_Buffer *buffer, char *start, char startlen, char *dst)
 {
  char escaped = 0;
  off_t pos = 0;
  size_t len = 0;
  char c;

  while (1)
   {
    if (!buffer->type->extend(buffer, pos + 1)) return -1;
    c = buffer->buf[buffer->pos + pos];

    if (escaped)
     {
      escaped = 0;
      if (buffer->type->contains(buffer, start, startlen, pos))
       {
	pos += startlen;
	len += startlen;
	continue;
       }
      else 
       switch (c)
	{
	 case '\n':
	  if (dst)
	   {
	    if (!buffer->type->advance(buffer, 1)) return -1;
	    pos = 0;
	    continue;
	   }
	  pos++;
	  continue;
	 case 'a': case 'b': case 'f': case 'n': case 'r': case 't': case 'v':
	  len++;
	  if (!dst)
	   {
	    pos++;
	    continue;
	   }
	  switch (c)
	   {
	    case 'a': *dst = '\a'; break;
	    case 'b': *dst = '\b'; break;
	    case 'f': *dst = '\f'; break;
	    case 'n': *dst = '\n'; break;
	    case 'r': *dst = '\r'; break;
	    case 't': *dst = '\t'; break;
	    case 'v': *dst = '\v'; break;
	   }
	  dst++;
	  if (!buffer->type->advance(buffer, 1)) return -1;
	  pos = 0;
	  continue;
	 case 'N': case 'u': case 'U':
	  {
	   ssize_t ln;

	   CReader_Buffer_lockInterpreter(buffer);
	   ln = CReader_readStr_read_unicodeescape(buffer, &pos, dst);
	   CReader_Buffer_releaseInterpreter(buffer);
	   if (ln == -1) return -1;
	   len += ln;
	   continue;
	  }
	 case 'x':
	  pos++; /* Skip x */
	  len++;
	  if (dst)
	   {
	    char num[3];

	    if (!buffer->type->extend(buffer, pos + 2)) return -1;
	    memcpy(num, buffer->buf + buffer->pos + pos, 2);
	    num[2] = '\0';

	    *((unsigned char *) dst++) = strtol(num, NULL, 16);
	    if (!buffer->type->advance(buffer, pos + 2)) return -1;
	    pos = 0;
	   }
	  else
	   pos += 2;
	  continue;
	 case DIGITS:
	  len++;
	  if (dst)
	   {
	    char num[4];

	    if (!buffer->type->extend(buffer, pos + 3)) return -1;
	    memcpy(num, buffer->buf + buffer->pos + pos, 3);
	    num[3] = '\0';

	    *((unsigned char *) dst++) = strtol(num, NULL, 8);
	    if (!buffer->type->advance(buffer, pos + 3)) return -1;
	    pos = 0;
	   }
	  else
	    pos += 3;
	  continue;
	}
     }
    else
     {
      if (buffer->type->contains(buffer, start, startlen, pos))
       {
	if (!dst)
	 break;
	if (pos) if (!buffer->type->cut(buffer, dst, pos)) return -1;
	if (!buffer->type->advance(buffer, startlen)) return -1;
	break;
       }
      else if (c == '\\')
       {
	if (dst)
	 {
	  if (pos) if (!buffer->type->cut(buffer, dst, pos)) return -1;
	  dst += pos;
	  if (!buffer->type->advance(buffer, 1)) return -1; /* Skip '\' */
	  pos = 0;
	 }
	else
	 pos++;
        escaped = 1;
	continue;
       }
     }
    len++;
    pos++;
   }
  return len;
 }

/* -interp, +buf */
static inline PyObject *CReader_readStr(CReader_Buffer *buffer, char unicode)
 {
  char start[3];
  char startlen = 1;
  size_t len = 0;
  PyObject *res;

  if (!buffer->type->extend(buffer, 2)) return NULL;
  start[0] = start[1] = start[2] = buffer->buf[buffer->pos];
  if (!buffer->type->advance(buffer, 1)) return NULL;
  if (buffer->type->contains(buffer, start, 2, 0))
   {
    startlen = 3;
    if (!buffer->type->advance(buffer, 2)) return NULL;
   }
  if ((len = CReader_readStr_read(buffer, start, startlen, NULL)) == -1) return NULL;
  {
   char buf[len + 1];

   if (CReader_readStr_read(buffer, start, startlen, buf) == -1) return NULL;
   buf[len] = '\0';

   CReader_Buffer_lockInterpreter(buffer);   
   if (unicode)
    res = PyUnicode_Decode(buf, len, "utf", "strict");
   else
    res = PyString_Decode(buf, len, "ascii", "strict");
   CReader_Buffer_releaseInterpreter(buffer);
   return res;
  }
 }

/* -interp, +buf */
static inline PyObject *CReader_readNum(CReader_Buffer *buffer)
 {
  PyObject *res;
  off_t pos = 0;
  char isf = 0;
  char isl = 0;
  char c;

  while (1)
   {
    if (!buffer->type->extend(buffer, pos + 1))
     break;
    c = buffer->buf[buffer->pos + pos];
    switch (c)
     {
      case SEPARATORS:
      case WHITESPACE:
       goto CReader_readNum_end;
      case 'F': case 'f': case 'E': case 'e': case '.':
       isf = 1;
       break;
      case 'L': case 'l':
       isl = 1;
       break;
     }
    pos++;
   }
  CReader_readNum_end:
  {
   char numstr[pos + 1];

   buffer->type->cut(buffer, numstr, pos); /* Nah, we've allready done extend on this, so this *can't* fail */
   numstr[pos] = '\0';

   CReader_Buffer_lockInterpreter(buffer);
   if (isf)
    res = PyFloat_FromDouble(atof(numstr));
   else if (isl)
    res = PyLong_FromString(numstr, NULL, 0);
   else
    res = PyInt_FromString(numstr, NULL, 0);
   CReader_Buffer_releaseInterpreter(buffer);
   return res;
  }
 }

/* -interp, +buf */
static inline ssize_t CReader_readIdentifier_read(CReader_Buffer *buffer, char *dst)
 {
  ssize_t len = 0;
  off_t pos = 0;
  off_t escape = 0;
  char c;

  while (1)
   {
    if (!buffer->type->extend(buffer, pos + 1))
     goto CReader_readIdentifier_read_end;
    c = buffer->buf[buffer->pos + pos];
    if (!escape)
     switch (c)
      {
       case '.': case SEPARATORS: case WHITESPACE:
        goto CReader_readIdentifier_read_end;
       case '\\':
        escape = 1;
	if (dst)
	 {
	  if (pos) if (!buffer->type->cut(buffer, dst, pos)) return -1;
	  dst += pos;
	  if (!buffer->type->advance(buffer, 1)) return -1;
	  pos = 0;
	  continue;
	 }
	pos++;
	continue;
      }
    escape = 0;
    pos++;
    len++;
   }
  CReader_readIdentifier_read_end:
   if (dst)
    if (pos) if (!buffer->type->cut(buffer, dst, pos)) return -1;
   return len;
 }

/* -interp, +buf */
static inline PyObject *CReader_readIdentifier(CReader_Buffer *buffer)
 {
  off_t len = 0;

  if (!(len = CReader_readIdentifier_read(buffer, NULL))) return NULL;
  {
   char identifier[len + 1];

   if (!(len = CReader_readIdentifier_read(buffer, identifier))) return NULL;
   identifier[len] = '\0';

   if (strcmp(identifier, "None") == 0)
    {
     CReader_Buffer_lockInterpreter(buffer);
     Py_INCREF(Py_None);
     CReader_Buffer_releaseInterpreter(buffer);
     return  Py_None;
    }
   else if (strcmp(identifier, "True") == 0)
    {
     CReader_Buffer_lockInterpreter(buffer);
     Py_INCREF(Py_True);
     CReader_Buffer_releaseInterpreter(buffer);
     return Py_True;
    }
   else if (strcmp(identifier, "False") == 0)
    {
     CReader_Buffer_lockInterpreter(buffer);
     Py_INCREF(Py_False);
     CReader_Buffer_releaseInterpreter(buffer);
     return Py_False;
    }
   else
    {
     PyObject *res;
     CReader_Buffer_lockInterpreter(buffer);
     res = PyObject_CallFunction(Extension, "Os", Identifier, identifier);
     CReader_Buffer_releaseInterpreter(buffer);
     return res;
    }
  }
 }

/* -interp, +buf */
static inline PyObject *CReader_readUnicodeOrId(CReader_Buffer *buffer)
 {
  if (   buffer->type->contains(buffer, "u'", 2, 0)
      || buffer->type->contains(buffer, "u\"", 2, 0)
      || buffer->type->contains(buffer, "U'", 2, 0)
      || buffer->type->contains(buffer, "U\"", 2, 0))
   {    
    buffer->type->advance(buffer, 1);
    return CReader_readStr(buffer, 1);
   }
  else
   return CReader_readIdentifier(buffer);
 }

/* +interp */
static inline char CReader_NameLast(PyObject *lst, PyObject *type, PyObject *value, char nameAsString)
 {
  PyObject *wrapped;
  PyObject *name;

  if (!(name = PyList_GetItem(lst, PyList_Size(lst) - 1))) return 0;
  if (nameAsString)
   {
    PyObject *tmp;

    if (!(tmp = PyObject_GetAttrString(name, "value"))) return 0;
    name = PySequence_GetItem(tmp, 1);
    Py_DECREF(tmp);
    if (!name) return 0;
   }
  wrapped = PyObject_CallFunction(Extension, "O(OO)", type, name, value);
  if (nameAsString) { Py_DECREF(name); }
  if (!wrapped) return 0;
  if (PyList_SetItem(lst, PyList_Size(lst) - 1, wrapped) == -1) return 0;
  return 1;
 }

/* +interp, +buf */
static PyObject *CReader_internalRead(CReader_Buffer *buffer, char inParens, char inMemberList)
 {
  PyObject *res;
  PyObject *key = NULL;
  PyObject *value = NULL;
  char multi = inParens && (inParens != '(');
  char separated = 1;
  char c;

  if (inParens == '{')
   res = PyDict_New();
  else
   res = PyList_New(0);
  if (!res) return NULL;
  while (1)
   {
    if (!CReader_Buffer_unlockedExtend(buffer, 1))
     {
      if (!PyObject_IsTrue(res) || inParens)
       goto CReader_internalRead_error;
      else
       goto CReader_internalRead_end;
     }

    c = buffer->buf[buffer->pos];
    switch (c)
     {
      case NEWLINE:
       if (!PyObject_IsTrue(res) || inParens)
	{
	 if (CReader_Buffer_unlockedAdvance(buffer, 1))
	  PyErr_SetString(PyExc_IOError, "APremature end of file reached");
	 continue;
	}
       goto CReader_internalRead_end;
      case ENDSEPARATORS:
       if (inParens)
	if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       goto CReader_internalRead_end;
      case SPACE:
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       continue;
      case ',':
       if (!inParens)
	goto CReader_internalRead_end;
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       multi = 1;
       separated = 1;
       continue;
      case ':':
       if (inParens != '{')
	{
	 PyErr_SetString(PyExc_SyntaxError, "Colon not inside a mapping");
	 goto CReader_internalRead_error;
	}
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       if (!(value = CReader_internalRead(buffer, 0, 0))) goto CReader_internalRead_error;
       if (PyDict_SetItem(res, key, value) == -1) goto CReader_internalRead_error;
       key = value = NULL;
       continue;
      case '=':
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       if (!(value = CReader_internalRead(buffer, 0, 0))) goto CReader_internalRead_error;
       if (!CReader_NameLast(res, ParameterName, value, 1)) goto CReader_internalRead_error;
       continue;
      case '.':
       if (inMemberList)
	{
	 if (!PyObject_IsTrue(res))
	  {
	   PyErr_SetString(PyExc_IOError, "CPremature end of file reached");
	   goto CReader_internalRead_error;
	  }
	 else
	  goto CReader_internalRead_end;
	}
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       if (!(value = CReader_internalRead(buffer, 0, 1))) goto CReader_internalRead_error;
       if (!CReader_NameLast(res, Member, value, 0)) goto CReader_internalRead_error;
       continue;
      case '(':
       if (!separated && inMemberList)
	goto CReader_internalRead_end;
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       if (!(value = CReader_internalRead(buffer, separated ? c : '[', 0))) goto CReader_internalRead_error;
       if (!separated)
	{
	 if (!CReader_NameLast(res, Application, value, 0)) goto CReader_internalRead_error;
	 continue;
	}
       break;
      case KNOWNBEGINSEPARATORS:
       if (!CReader_Buffer_unlockedAdvance(buffer, 1)) goto CReader_internalRead_error;
       if (!(value = CReader_internalRead(buffer, c, 0))) goto CReader_internalRead_error;
       break;
      case '\'': case '"':
       CReader_Buffer_releaseInterpreter(buffer);
       value = CReader_readStr(buffer, 0);
       CReader_Buffer_lockInterpreter(buffer);
       if (!value) goto CReader_internalRead_error;
       break;
      case NUMBERLEADCHARS:
       CReader_Buffer_releaseInterpreter(buffer);
       value = CReader_readNum(buffer);
       CReader_Buffer_lockInterpreter(buffer);
       if (!value) goto CReader_internalRead_error;
       break;
      default:
       CReader_Buffer_releaseInterpreter(buffer);
       value = CReader_readUnicodeOrId(buffer);
       CReader_Buffer_lockInterpreter(buffer);
       if (!value) goto CReader_internalRead_error;
       break;
     }
    separated = 0;
    if (inParens == '{')
     key = value;
    else
     if (PyList_Append(res, value) == -1)
      goto CReader_internalRead_error;
   }
  CReader_internalRead_end:
   if (!multi)
    {
     if (!PyObject_IsTrue(res))
      {
       if (inParens == '(')
	{
	 Py_DECREF(res);
	 res = PyTuple_New(0);
	}
       else
	{
         PyErr_SetString(PyExc_IOError, "GPremature end of file reached");
         goto CReader_internalRead_error;
	}
      }
     else
      {
       if (!(value = PyList_GetItem(res, 0)))
	goto CReader_internalRead_error;
       Py_INCREF(value);
       Py_DECREF(res);
       res = value;
      }
    }
   else if (inParens == '(')
    {
     if (!(value = PyList_AsTuple(res)))
      goto CReader_internalRead_error;
     Py_DECREF(res);
     res = value;
    }
   else if (inParens == '<')
    {
     if (!(value = PyList_AsTuple(res)))
      goto CReader_internalRead_error;
     Py_DECREF(res);
     res = value;
     if (!(value = PyObject_CallObject(Extension, res)))
      goto CReader_internalRead_error;
     Py_DECREF(res);
     res = value;
    }
   PyErr_Clear(); /* Do not propagate EOF if we've come here... */
   return res;
  CReader_internalRead_error:
   Py_DECREF(res);
   return NULL;
 }


static PyObject *CReader_read(PyObject *self, PyObject *args, PyObject *kws)
 {
  PyObject *buffer;
  PyObject *res;
  char *inParens = "\0";
  char *inMemberList = "\0";
  char *argnames[] = {"buffer", "inParens", "inMemberList", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kws, "O!|ss", argnames, (PyObject *) &CReader_Buffer_Type,
				   &buffer, &inParens, &inMemberList))
   return NULL;
  if (!inParens || !inMemberList)
   {
    PyErr_SetString(PyExc_ValueError, "inParens and inMemberList must be one-character strings");
    return NULL;
   }
  CReader_Buffer_lock((CReader_Buffer *) buffer);
  res = CReader_internalRead((CReader_Buffer *) buffer, inParens[0], inMemberList[0]);
  CReader_Buffer_release((CReader_Buffer *) buffer);
  return res;
 }


static PyMethodDef CReader_methods[] = {
 {"read", (PyCFunction) CReader_read, METH_VARARGS | METH_KEYWORDS,
  "Read one object form a buffer."},
 {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC initCReader(void) 
 {
  PyObject* m;

  if (!(m = PyImport_ImportModule("Grimoire.Utils.Serialize.Types"))) return;
  if (!(Extension = PyObject_GetAttrString(m, "Extension"))) return;
  if (!(Identifier = PyObject_GetAttrString(m, "Identifier"))) return;
  if (!(Member = PyObject_GetAttrString(m, "Member"))) return;
  if (!(Application = PyObject_GetAttrString(m, "Application"))) return;
  if (!(ParameterName = PyObject_GetAttrString(m, "ParameterName"))) return;
  Py_DECREF(m);

  if (!(m = PyImport_ImportModule("unicodedata"))) return;
  if (!(unicodedatalookup = PyObject_GetAttrString(m, "lookup"))) return;
  Py_DECREF(m);

  CReader_Buffer_Type.tp_name = "CReader.Buffer";
  CReader_Buffer_Type.tp_basicsize = sizeof(CReader_Buffer);
  CReader_Buffer_Type.tp_dealloc = (destructor) CReader_Buffer_dealloc;
  CReader_Buffer_Type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC;
  CReader_Buffer_Type.tp_doc = "CReader file/socket/string buffer wrapper object";
  CReader_Buffer_Type.tp_traverse = (traverseproc) CReader_Buffer_traverse;
  CReader_Buffer_Type.tp_clear = (inquiry) CReader_Buffer_clear;
  CReader_Buffer_Type.tp_new = CReader_Buffer_new;
  if (PyType_Ready(&CReader_Buffer_Type) < 0)
   return;

  if (!(m = Py_InitModule3("CReader", CReader_methods,
			   "Reader module.")))
   return;

  Py_INCREF(&CReader_Buffer_Type);
  PyModule_AddObject(m, "Buffer", (PyObject *) &CReader_Buffer_Type);
 }
