import time
import sys
import wordhunt
import json

START_TIME = time.time()

ret = {}

# CONTROLS INPUT PARAMETERS
if len(sys.argv) != 2:
    ret["status"] = "Expected 1 argument, received " + str(len(sys.argv) - 1)
    print(json.dumps(ret))
    exit()
else:
    letters = sys.argv[1].upper()
    if len(letters) == wordhunt.MAX_WORD_LENGTH:
        if letters.isalpha():
            ret["status"] = "Valid"
        else:
            ret["status"] = "Argument can only contain letters"
            print(json.dumps(ret))
            exit()
    else:
        ret["status"] = "Expected " + str(wordhunt.MAX_WORD_LENGTH) + " letters, received " + str(len(letters))
        print(json.dumps(ret))
        exit()

ret["words_by_len"], ret["word_paths"] = wordhunt.solve(letters)
ret["total_words"], ret["total_points"] = wordhunt.get_results(ret["words_by_len"])

if not wordhunt.ONLINE:
    wordhunt.print_results(ret["words_by_len"], ret["total_words"], ret["total_points"])

ret["word_order"] = wordhunt.find_word_order(ret["words_by_len"], ret["word_paths"])

ret["time"] = round(time.time() - START_TIME, 3)

if wordhunt.ONLINE:
    print(json.dumps(ret))
else:
    for i in range(min(50, len(ret["word_order"]))):
        print(ret["word_order"][i])
    print("Execution time (s):", ret["time"])
