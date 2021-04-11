import time
import sys
import wordhunt

START_TIME = time.time()

# CONTROLS INPUT PARAMETERS
if len(sys.argv) != 2:
    print("Expected 1 argument, received " + str(len(sys.argv) - 1))
    exit()
else:
    letters = sys.argv[1].lower()
    if len(letters) == wordhunt.MAX_WORD_LENGTH:
        if not letters.isalpha():
            print("Argument can only contain letters")
            exit()
    else:
        print("Expected", wordhunt.MAX_WORD_LENGTH, "letters, received", len(letters))
        exit()

words_by_len = wordhunt.solve(letters)
total_words, total_points = wordhunt.get_results(words_by_len)
wordhunt.print_results(words_by_len, total_words, total_points)

print("Execution time (s):", round(time.time() - START_TIME(), 3))
