#!/usr/bin/env python

import curses
import sys,signal
from debian.deb822 import OrderedSet
import time,math


WIDTH = 26*4 + 5
glob = {
     'ciphertextInfo':{
        'dists':{},
        'order':[],
        'data':''
     },
     'englishInfo':{
        'dists':{},
        'order':[],
        'dictionary':{}
     },
    'key':{
           'map':{},
     },
    'windows':{},
    'best':{
            'score':0,
            'map':{},
            'words':[]
    },
    'screen':None
}

def main():
        if (len(sys.argv) < 2):
                print "need to pass ciphertext"
                sys.exit(-1)
        ciphertext = sys.argv[1]
        stdscr = initCurses()
        x,y = stdscr.getmaxyx()
        if x < 68 or y < 226:
            stdscr.move(0,0)
            stdscr.refresh()
            curses.endwin()
            uninitCurses(stdscr,True)
            stdscr.move(1,0) 
            sys.exit(-1)
        glob['englishInfo']['dictionary'] = makeDict()
        glob['screen'] = stdscr

        def signal_handler(signal, frame):
            uninitCurses(stdscr)
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)

        run(stdscr,ciphertext)

def initCurses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(1)
    stdscr.keypad(1)
    return stdscr

def uninitCurses(scr,err):
    try:
        scr.keypad(0)
        curses.nocbreak()
        curses.echo(True)
        scr.move(66,0) #move to key window
        scr.refresh()
        curses.endwin()
    except:
        if (err):
           print("Please resize terminal to a minimum 68,226\n")
#

def debug(str):
#    glob['windows']['debugWin'].clear()
    glob['windows']['debugWin'].addstr(str)
    refreshWins()

def makeWindows(screen):
    begin_x = 5; 
    begin_y = 1
    height = 5; 
    width = WIDTH

    t_border = curses.newwin(height*3, width, begin_y, begin_x)
    t_border.border() 
    t_border.refresh()

    translated = curses.newwin(height*3-2, width-2, begin_y+1, begin_x+1)
    translated.refresh()


    keymap = curses.newwin(100, width-2, begin_y+17, begin_x+1)
    keymap.refresh()

    b_keymap = curses.newwin(3, width, begin_y+16, begin_x)
    b_keymap.border()
    b_keymap.refresh()

    stats = curses.newwin(height, width, begin_y+20, begin_x)
    stats.border()
    stats.refresh()
    
    standardFreqWin = curses.newwin(height, width, begin_y+27, begin_x)
    standardFreqWin.border() 
    standardFreqWin.refresh()
    
    b_digramWin = curses.newwin(12, width, begin_y+33, begin_x)
    b_digramWin.border() 
    b_digramWin.refresh()

    digramWin = curses.newwin(10, width-2, begin_y+34, begin_x+1)
    digramWin.refresh()

    b_debugWin = curses.newwin(20, width*2, begin_y+45, begin_x)
    b_debugWin.border()
    b_debugWin.refresh()

    global glob
    debugWin = curses.newwin(18, width*2-2, begin_y+46, begin_x+1)
    debugWin.scrollok(True)
    debugWin.refresh()

    
    wins = glob['windows']
    wins['debugWin'] = debugWin
    wins['stats'] = stats
    wins['stdFreq'] = standardFreqWin
    wins['translated'] = translated
    wins['keymap'] = keymap
    wins['b_keymap'] = keymap
    wins['gramInfo'] = digramWin

def refreshWins():
    for win in glob['windows']:
        glob['windows'][win].refresh()

def drawDist(win,dist):
    sortedDist = sorted(dist,key=lambda key: dist[key],reverse=True)
    i=0
    for v in sortedDist:
        win.addstr(1,2+i*4,v)
        win.addstr(3,2+i*4,'{:1.2g}'.format(100*dist[v]))
        i+=1
    win.hline(2,1,curses.ACS_HLINE,WIDTH-2)


def countDist():
    counts = {}
    ciphertext = glob['ciphertextInfo']['data']
    textLen = len(ciphertext)
    #init counts to 0
    for i in range(ord('A'),ord('Z')):
        counts[chr(i)] = 0

    #count letter frequencies in ciphertext
    for c in ciphertext:
        if c not in counts:
            counts[c] = 0
        counts[c] += 1
    dists = {}
    for c in counts:
        dists[c] = float(counts[c])/textLen
    return dists

