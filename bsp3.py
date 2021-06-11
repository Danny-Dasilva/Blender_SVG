import numpy as np

class Node:

    def __init__(self,data):
        self.data = data
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.sameList = []
        self.frontList = []
        self.backList = []
        self.front = None
        self.back = None


class Tree:

	def __init__(self):
		self.root = None

	def insert(self,data):
		if(self.root == None):
			self.root = n
		else:
			self.insertNode(self.root,data)

	def insertNode(self,curNode,data):
		n = self.pointify(data)
		
		checking = self.checkPolygonPosition(polygon)

		if(checking=="front"):
			if(curNode.front==None):
				curNode.front = n
				curNode.frontList.append(n.data)
			else:
				curNode.frontList.append(n.data)
				self.insertNode(curNode.front,data)
		elif(checking=="back"):
			if(curNode.back==None):
				curNode.back = n
				curNode.backList.append(n.data)
			else:
				curNode.backList.append(n.data)
				self.insertNode(curNode.back,data)
		elif(checking=="intersect"):
			data1,data2 = self.intersection(curNode,n)
			self.insertNode(curNode,data1)
			self.insertNode(curNode,data2)


	def intersection(self,curNode,n):
		pass


	def checkPolygonPosition(self, polygon):

		normal = np.cross(polygon[2] - polygon[0], polygon[1] - polygon[0])
        p = polygon[0]
        
        positive = []
        negative = []
        other = []
        for i in sort_order:
            polygon = vertices[face_idxs==i]
        
        dot = np.around(np.dot(p-polygon, normal), 10)
        if (np.all(dot >= 0)):
            positive.append(i)
        elif (np.all(dot <= 0)):
            negative.append(i)
        else:
            other.append(i)

        print(positive,negative,other)

	def pointify(self,data):
		points = data.split(" , ")
		point1 = points[0].strip("()")
		point2 = points[1].strip("()")
		x1,y1 = point1.split(", ")
		x2,y2 = point2.split(", ")
		n = Node(data)
		n.x1 = float(x1)
		n.y1 = float(y1)
		n.x2 = float(x2)
		n.y2 = float(y2)
		return n

	def find(self,data):
		return self.findNode(self.root,data)

	def findNode(self,curNode,data):
		if(curNode is None):
			return "Given Line is Not Found!"
		elif(curNode.data==data):
			return curNode
		elif(curNode.data!=data):
			if(data in curNode.frontList):
				self.findNode(curNode.front,data)
			elif(data in curNode.backList):
				self.findNode(curNode.back,data)
			else:
				return "Given Line is Not Found!"

	def fnbOfNode(self,data):
		n = self.find(data)
		print("________",data,"_________")
		try:
			print("Front Lines:",n.frontList)
			print("Back Lines:",n.backList)
		except:
			print(n)

	def frontMostLine(self):
		self.frontLine(self.root)

	def frontLine(self,curNode):
		if(curNode.front is None):
			print("Front Most Line:",curNode.data)
		elif(curNode.front is not None):
			self.frontLine(curNode.front)

	def back2front(self,n):
		if(n is not None):
			self.back2front(n.back)
			print(n.data)
			self.back2front(n.front)

	def print(self):
		self.printGraph(self.root)

	def printGraph(self,curNode):
		if(curNode.data is not None):
			print("_____",curNode.data,"_______")
			print("Front Line Set:",curNode.frontList)
			print("Back Line Set:",curNode.backList)
			print("Same Line Set:",curNode.sameList)
			if(curNode.front is not None):
				self.printGraph(curNode.front)
			if(curNode.back is not None):
				self.printGraph(curNode.back)
			



#________________________________ INPUTS ______________________________________#

def run():
	print("Please Enter Your Inputs: ")
	numOfLines = int(input())
	startLine = int(input())
	dataList = []

	for i in range(0,numOfLines):
		dataList.append(input())

	startData = startLine - 2

	t = Tree()
	t.insert(dataList[startData-1])

	for i in dataList:
		if(i == dataList[startData-1]):
			continue
		else:
			t.insert(i)
	return t

"""def commands(t):
        print("_______________ COMMANDS __________________")
        print("# Print All Lines: Enter 1")
        print("# Print Front Most Line: Enter 2")
        print("# Print Lines From Back to Front: Enter 3")
        print("# Get The Position Of A Given Line: Enter 4")
        print("# End The Programme: Enter 0")
        print("\n")
        while(True):
            print("Please Enter Your Command: ")
            a = int(input())
            if(a == 1):
                t.print()
                print("\n")
            elif(a == 2):
                t.frontMostLine()
                print("\n")
            elif(a == 3):
                t.back2front(t.root)
                print("\n")
            elif(a == 4):
                print("Enter The Line Cordinates: ")
                data = input()
                t.fnbOfNode(data)
                print("\n")
            elif(a == 0):
                break
            else:
                print("Please Enter A Valid Command")
                print("\n")"""



t = run()
#commands(t)


print("_____________ ALL LINES _________________")
t.print()
print("\n")

print("____________ LINES FROM BACK TO FRONT _______________")
t.back2front(t.root)
print("\n")

print("_____________ FRONT MOST LINE_____________")
t.frontMostLine()
print("\n")
