import math

for x in range(1, 11):
    print(repr(x).rjust(2), repr(x*x).rjust(3), end=' ')
    print(repr(x*x*x).rjust(4))

for x in range(1, 11):
    print('{0} {1:3d} {2:4d}'.format(str(x).zfill(2), x*x, x*x*x))

print('Your {} is {}'.format('Name', 'showwin'))
print("{0}の親は{1}, {1}の子は{0}.'".format('ヒヨコ', 'ニワトリ'))
hoge = 'rarara'
print("huhuhu{var}".format(var=hoge))

print("PI is approximatey {0:.3f}".format(math.pi))
table = {'Sjoerd': 4127, 'Jack': 4098, 'Dcab': 7678}
for name, phone in table.items():
    print('{0:10}=>{1:10}'.format(name, phone))
