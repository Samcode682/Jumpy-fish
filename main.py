#!/usr/bin/env python3
"""
Jumpy-fish — simple Flappy Fish style game using pygame.

Usage:
  python main.py            # run interactively (requires display)
  python main.py --headless # run a short headless smoke-test (uses SDL_VIDEODRIVER=dummy)
"""
import sys
import random
import argparse

import pygame


WIDTH, HEIGHT = 600, 400

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Game settings
GRAVITY = 0.5
JUMP_SPEED = -10
PIPE_SPEED = 3
PIPE_WIDTH = 80
PIPE_GAP = 150
PIPE_FREQ_MS = 1500


def run(headless: bool = False):
    pygame.init()
    if headless:
        # allow running in environments without a display for smoke tests
        pygame.display.init()
        pygame.display.set_mode((1, 1))
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Jumpy-fish")

    # Keep a reference to screen for drawing API compatibility
    screen = pygame.display.get_surface() or pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    # Fish
    fish_x = 50
    fish_y = HEIGHT // 2
    fish_speed = 0
    fish_size = 30

    # Pipes stored as dicts {x, top_height}
    pipes = []

    score = 0

    pygame.time.set_timer(pygame.USEREVENT, PIPE_FREQ_MS)

    running = True
    frames = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fish_speed = JUMP_SPEED
            elif event.type == pygame.USEREVENT:
                top_h = random.randint(50, HEIGHT - PIPE_GAP - 50)
                pipes.append({"x": WIDTH, "h": top_h})

        # Physics
        fish_speed += GRAVITY
        fish_y += fish_speed

        # Move pipes
        for p in pipes:
            p["x"] -= PIPE_SPEED

        # Remove off-screen pipes
        pipes = [p for p in pipes if p["x"] > -PIPE_WIDTH]

        # Collision with ground/ceiling
        if fish_y < 0 or fish_y + fish_size > HEIGHT:
            running = False

        # Collision with pipes
        for p in pipes:
            if (fish_x + fish_size > p["x"] and fish_x < p["x"] + PIPE_WIDTH):
                if fish_y < p["h"] or fish_y + fish_size > p["h"] + PIPE_GAP:
                    running = False

        # Scoring: when pipe passes the fish
        for p in pipes:
            if not p.get("scored") and p["x"] + PIPE_WIDTH < fish_x:
                p["scored"] = True
                score += 1

        # Drawing
        screen.fill(BLUE)
        pygame.draw.rect(screen, WHITE, (fish_x, int(fish_y), fish_size, fish_size))

        for p in pipes:
            pygame.draw.rect(screen, GREEN, (int(p["x"]), 0, PIPE_WIDTH, p["h"]))
            pygame.draw.rect(screen, GREEN, (int(p["x"]), p["h"] + PIPE_GAP, PIPE_WIDTH, HEIGHT - (p["h"] + PIPE_GAP)))

        score_surf = font.render(str(score), True, WHITE)
        screen.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, 20))

        pygame.display.flip()
        clock.tick(60)

        frames += 1
        if headless and frames > 10:
            # stop quickly during headless smoke-test
            running = False

    pygame.quit()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="run a short headless smoke-test")
    args = parser.parse_args(argv)

    try:
        run(headless=args.headless)
    except pygame.error as e:
        print("Pygame error:", e)
        print("If you run headless tests, try: export SDL_VIDEODRIVER=dummy")
        sys.exit(1)


if __name__ == "__main__":
    main()
