from flask import Flask, jsonify, request
import json
import argparse
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

parser = argparse.ArgumentParser()

indir = 'processed-data'
acaddir = 'data'

@app.route("/")
def index():
    return "<h2>Academic Relevance Web Service</h2>"

@app.route("/<int:value>")
def multiply(value):
    return jsonify({"Result": str(value * value)})

@app.route('/search/academics/<string:academic>')
def academic(academic):
    with open("../{}/academics-tags.json".format(indir), "r") as f:
        acads = json.load(f)
    with open('../{}/academics-schools.json'.format(acaddir), 'r') as f:
        academics = json.load(f)
    with open('../{}/tags.json'.format(indir), 'r') as f:
        tags = json.load(f)
    with open('../{}/top-tags.json'.format(indir), 'r') as f:
        toptags = json.load(f)
    try:
        with open('search-logs-academics.txt', 'a') as f:
            f.write('{}\n'.format(academic))
    except:
        pass
    acads = [(v['Name'], v['id']) for k, v in academics.iteritems()]
    query = academic
    returned = []
    names = filter(lambda x: query.lower() in x[0].lower(), acads)
    data = []
    for name, _id in names:
        try:
            acadTopTags = {x: tags[x] for (x, _) in toptags[name]}
            data.append({'name': name, 'id': _id, 'top tags': acadTopTags, 'school': academics[_id]['school']})
        except:
            pass
    return jsonify({'data': data})

@app.route('/academics/<string:uuid>')
def academic_page(uuid):
    with open("../{}/academics-tags.json".format(indir), "r") as f:
        acads = json.load(f)
    with open("../{}/academics-schools.json".format(acaddir), "r") as f:
        tags2acads = json.load(f)
    with open('../{}/tags.json'.format(indir), 'r') as f:
        tags2idx = json.load(f)
    name = tags2acads[uuid]['Name']
    school = tags2acads[uuid]['school']
    tags = acads[name]['tags']
    tag_freqs = []
    for tag, freq in tags.iteritems():
        try:
            tag_freqs.append((tag, freq, tags2idx[tag]))
        except:
            pass
    tag_freqs.sort(key = lambda tup : tup[1], reverse=True)
    data = []
    for tag, freq, tag_idx in tag_freqs:
        data.append({'tag': tag, 'freq': freq, 'tag-id': tag_idx})
    return jsonify({'data': data, 'name': name, 'url': tags2acads[uuid]['socUrl'], 'school': school})

@app.route('/search/tag/<string:query>')
def search_tag(query):
    with open('../{}/tags.json'.format(indir)) as f:
        tags = json.load(f)
    with open('../{}/tags2academics.json'.format(indir), 'r') as f:
        tags2acads = json.load(f)
    with open('../{}/top-tags.json'.format(indir), 'r') as f:
        toptags = json.load(f)
    tag2idx = tags
    tags = [(tag, _id) for tag, _id in tags.iteritems()]
    try:
        with open('search-logs-tags.txt', 'a') as f:
            f.write('{}\n'.format(query))
    except:
        pass
    returned_tags = []
    returned_tags = filter(lambda x : query in x[0], tags)
    rtags = [v[0] for v in returned_tags]
    acadRel = {}
    for tag in rtags:
        for academic, data in tags2acads[tag].iteritems():
            try:
                acadRel[academic]['freq'] += data['freq']
            except:
                acadRel[academic] = {'freq': data['freq'], 'id': data['id']}
    acadRel = [(k, v['freq'], v['id'], {x[0]: tag2idx[x[0]] for x in toptags[k]}) for k, v in acadRel.iteritems()]
    acadRel = sorted(acadRel, key=lambda x : x[1], reverse=True)
    data = []
    for name, freq, _id, top_tags in acadRel:
        data.append({'name': name, 'freq': freq, 'id': _id, 'top tags': top_tags})
    return jsonify({'data': data})


@app.route('/tags/<int:id>')
def tag_page(id):
    with open('../{}/tags2academics.json'.format(indir), 'r') as f:
        tags2acads = json.load(f)
    with open('../{}/tags.json'.format(indir), 'r') as f:
        tags = json.load(f)
    with open('../{}/academic-ids.json'.format(indir), 'r') as f:
        acadids = json.load(f)
    idx2tag = {v: k for k, v in tags.iteritems()}
    tag_text = idx2tag[id]
    tag = tags2acads[tag_text]
    tag2acad = [(name, acad['freq'], acadids[name]) for (name, acad) in tag.iteritems()]
    tag2acad.sort(key = lambda tup : tup[1], reverse=True)
    data = []
    for name, freq, _id in tag2acad:
        data.append({'name': name, 'id': _id, 'freq':freq})
    return jsonify({'data': data, 'tag': tag_text})

@app.route('/path/capability', methods=['POST'])
def capability_click():
    try:
        with open('../{}/tags.json'.format(indir), 'r') as f:
            tags = json.load(f)
        req = request.get_json()
        print req
        with open('click-logs-capabilities.txt', 'a') as f:
            f.write('\n{}, {}, {}'.format(req['query'], req['tag'], req['id']))
        return jsonify({"post": "successful"})
    except Exception as e:
        print e
        return jsonify({"post": "unsuccessful"})

@app.route('/path/academic', methods=['POST'])
def academic_click():
    try:
        with open('../{}/academic-ids.json'.format(indir), 'r') as f:
            acads = json.load(f)
        req = request.get_json()
        with open('click-logs-academics.txt', 'a') as f:
            f.write('\n{}, {}, {}'.format(req['query'], req['academic'], req['academicId']))
        return jsonify({"post": "successful"})
    except Exception as e:
        print e
        return jsonify({"post": "unsuccessful"})

if __name__ == "__main__":
    app.run(debug=True)