def getCiphertextInfo(ciphertext):
    global glob
    glob['ciphertextInfo']['data'] = ciphertext.upper()
    stdDist = getStandardDist()
    glob['englishInfo']['dists'] = stdDist
    glob['englishInfo']['order'] = sorted(getStandardDist(),key=lambda key: stdDist[key],reverse=True)
    cipherDist = countDist()
    glob['ciphertextInfo']['dists'] = cipherDist
    glob['ciphertextInfo']['order'] = sorted(cipherDist,key=lambda key: cipherDist[key],reverse=True)

def translate():
    subst = ''
    ciphertext = glob['ciphertextInfo']['data']
    keyMap = glob['key']['map']
    for i in range(0,len(ciphertext)):
        c = ciphertext[i]
        subst += keyMap[c]
    return subst

def getStandardDist():
    return {'E':.12, 'T':.091, 'A':.082, 'O':.075, 'I':.070, 'N':.068, 'S':.063, 'H':.061, 'R':.060, 'D':.043, 'L':.040,
            'U':.028, 'C':.028, 'W':.024, 'M':.024, 'F':.022, 'Y':.020, 'G':.020, 'P':.019, 'B':.015, 'V':.010, 'K':.008,
            'X':.002, 'J':.002, 'Z':.001, 'Q':.001}
    
def drawStandardDist(distWin):
    standDist = getStandardDist()
    drawDist(distWin,standDist)

def updateDigramWin(digrams,trigrams):
    win = glob['windows']['gramInfo']
    win.clear()
    win.addstr('Common digrams: th, he, in, er, an\nMessage digrams:'+str(digrams)+'\nCommon Trigrams: the, and, tha, ent, ing\n'+'Message trigrams:'+str(trigrams))


def displayStats(scr,dists,digrams,trigrams):
    wStats = glob['windows']['stats']
    wFreq = glob['windows']['stdFreq']
    drawDist(wStats,dists)
    drawStandardDist(wFreq)
    updateDigramWin(digrams,trigrams)
    refreshWins()


def displayTranslated():
    translated = translate()
    win = glob['windows']['translated']
    win.addstr(1,0,translated)
    win.refresh()

def getCipherTextDists():
    win = glob['windows']['stats']
    i=0
    for c in glob['ciphertextInfo']['order']:
        win.addstr(1,i*4+2,key[c])
        i+=1
    win.refresh()

def getKeyValuesOrder():
    win = glob['windows']['keymap']
    order = ''
    keyMap = glob['key']['map']
    for c in glob['ciphertextInfo']['order']:
        order+= keyMap[c]
    return order
    
def displayKeyValues():
    win = glob['windows']['keymap']
    i=0
    keyOrder = getKeyValuesOrder()
    for c in keyOrder:
         win.addstr(0,i*4+1,c)
         i+=1
    win.refresh()

def initKey():
    global glob
    englishOrder = glob['englishInfo']['order']
    cipherOrder =  glob['ciphertextInfo']['order']
    keyMap = {}
    for i in range(0,len(englishOrder)):
        keyMap[englishOrder[i].upper()] = englishOrder[i].upper()
    glob['key']['map'] = keyMap


def keyFromValue(map,val):
    for k in map:
        if map[k] == val:
            return k 
    return None

def replaceChar(index,iNewChar):
    keyMap = glob['key']['map']
    newVal = chr(iNewChar).upper()
    oldVal = keyMap[glob['ciphertextInfo']['order'][index].upper()].upper()
    repKey = keyFromValue(keyMap, oldVal)
    patchKey = keyFromValue(keyMap, newVal)
    debug('oldVal={}, newVal={}, repKey={}, patchKey={}\n'.format(oldVal,newVal,repKey,patchKey))
    keyMap[repKey] = newVal
    keyMap[patchKey] = oldVal
    refreshWins()

def calNGramValues(text,n):
    #find common digrams
    gramMap = {}
    for i in range (0,len(text)-1):
        gram = text[i:i+n]
        if gram in gramMap:
            gramMap[gram]+=1
        else:
            gramMap[gram]=1

    #remove all digrams less than 1
    toRem = []
    for g in gramMap:
        if (gramMap[g] < 2):
            toRem.append(g)
    for g in toRem:
        del gramMap[g]
    
    return sorted(gramMap,key=lambda key: gramMap[key],reverse=True)

def calcGrams(): 
    ciphertext = glob['ciphertextInfo']['data']
    return calNGramValues(ciphertext,2),calNGramValues(ciphertext,3)

def makeDict():
    orderedSet = set()
    with open('/usr/share/dict/american-english') as f:
        for line in f:
           orderedSet.add(line.strip())
    return orderedSet


