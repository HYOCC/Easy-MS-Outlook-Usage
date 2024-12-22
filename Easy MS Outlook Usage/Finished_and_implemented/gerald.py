import pyaudio 
import pygame 
import math 
import speech_recognition as sr 

screen_width = 500
screen_height = 500
pygame.init() 
pygame.mixer.init()
pygame.display.set_caption('gerald')
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

#Audio config
CHUNK = 1024 
FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,channels=CHANNEL,rate=RATE,input=True,frames_per_buffer=CHUNK)



def get_mic_input_level():
    data = stream.read(CHUNK)
    rms = 0 
    for i in range(0, len(data),2):
        sample = int.from_bytes(data[i:i+2], byteorder='little', signed=True)
        rms += sample * sample 
    rms = math.sqrt(rms/(CHUNK/2))
    return rms
    
def draw(amp):
    screen.fill((0,0,0))
    point = []
    if amp > 10:
        for x in range(screen_width):
            y = screen_height/2+int(amp*math.sin(x*.02))
            point.append((x,y))
    else:
        point.append((0,screen_height/2))
        point.append((screen_width, screen_height/2))

    pygame.draw.lines(screen, (255,255,255), False, point, 2)
    pygame.display.flip()

running = True
amp = 100 

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
            
    amp_adj = get_mic_input_level() / 25
    
    amp = max(10, amp_adj) 
    
    draw(amp)
    
    print(get_mic_input_level())
    clock.tick(120)

pygame.quit()