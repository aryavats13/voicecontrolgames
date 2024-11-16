
import pygame
import speech_recognition as sr
import pyttsx3
import random
import time
from fuzzywuzzy import fuzz

pygame.init()
engine = pyttsx3.init()

# display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Voice Controlled Game Menu')
# background colors
COLORS = {
    'background': (240, 243, 249),
    'primary': (79, 70, 229),
    'secondary': (99, 102, 241),
    'text': (31, 41, 55),
    'accent': (167, 139, 250),
    'success': (34, 197, 94),
    'error': (239, 68, 68),
    'card': (255, 255, 255),
    'shadow': (226, 232, 240)
}

# Font (all)
pygame.font.init()
font = pygame.font.SysFont('arial', 40)

# voice recognition catch ni kr paarha hai toh variation add krdiye hai taaki agar galat spell bhi hua toh logic smjh jaye konsa game
game_variations = {
    "word detective": [
        "word detective", "wordetective", "word-detective", 
        "detective", "word", "detective game", "word game"
    ],
    "spellbee": [
        "spellbee", "spell bee", "spell-bee", "spelling bee", 
        "spell", "bee", "spelling", "spelling game", "spell game",
        "spell b", "spellb", "spelling b", "spelling be","spell be"
    ],
    "flash cards": [
        "flash cards", "flashcards", "flash-cards", "flash card", 
        "flashcard", "cards", "flash", "card game", "cards game"
    ],
    "2048": [
        "2048", "twenty forty-eight", "two thousand forty-eight",
        "2048 game", "twenty forty eight", "2 0 4 8"
    ]
}
def normalize_command(command):
    """
    Normalize voice command by removing extra spaces, punctuation,
    and converting numbers to words where appropriate
    """
    if not command:
        return ""
        
    # punctuation and extra spaces htane
    command = command.lower().strip()
    command = ' '.join(command.split())
    
    
    number_mappings = {
        "2 0 4 8": "2048",
        "twenty forty eight": "2048",
        "twenty forty-eight": "2048",
        "two zero four eight": "2048",
        "to zero four eight": "2048"
    }
    
    for key, value in number_mappings.items():
        if key in command:
            command = command.replace(key, value)
            
    return command
def find_closest_game(command):
    """
    Find the closest matching game using fuzzy string matching
    """
    if not command:
        return None
        
    command = normalize_command(command)
    
    # First , try for exact words then if not 
    for game, variations in game_variations.items():
        if command in variations:
            return game
            
    #fuzzy matching(import kr lena)
    best_match = None
    highest_ratio = 0
    
    for game, variations in game_variations.items():
        for variation in variations:
            ratio = fuzz.ratio(command, variation)
            partial_ratio = fuzz.partial_ratio(command, variation)
            token_sort_ratio = fuzz.token_sort_ratio(command, variation)
            
            # Use the highest of the three ratios
            best_ratio = max(ratio, partial_ratio, token_sort_ratio)
            
            if best_ratio > highest_ratio:
                highest_ratio = best_ratio
                best_match = game
    
     # Agar confident match milta hai tabhi return karo
    if highest_ratio >= 60: 
        return best_match
    return None

    running = True
    show_menu()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        command = voice_control()
        if command:
            if command.lower() in ["exit", "quit", "goodbye", "bye"]:
                running = False
            elif command.lower() in ["menu", "main menu", "go back", "back"]:
                show_menu()
            else:
                start_game(command)
        
    
        if status_timer > 0:
            status_timer -= 1
        else:
            status_message = ""
            
        show_menu()
        
    pygame.quit()

# Game state variables
current_word = ""
current_question = ""
current_answer = ""
game_score = 0
game_grid = None
status_message = ""
status_color = COLORS['text']
status_timer = 0
is_showing_answer = False

