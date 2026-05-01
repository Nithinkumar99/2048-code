"""
2048 — Flask Web Edition
Endpoints:
  POST /api/new          → { board, score, best, state }
  POST /api/move         → { board, score, best, state, moved }
       body: { "direction": "U"|"D"|"L"|"R", "board": [...], "score": N, "best": N }
"""

from flask import Flask, jsonify, request, render_template
import random

app = Flask(__name__)

# ── Pure game logic (same as terminal version) ──────────────────────────────

def add_tile(board):
    empties = [(r, c) for r in range(4) for c in range(4) if board[r][c] == 0]
    if empties:
        r, c = random.choice(empties)
        board[r][c] = 4 if random.random() < 0.1 else 2

def new_game():
    board = [[0] * 4 for _ in range(4)]
    add_tile(board)
    add_tile(board)
    return board

def compress(row):
    new = [v for v in row if v != 0]
    new += [0] * (4 - len(new))
    return new

def merge(row):
    score = 0
    for i in range(3):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            score += row[i]
            row[i + 1] = 0
    return row, score

def move_left(board):
    total, new_b = 0, []
    for row in board:
        r = compress(row)
        r, s = merge(r)
        r = compress(r)
        new_b.append(r)
        total += s
    return new_b, total

def rotate_cw(board):
    return [list(row) for row in zip(*board[::-1])]

def rotate_ccw(board):
    return [list(row) for row in zip(*board)][::-1]

def apply_move(board, direction):
    if direction == "L":
        return move_left(board)
    if direction == "R":
        b = [row[::-1] for row in board]
        b, s = move_left(b)
        return [row[::-1] for row in b], s
    if direction == "U":
        b = rotate_ccw(board)
        b, s = move_left(b)
        return rotate_cw(b), s
    if direction == "D":
        b = rotate_cw(board)
        b, s = move_left(b)
        return rotate_ccw(b), s
    return board, 0

def board_changed(old, new):
    return any(old[r][c] != new[r][c] for r in range(4) for c in range(4))

def has_moves(board):
    for r in range(4):
        for c in range(4):
            if board[r][c] == 0:
                return True
            if c < 3 and board[r][c] == board[r][c + 1]:
                return True
            if r < 3 and board[r][c] == board[r + 1][c]:
                return True
    return False

def max_tile(board):
    return max(board[r][c] for r in range(4) for c in range(4))

def classify_state(board):
    if max_tile(board) >= 2048:
        return "won"
    if not has_moves(board):
        return "over"
    return "playing"

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/new", methods=["POST"])
def api_new():
    board = new_game()
    return jsonify(board=board, score=0, best=0, state="playing")

@app.route("/api/move", methods=["POST"])
def api_move():
    data = request.get_json()
    board     = data["board"]
    score     = data["score"]
    best      = data["best"]
    direction = data["direction"]        # U / D / L / R

    new_b, gained = apply_move(board, direction)
    moved = board_changed(board, new_b)

    if moved:
        board  = new_b
        score += gained
        best   = max(best, score)
        add_tile(board)

    return jsonify(board=board, score=score, best=best,
                   state=classify_state(board), moved=moved)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
