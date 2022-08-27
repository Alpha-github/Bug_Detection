import requests
import json
import os
import csv
import re
import base64
import jsonify

token = os.environ["GITHUB_TEST_TOKEN"]

baseURL = "https://api.github.com"

# repo_name = "Alpha-github/image_classification"
repo_name = "apache/superset"

req = requests.Session()
req.auth = ("Alpha-github",token)

def base64_decode_blobs(repo_name,sha):
    res = req.get(baseURL + "/repos/" + repo_name + "/git/blobs/" + sha)
    base64_message = json.loads(res.text)['content']
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return(message)

def annotations(repo_name,shaList):
    changes = {}
    for sha in shaList:
        res = req.get(baseURL + "/repos/" + repo_name + "/commits/"+sha) 
        jres = json.loads(res.text)
        changes[sha]=[]
        changes[sha].append({})
        changes[sha][0]['files'] = jres['files']
        if len(jres['parents'])!=0:
            temp=[]
            for i in range(len(jres['parents'])):
                temp.append(jres['parents'][i]['sha'])
            changes[sha][0]['parents']=temp
        else:
            changes[sha][0]['parents']=[None]
    return changes

def gitTrees(repo_name,sha,show_blob=False):
    res = req.get(baseURL + "/repos/" + repo_name + "/git/trees/" + sha)
    jres = json.loads(res.text)
    tree = jres["tree"]

    for i in range(len(tree)):
        if tree[i]["type"] == "tree":
            tree[i]["files"] = gitTrees(repo_name,tree[i]["sha"])
        if tree[i]["type"] == "blob" and show_blob:
            tree[i]["decrypt_content"] = base64_decode_blobs(repo_name,tree[i]["sha"])
    return tree

def get_commit_history(repo_name,shals=False):
    res = req.get(baseURL + "/repos/" + repo_name + '/commits')
    jres = json.loads(res.text)
    # print(jres)
    ls=[]
    for i in range(len(jres)):
        if(shals):
            shaList.append(jres[i]['sha'])
        # print(gitTrees(repo_name,jres[i]['commit']['tree']['sha']))
        # ls.append({'sha':jres[i]['sha'],'tree':jres[i]['commit']['tree'],'expanded':gitTrees(repo_name,jres[i]['commit']['tree']['sha']),'parents':jres[i]['parents']})
    r = open('t.json','w')
    json.dump(jres,r)
    r.close()
    if shals:
        return shaList

def restructure():
    wf = open("restructured.json","w")
    rf = open("annot3.json")
    jres = json.load(rf)
    keys = list(jres.keys())
    ls = {}
    for key in keys:
        print(key)
        files = jres[key][0]['files']
        for i  in files:
            f_name = i['filename']
            if(f_name not in list(ls.keys()) and i['changes']!=0):
                ls[f_name] = []
                x = {key:i['patch']}
                ls[f_name].append(x)
            elif f_name in list(ls.keys()) and i['changes']!=0:
                x = {key:i['patch']}
                ls[f_name].append(x)
    json.dump(ls,wf)
    rf.close()
    wf.close()


shaList=[]
# a = get_commit_history(repo_name,True)
# annot = annotations(repo_name,a)
# print(annot)
# r = open('annot3.json','w')
# json.dump(annot,r)
# r.close()

restructure()

