import Grimoire.Utils

class A(Grimoire.Utils.EMRO):
    def a_post(foo, self):
        print "A post"
    def a_pre(foo, self):
        print "A pre"
        A.__super__('foo', foo, self)()
    foo = Grimoire.Utils.EMROMethod([a_pre], [a_post])

class B(A):
    def b_post(foo, self):
        print "B post"
        B.__super__('foo', foo, self)()
    def b_pre(foo, self):
        print "B pre"
        B.__super__('foo', foo, self)()
    foo = Grimoire.Utils.EMROMethod([b_pre], [b_post])

class C(A):
    def c_post(foo, self):
        print "C post"
        C.__super__('foo', foo, self)()
    def c_pre(foo, self):
        print "C pre"
        C.__super__('foo', foo, self)()
    foo = Grimoire.Utils.EMROMethod([c_pre], [c_post])

class D(B, C):
    def d_post(foo, self):
        print "D post"
        D.__super__('foo', foo, self)()
    def d_pre(foo, self):
        print "D pre"
        D.__super__('foo', foo, self)()
    foo = Grimoire.Utils.EMROMethod([d_pre], [d_post])

    
class E(D):
    def foo(foo, self):
        print "E pre"
        E.__super__('foo', foo, self)()
    foo = Grimoire.Utils.EMROMethod([foo])
