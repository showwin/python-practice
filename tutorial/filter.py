class MyList(list):
    def odd_number(self):
        return List(filter(lambda a: a % 2 == 1, self))

    def times_of(self, n):
        return List(filter(lambda a: a % n == 0, self))

a = List(range(1, 21))
a.odd_number().times_of(3)
