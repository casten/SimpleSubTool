class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)

def swap(ary,a,b):
	t = ary[a]
	ary[a] = ary[b]
	ary[b] = t

def InitRC4(key):
	S = [None]*256
	K = [None]*256
	N = len(key)
	for i in range(0,256):
		S[i] = i
		K[i] = key[i%N]
	j=0
	for i in range(0,256):
		j=(j+S[i] + K[i])% 256
		swap(S,i,j)
	return obj({'S':S,'i':i,'j':j})

def getNextByte(rc4State):
	S = rc4State.S
	i = rc4State.i
	j = rc4State.j
	i = (i+1)%256
	j = (j+S[i])%256
	swap(S,i,j)
	t = (S[i]+S[j])%256
	rc4State.i = i
	rc4State.j = j
	return S[t]

def printState(rcState):
	print "RC4 permutation table:"
	stateString = "\t"
	for i in range (0,256):
		stateString += "0x{:02x}".format(rcState.S[i])+','
		if (i%16 == 15):
			stateString+= '\n\t'
		
	print stateString
	print "internal counters:"
	print "\ti={},j={}".format(rcState.i,rcState.j)
	
def NineA(rc4State):
	print "\n\nState after initialization:"
	printState(rc4State)
	
def NineB(rc4State):
	print "\n\nState after 100 bytes generated"
	for i in range(0,100):
		getNextByte(rc4State)
	printState(rc4State)

def NineC(rc4State):
	print "\n\nState after 1000 (900 more) bytes generated"
	for i in range(0,900):
		getNextByte(rc4State)
	printState(rc4State)

def drawImage():
	import Image, ImageDraw

	rc4State = InitRC4([0x1a,0x2b,0x3c,0x4d,0x5e,0x6f,0x77])
	
	im = Image.new("RGB", (1024,1024))
	for x in range(0,1024):
		for y in range (0,1024):
			im.putpixel((x,y),(getNextByte(rc4State),getNextByte(rc4State),getNextByte(rc4State)))

	# write to stdout
	im.save("3.6.9.png", "PNG")

def main():
	rc4State = InitRC4([0x1a,0x2b,0x3c,0x4d,0x5e,0x6f,0x77])
	NineA(rc4State)
	NineB(rc4State)
	NineC(rc4State)
	drawImage()
	
if __name__ == "__main__":
    main()