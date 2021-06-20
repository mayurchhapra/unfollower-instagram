import json
from unfollow import Unfollower

f = open('cache/unfollowers.json', 'r')
data = json.loads(f.read())
f.close()

# print(data)

newUserList = []

keys = ('username', 'id')

for user in data:
  if 'username' in user:
    newUserList.append({
      'id': user['id'],
      'username': user['username']
    })
open('cache/formatted_users.json', 'w').write(json.dumps(newUserList, indent=2))

userlist = json.load(open('cache/formatted_users.json'))

length = len(userlist)

start = 0
end = 0
itr = 4
count = 0
instance = Unfollower()
for i in range(int(length/10) + 1):
  start = i
  if start != 0:
    start = end + 1

  # i += 50
  end = i + 50
  if end != 0:
    end = start + 50

  if end > length:
    end = length
  
  if count % itr == 1:
    instance = Unfollower()
  instance.unFollowUser(start, end+1)


  print(start, end)

print(length)

# def unfollowers(start, end):
#   for i in range(start, end):
#     print(userlist[i])

# unfollowers(0, 50)


