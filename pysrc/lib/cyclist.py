class Cyclist:

    def __init__(self):

        self._p = self
        self._n = self

    @property
    def prev(self):
        return self._p
    @prev.setter
    def prev(self,p):
        self._p._n = p._n
        p._n._p = self._p
        self._p = p
        p._n = self

    @property
    def next(self):
        return self._n

    @next.setter
    def next(self,n):
        self._n._p = n._p
        n._p._n = self._n
        self._n = n
        n._p = self

    def swap_next(self):
        if self._p != self._n:
            self._n._n._p = self  # (c._p = a)
            self._p._n = self._n  # (d._n = b)
            self._n._p = self._p  # (b._p = d)
            self._p = self._n  # (a._p = b)
            self._n._n, self._n = self, self._n._n  # (b._n = a)


    def swap_prev(self):
        self._p.swap_next()

    def exclude(self):
        self._n._p = self._p
        self._p._n = self._n
        self._n = self
        self._p = self