def get_voice_input():
    """Get voice input from the user"""
    recognizer = sr.Recognizer() #recognizer
    with sr.Microphone() as source:
        screen.fill(COLORS['background']) 
        render_text("Listening...", (WINDOW_WIDTH//2, WINDOW_HEIGHT//2),COLORS['primary'])#neeche wala listening 
        pygame.display.flip()
        
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            # display
            screen.fill(COLORS['background'])
            render_text(f"You said: {text}", (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), COLORS['secondary'])
            pygame.display.flip()
            return text
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please try again.")
            return None
        except sr.RequestError:
            speak("There was an error with the speech recognition service.")
            return None
        except sr.WaitTimeoutError:
            speak("No speech detected. Please try again.")
            return None

def render_text(text, position, color):
    """Helper function to render text on screen"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)
def word_detective():
    global current_word, game_score, status_message, status_color, status_timer
    
    # Word and hints 
    word_hints = {
        "apple": [
            "I am red or green in color",
            "I keep the doctor away"
        ],
        "banana": [
            "I am yellow in color",
            "Monkeys love me"
        ],
        "cherry": [
            "I am small and round",
            "I am red in color"
        ],
        "orange": [
            "I am both a fruit and a color",
            "I am full of vitamin C"
        ],
        "mango": [
            "I am tropical fruit",
            "I am the king of fruits"
        ]
    }
    
    game_running = True
    while game_running:
        # Reset game state for new round
        current_word = random.choice(list(word_hints.keys()))
        hints = word_hints[current_word]
        hints_used = 0
        attempts = 0
        round_complete = False
        
        # Create display version of word
        display_word = ['_' for _ in current_word]
        
        status_message = "Say your guess!"
        status_color = COLORS['primary']
        
        while not round_complete and attempts < 3:  # Maximum 3 attempts per round(edit kr lena)
            screen.fill(COLORS['background'])
            

            title_text = font.render("Word Detective", True, COLORS['primary'])
            screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, 50))
            
            hint_font = pygame.font.SysFont('arial', 30)
            score_text = hint_font.render(f"Score: {game_score}", True, COLORS['text'])
            screen.blit(score_text, (50, 50))
            
            attempts_text = hint_font.render(f"Attempts Remaining: {3-attempts}", True, COLORS['text'])
            screen.blit(attempts_text, (WINDOW_WIDTH - 250, 50))
            
            # word
            word_text = font.render(' '.join(display_word), True, COLORS['text'])
            screen.blit(word_text, (WINDOW_WIDTH//2 - word_text.get_width()//2, 150))
            
            # Hints 
            for i, hint in enumerate(hints[:hints_used + 1]):
                hint_text = hint_font.render(f"Hint {i+1}: {hint}", True, COLORS['secondary'])
                screen.blit(hint_text, (WINDOW_WIDTH//2 - hint_text.get_width()//2, 250 + i*60))  # Increased spacing between hints
            
            # Bottom - Status Messages 
            if status_message:
                status_text = hint_font.render(status_message, True, status_color)
                screen.blit(status_text, (WINDOW_WIDTH//2 - status_text.get_width()//2, WINDOW_HEIGHT - 150))
            
            pygame.display.flip()
            
            # Get voice input
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
               #listening neeche wala msg
                listening_text = hint_font.render("Listening...", True, COLORS['primary'])
                screen.blit(listening_text, (WINDOW_WIDTH//2 - listening_text.get_width()//2, WINDOW_HEIGHT - 100))
                pygame.display.flip()
                
                try:
                    audio = recognizer.listen(source, timeout=5)
                    guess = recognizer.recognize_google(audio).lower()
                    attempts += 1
                    
                    # Display what was heard (edit mt krna )
                    heard_message = f"You said: {guess}"
                    heard_text = hint_font.render(heard_message, True, COLORS['secondary'])
                    screen.blit(heard_text, (WINDOW_WIDTH//2 - heard_text.get_width()//2, WINDOW_HEIGHT - 200))
                    pygame.display.flip()
                    
                    # Check guess
                    if guess == current_word:
                        game_score += 1
                        status_message = f"Correct! The word was {current_word}!"
                        status_color = COLORS['success']
                        round_complete = True
                    else:
                        if hints_used < len(hints) - 1:
                            hints_used += 1
                            status_message = "Wrong guess. Here's another hint!"
                        else:
                            status_message = "Wrong guess. No more hints!"
                        status_color = COLORS['error']
                    
                except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError) as e:
                    status_message = "Sorry, please try again."
                    status_color = COLORS['error']
            
            # quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return game_score
            
            pygame.time.delay(1000)
        
        #full screen
        screen.fill(COLORS['background'])
        
        #msg
        if attempts >= 3:
            messages = [
                f"Round Over! The word was: {current_word}",
                f"Your current score: {game_score}",
                "Press SPACE to play again",
                "Press ESC to quit"
            ]
        else:
            messages = [
                "Congratulations!",
                f"You guessed the word: {current_word}",
                f"Your current score: {game_score}",
                "Press SPACE to play again",
                "Press ESC to quit"
            ]
        
        # msg display
        for i, message in enumerate(messages):
            text = hint_font.render(message, True, COLORS['primary'])
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2 - 100 + i*50))
        
        pygame.display.flip()
        
        # Wait for player decision
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return game_score
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting_for_input = False  # Continue to next round
                    elif event.key == pygame.K_ESCAPE:
                        return game_score
        
        pygame.time.delay(500)

    return game_score



def spellbee():
    
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    
    #levels hta diya 
    words = [
        "encyclopedia", "pneumonia", "catastrophe", "surveillance",
        "conscious", "rhythm", "symphony", "phenomenon", "anonymous",
        "bureaucracy", "chromosome", "democracy", "hierarchy", "hygiene",
        "lieutenant", "millennium", "occurrence", "parliament", "prejudice"
    ]
    
    score = 0
    total_words = 5  # Number of words per game
    

    large_font = pygame.font.SysFont('arial', 48)
    medium_font = pygame.font.SysFont('arial', 36)
    small_font = pygame.font.SysFont('arial', 24)
    
    for round_num in range(total_words):
        word = random.choice(words)
        words.remove(word)
        screen.fill(COLORS['background'])
        round_text = large_font.render(f"Round {round_num + 1}/{total_words}", True, COLORS['primary'])
        screen.blit(round_text, (WINDOW_WIDTH//2 - round_text.get_width()//2, 50))
        
        score_text = medium_font.render(f"Score: {score}", True, COLORS['text'])
        screen.blit(score_text, (50, 50))
        
        instruction_text = medium_font.render("Listen to the word...", True, COLORS['secondary'])
        screen.blit(instruction_text, (WINDOW_WIDTH//2 - instruction_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
        
        pygame.display.flip()

        engine.say(f"Please spell the word: {word}")
        engine.runAndWait()
        
        screen.fill(COLORS['background'])
        spell_text = large_font.render("Now spell the word...", True, COLORS['primary'])
        screen.blit(spell_text, (WINDOW_WIDTH//2 - spell_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        
        listening_text = medium_font.render("Listening...", True, COLORS['secondary'])
        screen.blit(listening_text, (WINDOW_WIDTH//2 - listening_text.get_width()//2, WINDOW_HEIGHT//2))
        
        pygame.display.flip()
        
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10)

            user_spelling = recognizer.recognize_google(audio)
            user_spelling = ''.join(user_spelling.lower().split())
            

            screen.fill(COLORS['background'])
            heard_text = medium_font.render(f"You spelled: {user_spelling}", True, COLORS['text'])
            screen.blit(heard_text, (WINDOW_WIDTH//2 - heard_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            
  
            if user_spelling == word.lower():
                result_text = large_font.render("Correct!", True, COLORS['success'])
                engine.say("Correct spelling!")
            else:
                result_text = large_font.render("Incorrect", True, COLORS['error'])
                correct_text = medium_font.render(f"The correct spelling is: {word}", True, COLORS['text'])
                screen.blit(correct_text, (WINDOW_WIDTH//2 - correct_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
                engine.say("Incorrect spelling")
            
            screen.blit(result_text, (WINDOW_WIDTH//2 - result_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.flip()
            engine.runAndWait()
            
            if user_spelling == word.lower():
                score += 1

            pygame.time.delay(2000)
                
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            error_text = medium_font.render("Sorry, I couldn't understand your spelling.", True, COLORS['error'])
            screen.blit(error_text, (WINDOW_WIDTH//2 - error_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.flip()
            engine.say("Sorry, I couldn't understand your spelling")
            engine.runAndWait()
            pygame.time.delay(2000)
        except sr.RequestError:
            error_text = medium_font.render("Speech recognition service error.", True, COLORS['error'])
            screen.blit(error_text, (WINDOW_WIDTH//2 - error_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.flip()
            pygame.time.delay(2000)
    

    screen.fill(COLORS['background'])
    final_score_text = large_font.render(f"Final Score: {score}/{total_words}", True, COLORS['primary'])
    screen.blit(final_score_text, (WINDOW_WIDTH//2 - final_score_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
    
    if score == total_words:
        message = "Perfect score! You're a spelling champion!"
    elif score >= total_words * 0.7:
        message = "Great job! You're really good at spelling!"
    else:
        message = "Keep practicing! You'll get better!"
    
    message_text = medium_font.render(message, True, COLORS['secondary'])
    screen.blit(message_text, (WINDOW_WIDTH//2 - message_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
    

    continue_text = small_font.render("Press any key to continue...", True, COLORS['text'])
    screen.blit(continue_text, (WINDOW_WIDTH//2 - continue_text.get_width()//2, WINDOW_HEIGHT - 100))
    
    pygame.display.flip()
    engine.say(message)
    engine.runAndWait()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score
            elif event.type == pygame.KEYDOWN:
                waiting = False
    
    return score


def flash_cards():
    global current_question, current_answer, game_score, status_message, status_color, status_timer, is_showing_answer

    questions = {
        "What is the capital of France?": "paris",
        "What is 5 + 7?": "12",
        "What is the color of the sky?": "blue",
        "What planet is known as the Red Planet?": "mars",
        "Who wrote 'Hamlet'?": "shakespeare",
        "What is the largest mammal in the world?": "blue whale",
        "How many continents are there on Earth?": "7",
        "What is the boiling point of water in Celsius?": "100",
        "Who painted the Mona Lisa?": "da vinci",
        "What is the main language spoken in Brazil?": "portuguese"
    }
    game_score = 0
    status_message = ""
    status_color = COLORS['text']
    status_timer = 0  # Countdown timer for displaying status messages

    # question initialize krne ke liye
    current_question, current_answer = random.choice(list(questions.items()))
    is_showing_answer = False

    running = True
    while running:
        screen.fill(COLORS['background'])

        # Display - question
        question_text = font.render(current_question, True, COLORS['text'])
        question_rect = question_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(question_text, question_rect)

        # Display - game score
        score_text = font.render(f"Score: {game_score}", True, COLORS['text'])
        score_rect = score_text.get_rect(topleft=(20, 20))
        screen.blit(score_text, score_rect)

        # If answer mode  active
        if is_showing_answer:
            speak("Please answer the question.")
            user_answer = voice_control()

            if user_answer:
                user_answer = " ".join(user_answer.strip().lower().split())  # Normalize input

                # Check the answer using fuzzy matching(fuzzy ke baare mai pdhlena ek baar)
                if fuzz.ratio(user_answer, current_answer) >= 80:  # Adjust  as needed
                    game_score += 1
                    status_message = "Correct answer!"
                    status_color = COLORS['success']
                    speak(status_message)
                else:
                    status_message = f"Incorrect answer. The correct answer was {current_answer.capitalize()}."
                    status_color = COLORS['error']
                    speak(status_message)

            # Reset for the next question
            status_timer = 180 
            is_showing_answer = False
            current_question, current_answer = random.choice(list(questions.items()))

        # "Answer Question" button
        button_text = font.render("Answer Question" if not is_showing_answer else "Retry", True, COLORS['card'])
        button_rect = button_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
        pygame.draw.rect(screen, COLORS['primary'], button_rect.inflate(20, 20), border_radius=10)
        screen.blit(button_text, button_rect)

        #  "Quit" button
        quit_text = font.render("Quit", True, COLORS['error'])
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150))
        pygame.draw.rect(screen, COLORS['primary'], quit_rect.inflate(20, 20), border_radius=10)
        screen.blit(quit_text, quit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    if not is_showing_answer:
                        is_showing_answer = True
                    else:
                        is_showing_answer = False
                        current_question, current_answer = random.choice(list(questions.items()))
                        status_message = ""
                        status_timer = 0
                elif quit_rect.collidepoint(event.pos):
                    running = False

        
        if status_message and status_timer > 0:
            status_text = font.render(status_message, True, status_color)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            screen.blit(status_text, status_rect)
            status_timer -= 1

        # Update the display
        pygame.display.flip()
        clock = pygame.time.Clock()
        clock.tick(60)  

    pygame.quit()

def start_2048():
    speak("Starting 2048 game. This is a placeholder.")
def voice_control():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Voice recognition error: {e}")
            speak("Sorry, I'm having trouble connecting to the speech service.")
            return None
        except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.")
            return None
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")

games = ["word detective", "spellbee", "flash cards", "2048"]

def show_menu(status_message=None, status_color=(255, 0, 0)):
    screen.fill(COLORS['background'])
    
    # Display title
    title = font.render('Select a Game', True, COLORS['primary'])
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
    
    # Display game options
    for idx, game_name in enumerate(games):
        game_text = font.render(game_name, True, COLORS['text'])
        screen.blit(game_text, (WINDOW_WIDTH // 2 - game_text.get_width() // 2, 150 + idx * 60))
    
  
    if status_message:
        status_text = font.render(status_message, True, status_color)
        screen.blit(status_text, (WINDOW_WIDTH // 2 - status_text.get_width() // 2, WINDOW_HEIGHT - 100))
    
    pygame.display.flip()

def main():
    running = True
    show_menu()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        command = voice_control()
        if command:
            if command == "exit":
                running = False
            elif command == "menu":
                show_menu()
            else:
                start_game(command)
        
        global status_timer, status_message
        if status_timer > 0:
            status_timer -= 1
        else:
            status_message = ""
        
        show_menu()
    
    pygame.quit()
def start_game(game_name):
    global current_game
    game_name = game_name.strip().lower()
    print(f"Recognized game: {game_name}")
    
    for standard_name, variations in game_variations.items():
        if game_name in variations:
            if standard_name == "word detective":
                current_game = "word detective"
                word_detective()
            elif standard_name == "spellbee":
                current_game = "spellbee"
                spellbee()
            elif standard_name == "flash cards":
                current_game = "flash cards"
                flash_cards()
            elif standard_name == "2048":
                current_game = "2048"
                start_2048()
            return
    
    speak("Game not recognized.")

if __name__ == "__main__":
    main()