def getScore(text):
    minWordLen = 3
    wordCount = 0
    words = []
    max = 30
    text = text.lower()
    #go through each character and get a score
    for start in range(0,max):
        for end in range(start+minWordLen,start+10):
             word = text[start:end]
             if len(word) < minWordLen:
                 continue;
             if (word in glob['englishInfo']['dictionary']):
                 words.append(word)
    return len(words),words

def assignOrder(j,i):
    keyMap = glob['key']['map']
    valuesOrder = getKeyValuesOrder()
    firstKey = keyFromValue(keyMap,valuesOrder[i])
    firstValue = keyMap[firstKey]
    secondKey = keyFromValue(keyMap,valuesOrder[j])
    secondValue = keyMap[secondKey]
    keyMap[firstKey] = secondValue
    keyMap[secondKey] = firstValue
#    debug("trying to switch {},{} - {} with {}.  Their keys are: {} and {}\n".format(i,j,firstValue,secondValue,firstKey,secondKey))
    order = getKeyValuesOrder()

def swap(j,i):
    assignOrder(j,i)

def makeGuesses2():
    global glob
    keyMap = glob['key']['map']
    best = glob['best']['score']
    bestWords = glob['best']['words']
    bestMap = glob['best']['map']
    max = len(keyMap)-1
    translated = translate()
    score,words = getScore(translated)
    if (score > best):
        best = score
        bestWords = words
        bestMap = keyMap
        
    debug("starting with {} score, {} words\n".format(best,str(bestWords)))
    for k in range (0,5):#overall iterations
        for j in range (1,max):#swap with nth from curr
            for curr in range (0,max-j):#swap each from beginning
                swap(curr,curr+j)
                translated = translate()
                score,words = getScore(translated)
                if score > best:
                    best = score
                    bestWords = words
                    bestMap = glob['key']['map']
                    debug('better! {}:  {}: {}: {}\n'.format(score,getKeyValuesOrder(),translate()[:30],str(words)))
                else:
                    swap(curr,curr+j)
                displayKeyValues()
    if (len(bestMap) > len(keyMap)):
        glob['key']['map'] = bestMap
        glob['best']['score'] = best
        glob['best']['map'] = bestMap
        glob['best']['words'] = bestWords
        debug('best score was: '+str(best)+"\nwords:"+str(words)+'\n')
    else:
        debug("No improvement.\n")
    displayTranslated()
    displayKeyValues()
    refreshWins();
            
def makeGuesses():
    len = 10
    p = []
    for i in range(0,len):
        p.append(0)
    i=1
    j=0
    bestKey = glob['key']['map']
    words = []
    refreshWins();
    time.sleep(1)
    translated = translate()
    score,words = getScore(translated)
    debug('\nInitial! {}: {}\n'.format(score,getKeyValuesOrder()))
    bestScore = score

    while(i<len):
        if (p[i] < i):
            if i % 2 != 0:
                j=p[i]
            else:
                j=0
            swap(j,i)

            translated = translate()
            score,words = getScore(translated)
            if score > bestScore:
                debug('better! {}:  {}: {}: {}\n'.format(score,getKeyValuesOrder(),translate()[:20],str(words)))
                bestScore = score
                bestKey = glob['key']['map']
                displayTranslated()
            p[i]+=1
            i=1
        else:
            p[i] = 0
            i+=1

    debug('checked {} permutations\n'.format(math.factorial(len)))
    debug('best score was: '+str(bestScore)+"\nwords:"+str(words))
    glob['key']['map'] = bestKey
    displayTranslated()
    debug(str(bestKey))
     
def run(stdscr,ciphertext):
        global glob
        stdscr.refresh()
        makeWindows(stdscr)
        getCiphertextInfo(ciphertext)
        dists = countDist()
        initKey()
        index = 0
        xPos = xPosMin = 7
        xPosMax = 27*4
        yPos = 18
        digramstate = 0
        digrams, trigrams = calcGrams()
        while True:
            displayKeyValues()
            displayStats(stdscr,dists,digrams,trigrams)
            displayTranslated()
            stdscr.move(yPos,xPos) #move to key window
            c = stdscr.getch()
            if c == curses.KEY_LEFT:
                xPos-=4
                index-=1
                if index < 0:
                    index = 25
                    xPos = xPosMax-1

            if c == curses.KEY_RIGHT:
                xPos+=4
                index+=1
                if index > 25:
                    index = 0
                    xPos = xPosMin
            if (ord('a') <= c) and (c <=  ord('z')):
                replaceChar(index,c)
            if (c == ord('\t')):
                makeGuesses2()

if __name__ == "__main__":
        main()
