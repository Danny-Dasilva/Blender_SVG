

#def recursive(node, list):
#    
# [list of polys]
# pick 1 = Node -> [f] [b]
#
# Node.front = Node[one of f] [f] call recursive
# Node.back = Node[one of b] [b] call recursive


def test_recurse(front, back):
    if len(front) > 1:
        front.pop(0)
        print(front, back)
        test_recurse(front, back)
    elif len(back) > 1:
        back.pop(0)
        print(front, back)
        test_recurse(front, back)
    else: 
        print("done")
        return

front = [1,2,3,4,5]

back = [4,5]

test_recurse(front, back)