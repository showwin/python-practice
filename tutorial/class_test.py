class MyClass(object):
    def __init__(self):
        self.data = []

    def add(self, x):
        self.data.append(x)

    def add_twice(self, x):
        self.add(x)
        self.add(x)


class DerivedMyClass(MyClass):

    def __init__(self):
        super().__init__()
        self.name = 'showwin'

    def rename(self, new_name):
        self.name = new_name

    def _with_huhu(self):
        print(self.name + 'huhu')

    def with_huhu(self):
        print(self.name + 'huhu')


def reverse(data):
    for index in range(len(data)-1, -1, -1):
        yield data[index]
