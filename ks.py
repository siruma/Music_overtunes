import sys, os
import time, random, array
import wave, argparse, pygame
import numpy as np
from collections import deque
from matplotlib import pyplot as plt

# show plot of algorithm in action?
gShowPlot = False
writeBL = False
pygame.init()

sound_path = './sound/'
# notes of a Pentatonic Minor scale
# piano C3-E(b)-F-G-B(b)-C4
pmNotes = {'C3': 261.626, 'Eb': 311.127, 'F': 349.228, 'G':391.995, 'Bb':466.146}

#Japanese scale
#piano C3-D-E(b)-G-A(b)-C4
jpmNotes = {'C3': 261.626, 'D': 293.665, 'F': 349.228, 'G': 391.995, 'Ab': 415.305}

#Chinese scale
#piano C3-D-E-G-A-C4
chinapmNotes = {'C3': 261.626, 'D': 293.665, 'E':329.628, 'G': 391.995, 'A': 440.000 }

def getList(dict): 
    list = [] 
    for key in dict.keys(): 
        list.append(key) 
          
    return list

#Generate note of given freaquency
def generateNote(freq):
    nSamples = 44100
    sampleRate = 44100
    N = int(sampleRate/freq)
    #Initiaze ring buffer
    buf = deque([random.random() - 0.5 for i in range(N)])
    #Initiaze samples buffer
    samples = np.array([0]*nSamples, 'float32')

    for i in range(nSamples):
        samples[i] = buf[0]
        avg = 0.996*0.5*(buf[0]+buf[1])
        buf.append(avg)
        buf.popleft()

    #Convert sample to 16-bit values and then to a string
    # the maximum value is 32767 for 16-bit
    samples = np.array(samples*32767, 'int16')
    return samples.tostring()

def writeWAVE(fname, data):
    #Open file
    file = wave.open(fname, 'wb')
    #WAV file parameters
    nChannels = 1
    sampleWidth = 2
    frameRate = 44100
    nFrame = 44100
    #Set Parameters
    file.setparams((nChannels, sampleWidth, frameRate, nFrame, 'NONE', 'noncompressed'))
    file.writeframes(data)
    file.close()

#Read txt-files and play it
def readTXT(fileName, notePlayer):
    file = open(fileName, 'r')
    Lines = file.read().split(' ')
    for key in Lines:
        if not key:
            pass
        else: 
            print("Playing file %s.wav" % key)
            notePlayer.play(key + ".wav")
            time.sleep(0.5)
    file.close()

#Write txt-file 
def writeTXT(fileName, keys):
    file = open(fileName, 'w')
    for key in keys:
        file.write(key + ' ')
    file.close()
    
#Game window
class GameScreen:
    #Consrtuctor
    def __init__(self):
        self.screen = pygame.display.set_mode((1299, 957))
        self.pic1 = pygame.image.load(os.path.join('pictures\piano-keys.jpg'))
        self.pic1rect = self.pic1.get_rect()
    #Update the screen
    def upDate(self):
        self.screen.blit(self.pic1, self.pic1rect)
        pygame.display.flip()
        

#Play a WAV file
class NotePlayer:
    #Constructor
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        self.screen = GameScreen()
        self.screen.upDate()
        #Dictionary of notes
        self.notes = {}
    #Add note
    def add(self, fileName):
        self.notes[fileName] = pygame.mixer.Sound(sound_path + fileName)
        self.screen.upDate()
    #Play note
    def play(self, fileName):
        try:
            self.notes[fileName].play()
            self.screen.upDate()
        except:
            print(fileName + ' not found!')
            self.screen.upDate()

    def playRandom(self):
        """Play a random note"""
        index = random.randint(0 , len(self.notes)-1)
        note = list(self.notes.values())[index]
        note.play()
        self.screen.upDate()

#Main method
def main():
    # declare global var
    global gShowPlot, writeBL, sound_path
    #pygame.init()
    
    parser = argparse.ArgumentParser(description= "Generating sound with Karplus String Algorithm")

    #Add arguments
    parser.add_argument('--display', action='store_true', required=False)
    parser.add_argument('--play', action='store_true', required=False)
    parser.add_argument('--piano', action='store_true', required=False)
    parser.add_argument('--japan', action='store_true',required=False)
    parser.add_argument('--china', action='store_true',required=False)
    parser.add_argument('--inFile', dest='inFile', required=False)
    parser.add_argument('--outFile', dest='outFile', required=False)
    args = parser.parse_args()

    #Show plot if flag set
    if args.display:
        gShowPlot = True
        plt.ion()
    
    if args.outFile:
        writeBL = True
        outFile = args.outFile + '.txt'
        piano_list = []
    
    #Create note player
    nplayer = NotePlayer()

    if args.japan:
        notes = jpmNotes
    elif args.china:
        notes = chinapmNotes
    else:
        notes = pmNotes

    print('creating notes...')
    for name, freq in list(notes.items()):
        fileName = name + '.wav'
        file_path = os.path.join(sound_path + fileName)
        if not os.path.exists(file_path) or args.display:
            data = generateNote(freq)
            print('creating ' + fileName + '...')
            writeWAVE(fileName, data)
        else:
            print('fileName already created. skipping...')
        
        #Add note to player
        nplayer.add(fileName)

        #Play note if display flag set
        if args.display:
            nplayer.play(fileName)
            time.sleep(5)
    
    #Play random tune
    if args.play or args.inFile:
        if args.inFile:
            readTXT(args.inFile, nplayer)
        else:    
            while True:
                nplayer.playRandom()
                #Rest -1 to 8 beats
                rest = np.random.choice([1,2,4,8], 1, p=[0.15,0.7,0.1,0.05])
                time.sleep(0.25*rest[0])
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            exit()

    #Random piano mode
    if args.piano:
        #"print("piano")
        piano_keys = getList(notes)
        print(piano_keys)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if writeBL:
                            writeTXT(outFile, piano_list)
                        exit()
                    elif event.key == pygame.K_a:
                        nplayer.play(piano_keys[0] + '.wav')
                        if writeBL:
                            piano_list.append(piano_keys[0])
                    elif event.key == pygame.K_s:
                        nplayer.play(piano_keys[1] + '.wav')
                        if writeBL:
                            piano_list.append(piano_keys[1])
                    elif event.key == pygame.K_d:
                        nplayer.play(piano_keys[2] + '.wav')
                        if writeBL:
                            piano_list.append(piano_keys[2])
                    elif event.key == pygame.K_f:
                        nplayer.play(piano_keys[3] + '.wav')
                        if writeBL:
                            piano_list.append(piano_keys[3])
                    elif event.key == pygame.K_g:
                        nplayer.play(piano_keys[4] + '.wav')
                        if writeBL:
                            piano_list.append(piano_keys[4])
                    else:
                        nplayer.playRandom()
                    time.sleep(0.1)

#Call main
if __name__ == "__main__":
    main()
