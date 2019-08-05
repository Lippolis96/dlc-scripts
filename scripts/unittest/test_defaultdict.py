from collections import defaultdict

d = defaultdict(list)
d['aaa'] += ['cat']

for k,v in d.items():
    print(k,v)
