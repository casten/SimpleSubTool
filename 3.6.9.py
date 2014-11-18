import base64
from array import array


from duplicity.log import OutFilter
import binascii
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
	N = len(key)
	for i in range(0,256):
		S[i] = i
	j=0
	for i in range(0,256):
		j=(j+S[i] + key[i%N])% 256
		swap(S,i,j)
	return obj({'S':S,'i':0,'j':0})

def getNextByte(rc):
	rc.i = (rc.i+1)%256
	rc.j = (rc.j+rc.S[rc.i])%256
	swap(rc.S,rc.i,rc.j)
	t = (rc.S[rc.i]+rc.S[rc.j])%256
	return rc.S[t]

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

def printByteList(bl):
#	ary = array('B',bl)
	b64 = [];
	for i in range(0,len(bl)):
		b64.append(hex(bl[i]))
	#b64 = base64.b64encode(ary)
	print b64;
	

def testEncrypt(plaintext,key):
	pt = bytearray(plaintext)
	out = []
	ks = []
	rc4State = InitRC4(bytearray(key))
	for i in range(0,len(pt)):
		keyStreamChar = getNextByte(rc4State)
		ks.append(keyStreamChar) 
		out.append((pt[i] ^ keyStreamChar))
		
	printByteList(ks)
	return out

def main():
	rc4State = InitRC4([0x1a,0x2b,0x3c,0x4d,0x5e,0x6f,0x77])
	NineA(rc4State)
	NineB(rc4State)
	NineC(rc4State)
	#drawImage()

	out = testEncrypt('Attack at dawn','Secret')
	printByteList(out)
    
if __name__ == "__main__":
    main()