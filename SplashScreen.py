#0----------------------------------------------------------------------------------------------
#download the necessary package for the graphics pip install pygame 
#run this line to complete installation python -m pygame.examples.aliens
#how to Run 
#to run this file alone run python SplashScreen.py
#time is an import that allows for the transition between the graphic and main application
#0----------------------------------------------------------------------------------------------

import pygame
import time

#0----------------------------------------------------------------------------------------------
#initialize pygame which sets up all pygame modules
#0----------------------------------------------------------------------------------------------

def show_splash_screen():
    pygame.init()

#0----------------------------------------------------------------------------------------------    
#Set screen dimensions and create a window using pygame
#0----------------------------------------------------------------------------------------------

    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))

#0----------------------------------------------------------------------------------------------    
#Load the splash screen image and scale it to fit the screen dimensions
#0----------------------------------------------------------------------------------------------

    splash_image = pygame.image.load("logo.jpg")  # Ensure you have an image named 'logo.jpg'
    splash_image = pygame.transform.scale(splash_image, (screen_width, screen_height))

#0----------------------------------------------------------------------------------------------    
#Fill the screen with black background and display the splash image
#0----------------------------------------------------------------------------------------------

    screen.fill((0, 0, 0))
    screen.blit(splash_image, (0, 0))
    pygame.display.update()

#0----------------------------------------------------------------------------------------------    
#Pause execution for 3 seconds to keep the splash screen visible
#0----------------------------------------------------------------------------------------------

    time.sleep(3)

#0----------------------------------------------------------------------------------------------
#Transition to main application by calling the main_app function
#0----------------------------------------------------------------------------------------------

    main_app()

#0----------------------------------------------------------------------------------------------
#Define the main application window which runs after the splash screen
#0----------------------------------------------------------------------------------------------

def main_app():
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Main Application")
    
#0----------------------------------------------------------------------------------------------
#Main loop that keeps the application running until the user closes it
#0----------------------------------------------------------------------------------------------

    running = True
    while running:
        screen.fill((255, 255, 255))  # Fill with white background
        
        for event in pygame.event.get():  # Check for events
            if event.type == pygame.QUIT:  # If the close button is clicked, exit the loop
                running = False
        
        pygame.display.update()  # Update the display
    
    pygame.quit()  # Quit pygame when the loop exits

#0----------------------------------------------------------------------------------------------
#Check if the script is run directly and call show_splash_screen to start the program
#0----------------------------------------------------------------------------------------------

if __name__ == "__main__":
    show_splash_screen()

#0----------------------------------------------------------------------------------------------

#0----------------------------------------------------------------------------------------------
