import json
dic = {'hoge': 123, 'huga': {'nest': 'nested_huga'}}
f = open('sample.json', 'w')
json.dump(dic, f)
f.close
