import sys, os
import time, random
import wave, argparse, pygame
import numpy as np
from collections import deque
from matplotlib import pyplot as plt

# show plot of algorithm in action?
gShowPlot = False
# notes of a Pentatonic Minor scale
# piano C4-E(b)-F-G-B(b)-C5
pmNotes = {'C4': 262, 'Eb': 311, 'F': 349, 'G':391, 'Bb':466}

#Japanese mode
#piano C3-D-E(b)-G-A(b)-C4
jpmNotes = {'C3': 261, 'D': 393, 'F': 349, 'G': 391, 'Ab': 415}

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

#Play a WAV file
class NotePlayer:
    #Constructor
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        #Dictionary of notes
        self.notes = {}
    #Add note
    def add(self, fileName):
        self.notes[fileName] = pygame.mixer.Sound(fileName)
    #Play note
    def play(self, fileName):
        try:
            self.notes[fileName].play()
        except:
            print(fileName + ' not found!')
    def playRandom(self):
        """Play a random note"""
        index = random.randint(0 , len(self.notes)-1)
        note = list(self.notes.values())[index]
        note.play()

#Main method
def main():
    # declare global var
    global gShowPlot
    #pygame.init()
    
    parser = argparse.ArgumentParser(description= "Generating sound with Karplus String Algorithm")

    #Add arguments
    parser.add_argument('--display', action='store_true', required=False)
    parser.add_argument('--play', action='store_true', required=False)
    parser.add_argument('--piano', action='store_true', required=False)
    parser.add_argument('--japan', action='store_true',required=False)
    args = parser.parse_args()

    #Show plot if flag set
    if args.display:
        gShowPlot = True
        plt.ion()
    
    #Create note player
    nplayer = NotePlayer()

    if args.japan:
        notes = jpmNotes
    else:
        notes = pmNotes

    print('creating notes...')
    for name, freq in list(notes.items()):
        fileName = name + '.wav'
        if not os.path.exists(fileName) or args.display:
            data = generateNote(freq)
            print('creating ' + fileName + '...')
            writeWAVE(fileName, data)
        else:
            print('fileName already created. skipping...')
        
        #Add note to player
        nplayer.add(name + '.wav')

        #Play note if display flag set
        if args.display:
            nplayer.play(name + '.wav')
            time.sleep(5)
    
    #Play random tune
    if args.play:
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
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
                    #print("Key pressed")
                    nplayer.playRandom()
                    time.sleep(0.5)

#Call main
if __name__ == "__main__":
    main()
