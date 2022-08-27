import requests
import json
import os
import csv
import re
import base64

token = os.environ["GITHUB_TEST_TOKEN"]

baseURL = "https://api.github.com"

# repo_name = "Alpha-github/image_classification"
repo_name = "apache/superset"

req = requests.Session()
req.auth = ("Alpha-github",token)



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

def base64_decode_blobs(repo_name,sha):
    res = req.get(baseURL + "/repos/" + repo_name + "/git/blobs/" + sha)
    base64_message = json.loads(res.text)['content']
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return(message)

def get_timeline(repo_name,issue_num):
    res = req.get(baseURL + "/repos/" + repo_name + "/issues/" + str(issue_num)+ "/timeline")
    jres = json.loads(res.text)
    sha = jres[0]['sha']
    print(sha)


def get_issue(repo_name,num_pages=10,issue_num=False):
    issue_num = []
    if(issue_num):
        res = req.get(baseURL + "/repos/" + repo_name + "/issues/" + str(issue_num))
        jres = json.loads(res.text)
        
        issue_num.append(jres["number"])

        json_file = open("issue2.json",'w')
        json.dump([jres],json_file)
        json_file.close()
    else:
        json_file = open("issue2.json",'w')
        json_file.close()
        json_file = open("issue2.json",'a')
        issues=[]
        for i in range(1,num_pages+1):
            res = req.get(baseURL + "/repos/" + repo_name + "/issues",
                    params={"per_page":100,"page":i,"state":"all"})
            jres = json.loads(res.text)

            for obj in jres:
                issue_num.append(obj['number'])
            issues.extend(jres)

        json.dump(issues,json_file)
        json_file.close()

    return issue_num


def gitTrees(repo_name,sha,show_blob=False):
    res = req.get(baseURL + "/repos/" + repo_name + "/git/trees/" + sha)
    jres = json.loads(res.text)
    # print(jres)
    tree = jres["tree"]

    for i in range(len(tree)):
        # print(tree[i]["path"],"<-->",tree[i]["type"])
        if tree[i]["type"] == "tree":
            tree[i]["files"] = gitTrees(repo_name,tree[i]["sha"])
        if tree[i]["type"] == "blob" and show_blob:
            tree[i]["decrypt_content"] = base64_decode_blobs(repo_name,tree[i]["sha"])
    return tree

# print(gitTrees(repo_name,"d545a21be3fa0ac4dbf12ba225316fe434148603"))
get_issue(repo_name,2)
# print(annotations(repo_name,["3e3fbccdcb03faaf484b5077827fa48d3183f629"]))
# get_timeline(repo_name,20129)
