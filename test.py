from github import Github as gh

g = gh("{Enter Token}")

print(g.get_user().get_repos())

i=1
for repo in g.get_user().get_repos():
    print(i,repo.name)
    i+=1
print(g.search_code("filename:{RepoName} user:{UserName}"))
for j in g.search_code("filename: {RepoName} user:{UserName}",order='desc'):
    print("Hi",j.decoded_content.decode("UTF-8"))
    
print(g.search_issues(""))
for i in g.search_issues(""):
    print(i)



# from difflib import Differ
  
# with open('file1.txt') as file_1, open('file2.txt') as file_2:
#     differ = Differ()
#     print(file_1.readlines())
#     for line in differ.compare(file_2.readlines(), file_1.readlines()):
#         if line[0] in ['-','+']:
#             print(line,end='')
#         else:
#             print("COMMON")
