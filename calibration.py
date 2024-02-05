import ast
import time
import pygame
import pyautogui as py

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = py.size()
BACKGROUND_COLOR = (0, 0, 0)  # Black color
RADIUS = 40
COLOR_RED = (255, 0, 0)

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Göz Takibi Kalibrasyon")

# Calibration positions
positions = [(RADIUS, SCREEN_HEIGHT // 2),        # Left
             (SCREEN_WIDTH - RADIUS, SCREEN_HEIGHT // 2),  # Right
             (SCREEN_WIDTH // 2, RADIUS),        # Top
             (SCREEN_WIDTH // 2, SCREEN_HEIGHT - RADIUS),  # Bottom
             (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]  # Middle

# Function to draw a red circle at a given position
def draw_circle(position):
    pygame.draw.circle(screen, COLOR_RED, position, RADIUS)

# Main function
def main():
    running = True
    index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Check for key press events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break  # Exit the loop immediately

        # Clear the screen
        screen.fill(BACKGROUND_COLOR)

        # Draw the current calibration circle
        draw_circle(positions[index])

        # Update the display
        pygame.display.flip()

        try:
            # Read blink information from the file
            with open("components/blink.txt", "r") as file1:
                lines = file1.readlines()
            file1.close()
            # Check if a blink is detected
            if int(lines[0]) == 1:
                coord = ast.literal_eval(lines[1])
                coord.append(index)

                # Write the current coordinates to "coordinates.txt"
                with open("components/coordinates.txt", "w") as file2:
                    file2.write(str(coord))
                file2.close()
                print(coord)
                # Move to the next calibration point after a brief delay
                index += 1
                time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")

        # Exit the loop when all calibration points are visited
        if index >= len(positions):
            running = False

    # Quit Pygame
    pygame.quit()

# Entry point
if __name__ == "__main__":
    main()