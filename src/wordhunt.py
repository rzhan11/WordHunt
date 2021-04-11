import time
import sys

ONLINE = True

START_TIME = time.time()

# CONSTANTS FOR GAME SETTINGS
GRAPH_MAX_X = 4
GRAPH_MAX_Y = 4
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 16

LENGTH_TO_POINTS = {3: 100, 4: 400, 5: 800, 6: 1400, 7: 1800, 8: 2200, 9: 2600, 10: 3000}
# WORD HUNT DOESN'T TAKE WORDS WITH 11+ LETTERS
for i in range(11, MAX_WORD_LENGTH + 1):
    LENGTH_TO_POINTS[i] = 0

words_by_len = None
word_paths = None
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
    global words_by_len, word_paths, graph

    freq = letters_to_freq(letters)

    if ONLINE:
        file_name = "./src/scrabble.txt"
    else:
        file_name = "scrabble.txt"

    with open(file_name) as file:
        lines = [line.strip().upper() for line in file][2:]

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

    # PRINT GRAPH STRUCTURE
    if not ONLINE:
        for i in range(GRAPH_MAX_X):
            for j in range(GRAPH_MAX_Y):
                print(graph[i][j], end=" ")
            print()
        print()

    # KEEP TRACK OF DFS RESULTS
    word_paths = {}
    words_by_len = {i: [] for i in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1)}

    for i in range(GRAPH_MAX_X):
        for j in range(GRAPH_MAX_Y):
            if graph[i][j] in tree:
                dfs(i, j, tree[graph[i][j]], graph[i][j], [(i, j)])

    for key in words_by_len:
        words_by_len[key].sort()

    return words_by_len, word_paths


def dfs(x, y, cur_tree, cur_word, path):
    if 0 in cur_tree:
        if cur_word not in word_paths:
            words_by_len[len(cur_word)] += [cur_word]
            word_paths[cur_word] = []
        word_paths[cur_word] += [(calc_path_cost(path), [*path])]

    for i in range(max(x - 1, 0), min(x + 2, GRAPH_MAX_X)):
        for j in range(max(y - 1, 0), min(y + 2, GRAPH_MAX_Y)):
            pos = (i, j)
            val = graph[i][j]
            if pos not in path:
                if val in cur_tree:
                    path += [(i, j)]
                    dfs(i, j, cur_tree[val], cur_word + val, path)
                    path.pop()


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


LATERAL_SWIPE_COST = 1
'''less penalty if surrounding tiles have already been used'''
DIAGONAL_SWIPE_COST = 4
OCCUPIED_DIAGONAL_DISCOUNT = 0.5 ** 0.5

SAME_DIRECTION_DISCOUNT = 0.5


def calc_path_cost(path):
    total_cost = 3
    prev_move = None

    for i in range(len(path) - 1):
        p = path[i]
        move = diff(p, path[i + 1])
        if abs(move[0]) + abs(move[1]) == 1:
            move_cost = LATERAL_SWIPE_COST
        else:
            move_cost = DIAGONAL_SWIPE_COST
            h = add(p, (move[0], 0))
            v = add(p, (0, move[1]))
            if h in path[:i]:
                move_cost *= OCCUPIED_DIAGONAL_DISCOUNT
            if v in path[:i]:
                move_cost *= OCCUPIED_DIAGONAL_DISCOUNT
        if move == prev_move:
            move_cost *= SAME_DIRECTION_DISCOUNT
        total_cost += move_cost
        prev_move = move

    return total_cost


def diff(start, end):
    return (end[0] - start[0], end[1] - start[1])


def add(start, dir):
    return (start[0] + dir[0], start[1] + dir[1])


def calc_similarity(path1, path2):
    if path1 is None or path2 is None:
        return 1
    longest = 0
    for s_i in range(len(path1)):
        for s_j in range(len(path2)):
            cur = 0
            for i in range(min(len(path1) - s_i, len(path2) - s_j)):
                if path1[s_i + i] == path2[s_j + i]:
                    cur += 1
                else:
                    break
            longest = max(longest, cur)
    front = 0
    if path1[0] == path2[0]:
        front = 5
    if longest == min(len(path1), len(path2)):
        return 1000 / abs(len(path1) - len(path2))
    return (1 + longest + front)


def find_word_order(words_by_len, word_paths):
    prev_path = None
    word_order = []
    used = set()
    while len(word_order) < len(word_paths):
        best_ratio = -1
        best_pair = None
        for key in word_paths:
            if key in used:
                continue
            for p in word_paths[key]:
                penalty = 3 + p[0] / calc_similarity(p[1], prev_path)
                ratio = LENGTH_TO_POINTS[len(key)] / penalty
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_pair = (key, p[1])
        word_order += [best_pair]
        used.add(best_pair[0])
        prev_path = best_pair[1]

    return word_order
