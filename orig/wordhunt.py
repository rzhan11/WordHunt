import time
import sys

START_TIME = time.time()

# CONSTANTS FOR GAME SETTINGS
GRAPH_MAX_X = 4
GRAPH_MAX_Y = 4
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 16

LENGTH_TO_POINTS = {3: 100, 4: 400, 5: 800, 6: 1400, 7: 1700, 8: 2000}
# WORD HUNT DOESN'T TAKE WORDS WITH 9+ LETTERS
# for i in range(9, MAX_WORD_LENGTH + 1):
#     LENGTH_TO_POINTS[i] = LENGTH_TO_POINTS[i - 1] + 300

words_by_len = None
found_words = None
graph = None


# USED FOR LIMITING POSSIBLE WORDS
def letters_to_freq(letters):
    freq = {}
    for c in letters:
        if c not in freq:
            freq[c] = 1
        else:
            freq[c] += 1
    return freq


def check_valid(freq, base_freq):
    for key in freq:
        if key not in base_freq or freq[key] > base_freq[key]:
            return False
    return True


def solve(letters):
    global words_by_len, found_words, graph

    freq = letters_to_freq(letters)

    with open("scrabble.txt") as file:
        lines = [line.strip().lower() for line in file][2:]

    words = [l for l in lines if MIN_WORD_LENGTH <= len(l) <= MAX_WORD_LENGTH and check_valid(letters_to_freq(l), freq)]
    words.sort()

    # CREATE STRING TREE STRUCTURE
    tree = {}
    for w in words:
        cur = tree
        for c in w:
            if c not in cur:
                cur[c] = {}
            cur = cur[c]
        cur[0] = 0

    # CREATE GRAPH STRUCTURE
    graph = [[letters[i * GRAPH_MAX_Y + j] for j in range(GRAPH_MAX_Y)] for i in range(GRAPH_MAX_X)]
    for i in range(GRAPH_MAX_X):
        for j in range(GRAPH_MAX_Y):
            print(graph[i][j], end=" ")
        print()
    print()

    # KEEP TRACK OF DFS RESULTS
    found_words = set()
    words_by_len = {i: [] for i in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1)}

    for i in range(GRAPH_MAX_X):
        for j in range(GRAPH_MAX_Y):
            if graph[i][j] in tree:
                dfs(i, j, tree[graph[i][j]], graph[i][j], {(i, j)})

    for key in words_by_len:
        words_by_len[key].sort()

    return words_by_len


def dfs(x, y, cur_tree, cur_word, used):
    if 0 in cur_tree and cur_word not in found_words:
        words_by_len[len(cur_word)] += [cur_word]
        found_words.add(cur_word)

    for i in range(max(x - 1, 0), min(x + 2, GRAPH_MAX_X)):
        for j in range(max(y - 1, 0), min(y + 2, GRAPH_MAX_Y)):
            pos = (i, j)
            val = graph[i][j]
            if pos not in used:
                if val in cur_tree:
                    used.add((i, j))
                    dfs(i, j, cur_tree[val], cur_word + val, used)
                    used.remove((i, j))


def get_results(words_by_len):
    total_words = 0
    total_points = 0
    for i in range(MAX_WORD_LENGTH, MIN_WORD_LENGTH - 1, -1):
        if len(words_by_len[i]) == 0:
            continue
        if i in LENGTH_TO_POINTS:
            cur_points = len(words_by_len[i]) * LENGTH_TO_POINTS[i]
        else:
            cur_points = 0
        total_words += len(words_by_len[i])
        total_points += cur_points
    return total_words, total_points


def print_results(words_by_len, total_words, total_points):
    for i in range(MAX_WORD_LENGTH, MIN_WORD_LENGTH - 1, -1):
        if len(words_by_len[i]) == 0:
            continue
        if i in LENGTH_TO_POINTS:
            cur_points = len(words_by_len[i]) * LENGTH_TO_POINTS[i]
        else:
            cur_points = 0
        print(i, "LETTERS (" + str(len(words_by_len[i])) + ", " + str(cur_points) + ")")
        print()
        for w in words_by_len[i]:
            print(w, end=" ")
        print()
        print()

    print("Total words:", total_words)
    print("Total points:", total_points)
    print()
