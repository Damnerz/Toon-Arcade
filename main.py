import pygame
import json
import os

pygame.init()
pygame.mixer.init()

# --- SETTINGS ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
FPS = 60
PIXELS_PER_SECOND = 100
HIT_WINDOW = 0.25
PERFECT_WINDOW = 0.1
GOOD_WINDOW = 0.2
NOTE_SPEED = PIXELS_PER_SECOND
LANE_Y = [200, 350]
LANE_HEIGHT = 60
# Keys to detect combos per lane
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
pygame.display.set_caption("Guitar Hero Playback")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# --- LOAD MUSIC AND LEVEL ---
music_path = os.path.join("assets", "beat.wav")
level_path = "level.json"

with open(level_path, "r") as f:
    notes = json.load(f)

pygame.mixer.music.load(music_path)
TOTAL_SECONDS = int(pygame.mixer.Sound(music_path).get_length()) + 1

# --- GAME STATE ---
running = True
playing = False
game_over = False
start_ticks = None
score = 0
combo = 0
max_combo = 0
hit_notes = []
missed_notes = []
feedback_messages = []

# --- MAIN LOOP ---
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
                    start_ticks = pygame.time.get_ticks()
                    pygame.mixer.music.play()
                    playing = True
                    game_over = False
                    score = combo = max_combo = 0
                    hit_notes = []
                    missed_notes = []
                    feedback_messages = []

            if playing and not game_over:
                current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
                # Check lanes and keys
                for lane_index, (key1, key2) in enumerate(LANE_KEYS):
                    # Single keys and combos on lane 0 or 1
                    # Check notes in order of timing
                    for note in notes:
                        if note in hit_notes or note in missed_notes:
                            continue
                        if note['lane'] != lane_index:
                            continue

                        diff = abs(note['time_sec'] - current_time)
                        if diff > HIT_WINDOW:
                            continue

                        note_type = note['type']

                        # Lane 0: Z, L, ZL
                        if lane_index == 0:
                            # If note is single Z and pressed Z
                            if note_type == 'Z' and event.key == key1:
                                hit_notes.append(note)
                                if diff <= PERFECT_WINDOW:
                                    score += 150
                                    feedback = "Perfect"
                                elif diff <= GOOD_WINDOW:
                                    score += 100
                                    feedback = "Good"
                                else:
                                    score += 50
                                    feedback = "Okay"
                                combo += 1
                                max_combo = max(max_combo, combo)
                                feedback_messages.append((feedback, pygame.time.get_ticks(), lane_index))
                                break

                            # Single L and pressed L
                            elif note_type == 'L' and event.key == key2:
                                hit_notes.append(note)
                                if diff <= PERFECT_WINDOW:
                                    score += 150
                                    feedback = "Perfect"
                                elif diff <= GOOD_WINDOW:
                                    score += 100
                                    feedback = "Good"
                                else:
                                    score += 50
                                    feedback = "Okay"
                                combo += 1
                                max_combo = max(max_combo, combo)
                                feedback_messages.append((feedback, pygame.time.get_ticks(), lane_index))
                                break

                            # Combo ZL: both keys pressed
                            elif note_type == 'ZL':
                                if pressed_keys[key1] and pressed_keys[key2]:
                                    hit_notes.append(note)
                                    if diff <= PERFECT_WINDOW:
                                        score += 200
                                        feedback = "Perfect Combo"
                                    elif diff <= GOOD_WINDOW:
                                        score += 150
                                        feedback = "Good Combo"
                                    else:
                                        score += 100
                                        feedback = "Okay Combo"
                                    combo += 1
                                    max_combo = max(max_combo, combo)
                                    feedback_messages.append((feedback, pygame.time.get_ticks(), lane_index))
                                    break

                        # Lane 1: A, N, AN
                        elif lane_index == 1:
                            if note_type == 'A' and event.key == key1:
                                hit_notes.append(note)
                                if diff <= PERFECT_WINDOW:
                                    score += 150
                                    feedback = "Perfect"
                                elif diff <= GOOD_WINDOW:
                                    score += 100
                                    feedback = "Good"
                                else:
                                    score += 50
                                    feedback = "Okay"
                                combo += 1
                                max_combo = max(max_combo, combo)
                                feedback_messages.append((feedback, pygame.time.get_ticks(), lane_index))
                                break

                            elif note_type == 'N' and event.key == key2:
                                hit_notes.append(note)
                                if diff <= PERFECT_WINDOW:
                                    score += 150
                                    feedback = "Perfect"
                                elif diff <= GOOD_WINDOW:
                                    score += 100
                                    feedback = "Good"
                                else:
                                    score += 50
                                    feedback = "Okay"
                                combo += 1
                                max_combo = max(max_combo, combo)
                                feedback_messages.append((feedback, pygame.time.get_ticks(), lane_index))
                                break

                            elif note_type == 'AN':
                                if pressed_keys[key1] and pressed_keys[key2]:
                                    hit_notes.append(note)
                                    if diff <= PERFECT_WINDOW:
                                        score += 200
                                        feedback = "Perfect Combo"
                                    elif diff <= GOOD_WINDOW:
                                        score += 150
                                        feedback = "Good Combo"
                                    else:
                                        score += 100
                                        feedback = "Okay Combo"
                                    combo += 1
                                    max_combo = max(max_combo, combo)
                                    feedback_messages.append((feedback, pygame.time.get_ticks(), lane_index))
                                    break

                    else:
                        # If no note matched for this key press
                        if event.key == key1 or event.key == key2:
                            combo = 0
                            feedback_messages.append(("Miss", pygame.time.get_ticks(), lane_index))

    elapsed_time = 0
    if playing and start_ticks:
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000.0

    if playing and elapsed_time >= TOTAL_SECONDS:
        playing = False
        game_over = True
        pygame.mixer.music.stop()

    # Draw lanes and hit line
    for i, y in enumerate(LANE_Y):
        pygame.draw.rect(screen, LANE_COLOR, (0, y - LANE_HEIGHT // 2, SCREEN_WIDTH, LANE_HEIGHT))
        label = font.render(KEY_NAMES[i], True, (180, 180, 180))
        screen.blit(label, label.get_rect(center=(SCREEN_WIDTH // 2 - 100, y)))

    pygame.draw.line(screen, HIT_LINE_COLOR, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)

    # Draw notes
    for note in notes:
        note_time = note['time_sec']
        if note in hit_notes:
            continue
        if note_time < elapsed_time - HIT_WINDOW:
            missed_notes.append(note)
            combo = 0
            feedback_messages.append(("Miss", pygame.time.get_ticks(), note['lane']))
            continue

        note_type = note['type']
        lane = note['lane']
        y = LANE_Y[lane]
        x = SCREEN_WIDTH // 2 + (note_time - elapsed_time) * NOTE_SPEED

        if -50 <= x <= SCREEN_WIDTH + 50:
            color = NOTE_COLORS.get(note_type, (255, 255, 255))
            radius = 20 if note_type in ['ZL', 'AN'] else 14
            pygame.draw.circle(screen, color, (int(x), y), radius)
            label = font.render(note_type, True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=(int(x), y)))

    # Draw feedback messages
    for msg, t, lane in feedback_messages[:]:
        if pygame.time.get_ticks() - t < 800:
            text = font.render(msg, True, (255, 255, 0) if msg != "Miss" else (255, 80, 80))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2 + 80, LANE_Y[lane])))
        else:
            feedback_messages.remove((msg, t, lane))

    # Text info
    screen.blit(font.render("Press SPACE to Play", True, TEXT_COLOR), (10, 10))
    screen.blit(font.render(f"Time: {elapsed_time:.2f}s", True, TEXT_COLOR), (10, 40))
    screen.blit(font.render(f"Score: {score}", True, TEXT_COLOR), (10, 70))
    screen.blit(font.render(f"Combo: {combo}", True, TEXT_COLOR), (10, 100))

    # Show end screen
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        end_texts = [
            f"SONG COMPLETE!",
            f"Final Score: {score}",
            f"Max Combo: {max_combo}",
            f"Notes Hit: {len(hit_notes)} / {len(notes)}",
            f"Accuracy: {100 * len(hit_notes) / len(notes):.1f}%",
            "Press SPACE to Replay",
        ]
        for i, text in enumerate(end_texts):
            label = font.render(text, True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 40)))

    pygame.display.flip()

pygame.quit()

