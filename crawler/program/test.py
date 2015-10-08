import time
import networkx as nx


g = nx.Graph()
for i in range(1000):
	g.add_node(i)

s = time.time()
for i in range(100, -100, -1):
	# print(i)
	try:
		if g.node[i]:
			print("exist in list")
	except:
		g.add_node(i, status=0)
e = time.time()
print(e-s)
# print(g.nodes())

tmp = list()
for i in range(1000):
	tmp.append(i)

s = time.time()
for i in range(100, -100, -1):
	# print(i)
	if i not in tmp:
		tmp.append(i)
e = time.time()
print(e-s)
# print(tmp)