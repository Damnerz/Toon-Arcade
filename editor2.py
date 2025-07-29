import pygame
import json
import os

pygame.init()
pygame.mixer.init()

# --- SETTINGS ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
FPS = 60
PIXELS_PER_SECOND = 100
LANE_Y = [200, 350]
LANE_HEIGHT = 60
LANE_KEYS = [
    (pygame.K_z, pygame.K_l),  # Lane 0 keys (Z and L)
    (pygame.K_a, pygame.K_n),  # Lane 1 keys (A and N)
]
KEY_NAMES = ["Z/L", "A/N"]

# --- COLORS ---
BACKGROUND_COLOR = (20, 20, 30)
LANE_COLOR = (50, 50, 50)
HIT_LINE_COLOR = (255, 255, 255)
NOTE_COLORS = {
    'Z': (100, 200, 100),
    'L': (50, 150, 50),
    'ZL': (0, 255, 0),
    'A': (255, 105, 180),
    'N': (200, 50, 130),
    'AN': (255, 20, 147),
}
TEXT_COLOR = (200, 200, 200)

# --- SETUP ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Guitar Hero Note Editor with Pause, Timeline Move, and Note Removal")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# --- LOAD MUSIC ---
music_path = os.path.join("assets", "beat.wav")
pygame.mixer.music.load(music_path)
music_length = pygame.mixer.Sound(music_path).get_length()

# --- EDITOR STATE ---
notes = []
running = True
playing = False
paused = False
start_ticks = None
paused_at = 0.0
current_time = 0.0
time_increment = 0.1  # seconds to move with arrows

def update_current_time():
    global current_time
    if playing and not paused:
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
    # Clamp current_time to music length
    current_time = max(0.0, min(current_time, music_length))

def is_point_in_circle(px, py, cx, cy, r):
    return (px - cx) ** 2 + (py - cy) ** 2 <= r ** 2

while running:
    dt = clock.tick(FPS) / 1000.0
    screen.fill(BACKGROUND_COLOR)
    pressed_keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not playing:
                    # Start playing
                    pygame.mixer.music.play(start=paused_at)
                    start_ticks = pygame.time.get_ticks() - int(paused_at * 1000)
                    current_time = paused_at
                    playing = True
                    paused = False
                else:
                    if paused:
                        # Resume
                        pygame.mixer.music.unpause()
                        start_ticks = pygame.time.get_ticks() - int(current_time * 1000)
                        paused = False
                    else:
                        # Pause
                        pygame.mixer.music.pause()
                        paused_at = current_time
                        paused = True

            # Move timeline with arrows (only when playing or paused)
            if event.key == pygame.K_RIGHT:
                if not playing or paused:
                    current_time = min(current_time + time_increment, music_length)
                    if playing and paused:
                        paused_at = current_time
                        pygame.mixer.music.play(start=current_time)
                        pygame.mixer.music.pause()
                else:
                    pass

            elif event.key == pygame.K_LEFT:
                if not playing or paused:
                    current_time = max(current_time - time_increment, 0)
                    if playing and paused:
                        paused_at = current_time
                        pygame.mixer.music.play(start=current_time)
                        pygame.mixer.music.pause()
                else:
                    pass

            # Save notes to JSON
            elif event.key == pygame.K_s:
                with open("level.json", "w") as f:
                    json.dump(notes, f, indent=2)
                print("Notes saved to level.json")

            if playing and not paused:
                # Add notes on key press
                current_keys = pygame.key.get_pressed()
                for lane_idx, (key1, key2) in enumerate(LANE_KEYS):
                    if event.key == key1 and current_keys[key2]:
                        note_type = "ZL" if lane_idx == 0 else "AN"
                        notes.append({'time_sec': current_time, 'lane': lane_idx, 'type': note_type})
                        print(f"Placed combo note {note_type} at {current_time:.2f}s lane {lane_idx}")
                    elif event.key == key1:
                        note_type = "Z" if lane_idx == 0 else "A"
                        notes.append({'time_sec': current_time, 'lane': lane_idx, 'type': note_type})
                        print(f"Placed note {note_type} at {current_time:.2f}s lane {lane_idx}")
                    elif event.key == key2 and current_keys[key1]:
                        pass  # combo handled above
                    elif event.key == key2:
                        note_type = "L" if lane_idx == 0 else "N"
                        notes.append({'time_sec': current_time, 'lane': lane_idx, 'type': note_type})
                        print(f"Placed note {note_type} at {current_time:.2f}s lane {lane_idx}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click to remove note
                mx, my = event.pos
                removed = False
                for note in notes[:]:
                    note_time = note['time_sec']
                    lane = note['lane']
                    y = LANE_Y[lane]
                    x = SCREEN_WIDTH // 2 + (note_time - current_time) * PIXELS_PER_SECOND
                    radius = 20 if note['type'] in ['ZL', 'AN'] else 14
                    if is_point_in_circle(mx, my, x, y, radius):
                        notes.remove(note)
                        print(f"Removed note {note['type']} at {note_time:.2f}s lane {lane}")
                        removed = True
                        break  # remove only one note per click

    # Update time if playing and not paused
    if playing and not paused:
        update_current_time()

    # Draw lanes
    for i, y in enumerate(LANE_Y):
        pygame.draw.rect(screen, LANE_COLOR, (0, y - LANE_HEIGHT // 2, SCREEN_WIDTH, LANE_HEIGHT))
        label = font.render(KEY_NAMES[i], True, (180, 180, 180))
        screen.blit(label, label.get_rect(center=(SCREEN_WIDTH // 2 - 100, y)))

    pygame.draw.line(screen, HIT_LINE_COLOR, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

    # Draw notes
    for note in notes:
        note_time = note['time_sec']
        lane = note['lane']
        y = LANE_Y[lane]
        x = SCREEN_WIDTH // 2 + (note_time - current_time) * PIXELS_PER_SECOND

        if -50 <= x <= SCREEN_WIDTH + 50:
            color = NOTE_COLORS.get(note['type'], (255, 255, 255))
            radius = 20 if note['type'] in ['ZL', 'AN'] else 14
            pygame.draw.circle(screen, color, (int(x), y), radius)
            label = font.render(note['type'], True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=(int(x), y)))

    # Display info
    play_status = "Paused" if paused else "Playing" if playing else "Stopped"
    screen.blit(font.render(f"Status: {play_status}", True, TEXT_COLOR), (10, 10))
    screen.blit(font.render("SPACE: Play/Pause", True, TEXT_COLOR), (10, 40))
    screen.blit(font.render("LEFT/RIGHT: Move timeline (when paused/stopped)", True, TEXT_COLOR), (10, 70))
    screen.blit(font.render("Z, L, A, N: Place notes", True, TEXT_COLOR), (10, 100))
    screen.blit(font.render("Click note to remove it", True, TEXT_COLOR), (10, 130))
    screen.blit(font.render("S: Save notes", True, TEXT_COLOR), (10, 160))
    screen.blit(font.render(f"Time: {current_time:.2f} / {music_length:.2f} s", True, TEXT_COLOR), (10, 190))
    screen.blit(font.render(f"Notes placed: {len(notes)}", True, TEXT_COLOR), (10, 220))

    pygame.display.flip()

pygame.quit()
