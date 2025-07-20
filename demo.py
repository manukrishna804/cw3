#!/usr/bin/env python3
"""
Demo script for Sign Language Learning App
This script simulates the app functionality without external dependencies
"""

import time
import random
import json
from datetime import datetime, timedelta

class SignLanguageDemo:
    def __init__(self):
        self.user_progress = {
            'level': 'beginner',
            'completed_exercises': [],
            'current_exercise': None,
            'total_score': 0
        }
        
        # Sign patterns for demo
        self.sign_patterns = {
            "A": [1, 0, 0, 0, 0],  # Thumb only
            "B": [0, 1, 1, 1, 1],  # Four fingers up
            "C": [1, 1, 1, 0, 0],  # Thumb, index, middle
            "D": [0, 1, 0, 0, 0],  # Index finger only
            "E": [0, 0, 0, 0, 0],  # Closed fist
            "F": [1, 0, 1, 1, 1],  # Thumb, middle, ring, pinky
            "G": [1, 1, 0, 0, 0],  # Thumb and index
            "H": [0, 1, 1, 0, 0],  # Index and middle
            "I": [0, 0, 0, 0, 1],  # Pinky only
            "J": [0, 0, 0, 1, 0],  # Ring finger only
        }
        
        self.number_patterns = {
            "0": [0, 0, 0, 0, 0],  # Closed fist
            "1": [0, 1, 0, 0, 0],  # Index finger only
            "2": [0, 1, 1, 0, 0],  # Index and middle
            "3": [0, 1, 1, 1, 0],  # Index, middle, ring
            "4": [0, 1, 1, 1, 1],  # Four fingers
            "5": [1, 1, 1, 1, 1],  # All fingers
        }
        
        self.mannerism_patterns = {
            "HELLO": [1, 1, 0, 0, 0],  # Thumb and index
            "THANK YOU": [1, 0, 0, 0, 0],  # Thumb up
            "PLEASE": [1, 1, 1, 0, 0],  # Three fingers
            "GOOD": [1, 1, 0, 0, 0],  # Thumb and index
            "BAD": [0, 0, 0, 0, 0],  # Closed fist
        }
        
        self.current_exercise = None
        self.current_letters = []
        
    def generate_exercise(self):
        """Generate exercise based on user progress"""
        level = self.user_progress['level']
        completed = self.user_progress['completed_exercises']
        
        if level == 'beginner' and len(completed) < 3:
            # Initial exercises: alphabets, numbers, basic mannerisms
            if len(completed) == 0:
                return {
                    'type': 'alphabet',
                    'target': 'A',
                    'description': 'Show the sign for letter A (thumb only)',
                    'pattern': self.sign_patterns['A'],
                    'level': 'beginner'
                }
            elif len(completed) == 1:
                return {
                    'type': 'number',
                    'target': '1',
                    'description': 'Show the sign for number 1 (index finger only)',
                    'pattern': self.number_patterns['1'],
                    'level': 'beginner'
                }
            elif len(completed) == 2:
                return {
                    'type': 'mannerism',
                    'target': 'HELLO',
                    'description': 'Show the sign for HELLO (thumb and index finger)',
                    'pattern': self.mannerism_patterns['HELLO'],
                    'level': 'beginner'
                }
        else:
            # Generate word building exercises
            words = ['CAT', 'DOG', 'HAT', 'SUN', 'BIG', 'RED', 'BLUE', 'GREEN']
            word = random.choice(words)
            
            return {
                'type': 'word_building',
                'target': word,
                'description': f'Spell the word "{word}" using sign language letters',
                'level': level,
                'letters': list(word)
            }
    
    def recognize_sign(self, fingers):
        """Recognize sign from finger pattern"""
        # Check alphabet patterns
        for letter, pattern in self.sign_patterns.items():
            if fingers == pattern:
                return letter, 'alphabet'
        
        # Check number patterns
        for number, pattern in self.number_patterns.items():
            if fingers == pattern:
                return number, 'number'
        
        # Check mannerism patterns
        for mannerism, pattern in self.mannerism_patterns.items():
            if fingers == pattern:
                return mannerism, 'mannerism'
        
        return None, None
    
    def simulate_hand_tracking(self):
        """Simulate hand tracking by generating random finger patterns"""
        patterns = [
            [1, 0, 0, 0, 0],  # A
            [0, 1, 0, 0, 0],  # 1
            [1, 1, 0, 0, 0],  # L
            [0, 1, 1, 0, 0],  # U
            [1, 1, 1, 1, 1],  # O
            [0, 0, 0, 0, 0],  # Closed fist
        ]
        return random.choice(patterns)
    
    def start_exercise(self):
        """Start a new exercise"""
        self.current_exercise = self.generate_exercise()
        self.current_letters = []
        
        print(f"\n🎯 New Exercise Started!")
        print(f"Type: {self.current_exercise['type'].upper()}")
        print(f"Target: {self.current_exercise['target']}")
        print(f"Description: {self.current_exercise['description']}")
        print("\nShow your hand sign to the camera...")
        
        return self.current_exercise
    
    def check_sign(self, fingers):
        """Check if the sign matches the current exercise"""
        recognized_sign, sign_type = self.recognize_sign(fingers)
        
        if not recognized_sign:
            return {
                'success': True,
                'recognized': None,
                'correct': False,
                'message': 'No sign recognized'
            }
        
        if self.current_exercise['type'] == 'word_building':
            # For word building, check if the letter is correct
            target_word = self.current_exercise['target']
            
            if recognized_sign in target_word and recognized_sign not in self.current_letters:
                self.current_letters.append(recognized_sign)
                is_complete = len(self.current_letters) == len(target_word)
                
                if is_complete:
                    # Update progress
                    self.user_progress['completed_exercises'].append({
                        'type': 'word_building',
                        'word': target_word,
                        'completed_at': datetime.now().isoformat()
                    })
                    
                    # Check if ready for next level
                    if len(self.user_progress['completed_exercises']) >= 5:
                        self.user_progress['level'] = 'intermediate'
                
                return {
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': True,
                    'current_letters': self.current_letters,
                    'is_complete': is_complete
                }
            else:
                return {
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': False,
                    'message': 'Letter not needed or already used'
                }
        else:
            # For other exercise types
            target = self.current_exercise['target']
            if recognized_sign == target:
                # Update progress
                self.user_progress['completed_exercises'].append({
                    'type': self.current_exercise['type'],
                    'target': target,
                    'completed_at': datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': True,
                    'exercise_complete': True
                }
            else:
                return {
                    'success': True,
                    'recognized': recognized_sign,
                    'correct': False,
                    'message': f'Try showing the sign for {target}'
                }
    
    def show_progress(self):
        """Display user progress"""
        completed = self.user_progress['completed_exercises']
        level = self.user_progress['level']
        
        print(f"\n📊 Progress Report")
        print(f"Level: {level}")
        print(f"Exercises Completed: {len(completed)}")
        print(f"Total Score: {self.user_progress['total_score']}")
        
        if completed:
            print("\nRecent Exercises:")
            for i, exercise in enumerate(completed[-5:], 1):
                if exercise['type'] == 'word_building':
                    print(f"  {i}. Word Building: {exercise['word']}")
                else:
                    print(f"  {i}. {exercise['type'].title()}: {exercise['target']}")
        else:
            print("\nNo exercises completed yet.")
    
    def run_demo(self):
        """Run the interactive demo"""
        print("🤟 Sign Language Learning App - Demo Mode")
        print("=" * 50)
        print("This demo simulates the sign language learning experience.")
        print("You can test the exercise flow without camera access.")
        print("\nCommands:")
        print("- 'start': Start a new exercise")
        print("- 'sign <letter/number>': Simulate showing a sign")
        print("- 'progress': Show your progress")
        print("- 'help': Show this help")
        print("- 'quit': Exit the demo")
        print("=" * 50)
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'quit':
                    print("👋 Thanks for trying the demo!")
                    break
                elif command == 'help':
                    print("\nCommands:")
                    print("- 'start': Start a new exercise")
                    print("- 'sign <letter/number>': Simulate showing a sign")
                    print("- 'progress': Show your progress")
                    print("- 'help': Show this help")
                    print("- 'quit': Exit the demo")
                elif command == 'start':
                    self.start_exercise()
                elif command == 'progress':
                    self.show_progress()
                elif command.startswith('sign '):
                    sign_input = command[5:].upper()
                    
                    # Simulate finger pattern based on input
                    if sign_input in self.sign_patterns:
                        fingers = self.sign_patterns[sign_input]
                    elif sign_input in self.number_patterns:
                        fingers = self.number_patterns[sign_input]
                    elif sign_input in self.mannerism_patterns:
                        fingers = self.mannerism_patterns[sign_input]
                    else:
                        print(f"❌ Unknown sign: {sign_input}")
                        continue
                    
                    print(f"🤚 Showing sign: {sign_input} (Pattern: {fingers})")
                    
                    if self.current_exercise:
                        result = self.check_sign(fingers)
                        
                        if result['correct']:
                            print(f"✅ Correct! You signed {result['recognized']}")
                            
                            if result.get('exercise_complete'):
                                print("🎉 Exercise completed!")
                                self.current_exercise = None
                            elif result.get('is_complete'):
                                print("🎉 Word completed!")
                                self.current_exercise = None
                        else:
                            print(f"❌ {result['message']}")
                    else:
                        print("❌ No active exercise. Use 'start' to begin.")
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    demo = SignLanguageDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 