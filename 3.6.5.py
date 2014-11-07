from bitarray import bitarray


def step(array,taps,shift):
	t = 0
	for tap in taps:
		t ^= array[tap]
	for i in range(shift,0,-1):
		array[i]=array[i-1]
	array[0] = t

def xStep(array):
	step(array,[13,16,17,18],18)

def yStep(array):
	step(array,[20,21],21)

def zStep(array):
	step(array,[7,20,21,22],22)

def getMajority(x,y,z):
	return 1 if ((x[0] + y[0] + z[0]) > 1) else 0

def stepRegistersAsNeeded(x,y,z,maj):
	if (x[0] == maj):
		xStep(x)
	if (y[0] == maj):
		yStep(y)
	if (z[0] == maj):
		zStep(z)

def getBit(x,y,z):
	return x[18]^y[21]^z[22]

def nextBit(x,y,z):
	maj = getMajority(x,y,z)
	stepRegistersAsNeeded(x,y,z,maj)
	return getBit(x,y,z)
	
def homeworkProblem():
	x = bitarray('1010101010101010101')
	y = bitarray('1100110011001100110011')
	z = bitarray('11100001111000011110000')
	cs = bitarray(32)
	for i in range (0,32):
		cs[i] = nextBit(x,y,z)
	print 'cs = '+str(cs)
	print 'x = '+str(x)
	print 'y = '+str(y)
	print 'z = '+str(z)

def drawImage():
		import Image, ImageDraw
		xA = bitarray('1010101010101010101')
		yA = bitarray('1100110011001100110011')
		zA = bitarray('11100001111000011110000')
		im = Image.new("1", (1024,1024))
		for x in range(0,1024):
			for y in range (0,1024):
				im.putpixel((x,y),nextBit(xA,yA,zA))

		# write to stdout
		im.save("out.png", "PNG")

def main():
	drawImage()
	
if __name__ == "__main__":
    main()
