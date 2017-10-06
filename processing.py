import json 
with open('processed-data/academics-tags.json', 'r') as f:
  acads = json.load(f)

toptags = {}
for acad, data in acads.iteritems():
  tags = [(k, v) for k, v in data['tags'].iteritems()]
  tags = sorted(tags, key=lambda x: x[1], reverse=True)
  toptags[acad] = tags[:10]

with open('processed-data/top-tags.json', 'w') as f:
  json.dump(toptags, f, indent=2)
