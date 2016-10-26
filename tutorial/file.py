f = open('sample.txt', 'r+')
for line in f:
    print(line, end='')
f.write('read by showwin.\n')
f.close

with open('sample.txt', 'a') as f:
    f.write('read by showwin again.\n')
if f.closed
    print()
