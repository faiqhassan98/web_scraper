import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Function to save results to a CSV file
def save_results(results, filename='wahlomat_results.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Question', 'Your Answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            # Map the answer to 'Agree', 'Neutral', or 'Disagree'
            answer = {'a': 'Agree', 'b': 'Neutral', 'c': 'Disagree'}.get(result['Your Answer'], result['Your Answer'])
            writer.writerow({'Question': result['Question'], 'Your Answer': answer})

# Function to navigate through questions and capture results
def navigate_and_capture_answers():
    results = []
    try:
        # Start WebDriver
        driver = webdriver.Chrome()
        driver.get("https://www.wahl-o-mat.de/bundestagswahl2021/app/main_app.html")
        driver.maximize_window()  # Maximize the window for better interaction
        time.sleep(2)  # Wait for initial loading

        # Click Start button
        start_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "button--big")))
        start_button.click()

        # Wait for question text to be visible with increased waiting time
        WebDriverWait(driver, 25).until(EC.visibility_of_element_located((By.CLASS_NAME, "theses__text")))

        # Navigate through slides (questions)
        slides = driver.find_elements(By.CSS_SELECTOR, ".theses__slider .glide__slide .theses__box")
        print(f"Total slides (questions): {len(slides)}")
        questions_attempted = 0
        for slide in slides:
            # Capture question text
            question_text_element = WebDriverWait(slide, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.theses__text")))
            question_text = question_text_element.text
            print("Question:", question_text)

            # Find parent element containing answer buttons
            answers_parent = WebDriverWait(slide, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "theses__actions")))

            # Find answer buttons within parent element
            answer_buttons = answers_parent.find_elements(By.CLASS_NAME, "theses-btn")

            # Map options a, b, c to their corresponding data-choice values
            choice_map = {'a': '1', 'b': '0', 'c': '-1'}

            # Print options and prompt user for input
            print("Options:")
            for choice, value in sorted(choice_map.items()):
                if value == '1':
                    option_text = "Agree"
                elif value == '0':
                    option_text = "Neutral"
                elif value == '-1':
                    option_text = "Disagree"
                print(f"{choice}: {option_text}")
            selected_choice = input("Enter your choice (a/b/c): ").lower()

            # Check if the selected choice is valid
            while selected_choice not in choice_map:
                print("Please enter a valid option (a/b/c).")
                selected_choice = input("Enter your choice (a/b/c): ").lower()

            # Find the button corresponding to the selected choice
            chosen_button = next((button for button in answer_buttons if button.get_attribute("data-choice") == choice_map[selected_choice]), None)

            # Click on the chosen button if it exists
            if chosen_button:
                chosen_button.click()

                # Add the selected choice to results
                results.append({'Question': question_text, 'Your Answer': selected_choice})
            else:
                print("Failed to click the button. Please try again.")

            # Sleep to ensure page loads fully
            time.sleep(1)
            questions_attempted += 1
            print(f"Questions attempted: {questions_attempted}")

    except Exception as e:
        print("An error occurred:", e)
        raise  # Reraise the exception to understand the exact cause of the error
    finally:
        # Save results and close WebDriver
        save_results(results)
        driver.quit()

# Execute the function
navigate_and_capture_answers()
