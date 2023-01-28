keyword = input()
message = input()

s = ""
if len(message)>len(keyword):
    w = len(keyword)
    mm = [message[w*i:w*(i+1)] for i in range(len(message)//len(keyword))]
else:
    mm = [message]

for m in mm:
    for k in keyword:
        s+= m[int(k)]

print(s)