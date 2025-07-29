# Enhanced Guitar Hero Style Editor with Cool Features

import pygame
import json
import sys
import wave
import contextlib

# === Setup ===
pygame.init()
pygame.mixer.init()

# Get song duration dynamically
def get_wav_duration(filename):
    with contextlib.closing(wave.open(filename, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

music_file = 'assets/beat.wav'
music_duration = get_wav_duration(music_file)
TOTAL_SECONDS = int(music_duration) + 1

pygame.mixer.music.load(music_file)

WIDTH, HEIGHT = 1000, 600
PIXELS_PER_SECOND = 100
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guitar Hero Editor - Deluxe")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 24, bold=True)

# === Constants ===
BG_COLOR = (20, 20, 20)
LANE_COLOR = (60, 60, 60)
NOTE_COLORS = {
    'Z': (100, 200, 100),
    'L': (50, 150, 50),
    'ZL': (0, 255, 0),
    'A': (255, 105, 180),
    'N': (200, 50, 130),
    'AN': (255, 20, 147)
}
LANES_Y = [200, 350]
TIMELINE_Y = HEIGHT - 80

# === Variables ===
notes = []
playback_time = 0.0
playing = False
selected_note_type = 'Z'
zoom = 1.0

# === Functions ===
def draw_lanes():
    for i, y in enumerate(LANES_Y):
        pygame.draw.rect(screen, LANE_COLOR, (0, y - 30, WIDTH, 60))
        lane_name = "Lane 1 (Z,L,ZL)" if i == 0 else "Lane 2 (A,N,AN)"
        screen.blit(FONT.render(lane_name, True, (200, 200, 200)), (10, y - 50))

def draw_timeline():
    pygame.draw.rect(screen, (40, 40, 40), (0, TIMELINE_Y, WIDTH, 50))
    for sec in range(TOTAL_SECONDS + 1):
        x = sec * PIXELS_PER_SECOND * zoom - playback_time * PIXELS_PER_SECOND * zoom
        if 0 <= x <= WIDTH:
            pygame.draw.line(screen, (180, 180, 180), (x, TIMELINE_Y), (x, TIMELINE_Y + 50))
            label = FONT.render(str(sec), True, (180, 180, 180))
            screen.blit(label, (x + 2, TIMELINE_Y + 2))

    # Draw playback head
    pygame.draw.line(screen, (255, 255, 0), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)

def draw_notes():
    for note in notes:
        x = note['time_sec'] * PIXELS_PER_SECOND * zoom - playback_time * PIXELS_PER_SECOND * zoom + WIDTH // 2
        if -30 <= x <= WIDTH + 30:
            y = LANES_Y[note['lane']]
            color = NOTE_COLORS.get(note['type'], (255, 255, 255))
            radius = 20 if note['type'] in ['ZL', 'AN'] else 14
            pygame.draw.circle(screen, color, (int(x), y), radius)
            text = FONT.render(note['type'], True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(int(x), y)))

def draw_ui():
    info = [
        "SPACE: Play/Pause",
        "Arrow Keys: Move Timeline",
        "+/-: Zoom In/Out",
        "1-6: Select Note Type",
        "Click: Add/Remove Note",
        "S: Save | L: Load"
    ]
    for i, txt in enumerate(info):
        screen.blit(FONT.render(txt, True, (200, 200, 200)), (WIDTH - 220, 10 + i * 20))
    screen.blit(BIG_FONT.render(f"Note: {selected_note_type}", True, (255, 255, 0)), (10, 10))

def add_note_at_pos(mouse_pos):
    mx, my = mouse_pos
    lane = None
    for i, y in enumerate(LANES_Y):
        if y - 30 <= my <= y + 30:
            lane = i
            break
    if lane is None:
        return
    time_sec = (mx - WIDTH // 2) / (PIXELS_PER_SECOND * zoom) + playback_time
    time_sec = round(time_sec, 2)
    for note in notes:
        if abs(note['time_sec'] - time_sec) < 0.05 and note['lane'] == lane:
            notes.remove(note)
            return
    notes.append({'time_sec': time_sec, 'lane': lane, 'type': selected_note_type})

def save_notes():
    with open('level.json', 'w') as f:
        json.dump(notes, f, indent=2)
    print("Notes saved.")

def load_notes():
    global notes
    try:
        with open('level.json', 'r') as f:
            notes = json.load(f)
        print("Notes loaded.")
    except:
        print("No save file found.")

# === Main Loop ===
running = True
while running:
    dt = clock.tick(60) / 1.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                add_note_at_pos(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                playing = not playing
                if playing:
                    pygame.mixer.music.play(-1, start=playback_time)
                else:
                    pygame.mixer.music.pause()
            elif event.key == pygame.K_s:
                save_notes()
            elif event.key == pygame.K_l:
                load_notes()
            elif event.key == pygame.K_LEFT:
                playback_time = max(0, playback_time - 0.5)
                if playing:
                    pygame.mixer.music.play(-1, start=playback_time)
            elif event.key == pygame.K_RIGHT:
                playback_time = min(TOTAL_SECONDS, playback_time + 0.5)
                if playing:
                    pygame.mixer.music.play(-1, start=playback_time)
            elif event.key == pygame.K_MINUS:
                zoom = max(0.25, zoom - 0.1)
            elif event.key == pygame.K_EQUALS:
                zoom = min(2.0, zoom + 0.1)
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                selected_note_type = ['Z', 'L', 'ZL', 'A', 'N', 'AN'][event.key - pygame.K_1]

    if playing:
        playback_time += dt / 1000.0
        if playback_time > TOTAL_SECONDS:
            playback_time = 0
            pygame.mixer.music.play(-1, start=0)

    screen.fill(BG_COLOR)
    draw_lanes()
    draw_timeline()
    draw_notes()
    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()
