import requests
import json
import os
import csv
import re
import base64

token = os.environ["GITHUB_TEST_TOKEN"]

baseURL = "https://api.github.com"

repo_name = "Alpha-github/image_classification"
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

def get_issue(repo_name,num_pages=10,issue_num=False):
    if(issue_num):
        res = req.get(baseURL + "/repos/" + repo_name + "/issues/" + str(issue_num))
        jres = json.loads(res.text)
        json_file = open("issue.json",'w')
        json.dump(jres,json_file)
        json_file.close()
    else:
        for i in range(1,num_pages+1):
            res = req.get(baseURL + "/repos/" + repo_name + "/issues",
                    params={"per_page":100,"page":i,"state":"all"})
            jres = json.loads(res.text)
            json_file = open("issue.json",'a')
            json.dump(jres,json_file)
            json_file.close()
    
    # print(jres)

def gitTrees(repo_name,sha,show_blob=False):
    res = req.get(baseURL + "/repos/" + repo_name + "/git/trees/" + sha)
    jres = json.loads(res.text)
    tree = jres["tree"]

    for i in range(len(tree)):
        # print(tree[i]["path"],"<-->",tree[i]["type"])
        if tree[i]["type"] == "tree":
            tree[i]["files"] = gitTrees(repo_name,tree[i]["sha"])
        if tree[i]["type"] == "blob" and show_blob:
            tree[i]["decrypt_content"] = base64_decode_blobs(repo_name,tree[i]["sha"])
    return tree

def commitLog(repo_name, git_trees=False, annotat=False):
    res = req.get(baseURL + "/repos/" + repo_name + "/commits")   # returns all commits made
    jres = json.loads(res.text)
    # print(jres)

    SHAlist =[]

    # if not(os.path.exists(".\info.csv")):  # if info.csv doesn't exist
    #     outfile = open("info.csv", "a+", newline='')
    #     handlew = csv.writer(outfile, delimiter=",")
    #     fields = ["Author","email","CommHash", "CommMsg", "TreeHash", "#Issue"]
    #     handlew.writerow(fields)
    # else:
    #     outfile = open("info.csv", "a+", newline='')
    #     handlew = csv.writer(outfile, delimiter=",")

    outfile = open("info.csv", "w", newline='')
    handlew = csv.writer(outfile, delimiter=",")
    fields = ["Author","email","CommHash", "CommMsg", "TreeHash", "#Issue"]
    handlew.writerow(fields)


    for j in range(len(jres)):
        chash = jres[len(jres)-1-j]["sha"]
        # SHAlist.append(chash)
        thash = jres[len(jres)-1-j]["commit"]["tree"]["sha"]
        committer  = jres[len(jres)-1-j]["commit"]["author"]["name"] # use "author" is needed
        email = jres[len(jres)-1-j]["commit"]["author"]["email"]
        msg = jres[len(jres)-1-j]["commit"]["message"]

        issueList = re.findall("#\d*", msg)
        issueNum=[]

        for i in issueList:
            issueNum.append(int(i[1:]))

        if(len(issueNum) != 0):    # when issue number if present in commit mg, the following shud happen
            handlew.writerow([committer,email,chash, msg, thash, issueNum])
            
            SHAlist.append(chash)

            if(git_trees):
                treeSHA = jres[len(jres)-1-j]["commit"]["tree"]["sha"]
                jres[len(jres)-1-j]["commit"]["tree"]["expanded"] = gitTrees(repo_name,treeSHA,True)

    outfile.close()
    print(SHAlist,len(SHAlist))
    if(git_trees):
        try:
            json_file = open("commit_expand.json", "w")
            json.dump(jres, json_file, indent = 4)
            json_file.close()
            print("Successfully Dumped ! -> Expanded Commit Log")
        except Exception as e:
            print(e)

    if(annotat):
        json_file = open("annotation.json", "w")
        json.dump(annotations(repo_name,SHAlist), json_file, indent = 4)
        json_file.close()
        print("Successfully Dumped ! -> Annotations")


    
commitLog(repo_name,annotat=True)
# print(gitTrees(repo_name,"d545a21be3fa0ac4dbf12ba225316fe434148603"))
# get_issue(repo_name,4)
# annotations(repo_name,"0f5112801b3e1df1aaf378dc5ae680c20bc114ca")
