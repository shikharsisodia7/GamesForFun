#!/usr/bin/env python3
# Combined Calculator, Tic Tac Toe, and Hangman CLI game
# Save as a single file and run with Python 3.8+

import ast
import math
import operator
import random
import sys

# ---------- Utilities ----------
def safe_input(prompt="> "):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return ""

# ---------- Calculator ----------
class SafeEval(ast.NodeVisitor):
    ALLOWED_BINOPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    ALLOWED_UNARY = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, allow_funcs=True, allow_constants=True):
        # allow_funcs: math.* and abs/round
        if allow_funcs:
            funcs = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
            funcs.update({"abs": abs, "round": round})
            self.allowed_funcs = funcs
        else:
            self.allowed_funcs = {}
        if allow_constants:
            self.allowed_names = {"pi": math.pi, "e": math.e}
        else:
            self.allowed_names = {}

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Expr(self, node):
        # some AST variants wrap expressions in Expr/value
        # try to handle either attribute name used by the node
        if hasattr(node, "value"):
            return self.visit(node.value)
        if hasattr(node, "body"):
            return self.visit(node.body)
        return self.generic_visit(node)

    def visit_BinOp(self, node):
        if type(node.op) not in self.ALLOWED_BINOPS:
            raise ValueError("operator not allowed")
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.ALLOWED_BINOPS[type(node.op)](left, right)

    def visit_UnaryOp(self, node):
        if type(node.op) not in self.ALLOWED_UNARY:
            raise ValueError("unary operator not allowed")
        operand = self.visit(node.operand)
        return self.ALLOWED_UNARY[type(node.op)](operand)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            fname = node.func.id
            if fname not in self.allowed_funcs:
                raise ValueError("function not allowed")
            func = self.allowed_funcs[fname]
            args = [self.visit(a) for a in node.args]
            return func(*args)
        raise ValueError("invalid function call")

    def visit_Name(self, node):
        if node.id in self.allowed_names:
            return self.allowed_names[node.id]
        raise ValueError(f"invalid name: {node.id}")

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numeric constants allowed")

    # for Python <3.8
    def visit_Num(self, node):
        return node.n

    # for older Python AST versions where booleans/None used NameConstant
    def visit_NameConstant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numeric constants allowed")

def calc_repl():
    print("Calculator. Modes: 1) Basic  2) Scientific  (type 'back' to return)")
    mode = ""
    while mode not in ("1","2","back"):
        mode = safe_input("Choose calculator mode (1/2) or 'back': ").strip().lower()
    if mode == "back":
        return
    allow_funcs = mode == "2"
    allow_constants = mode == "2"  # scientific allows pi/e
    print("Enter expressions (or 'history', 'back'). Basic allows + - * / // % ** and numbers.")
    history = []
    while True:
        s = safe_input("calc> ").strip()
        if not s:
            continue
def print_board(board):
    chars = [c if c else " " for c in board]
    print(f" {chars[0]} | {chars[1]} | {chars[2]} ")
    print("---+---+---")
    print(f" {chars[3]} | {chars[4]} | {chars[5]} ")
    print("---+---+---")
    print(f" {chars[6]} | {chars[7]} | {chars[8]} ")

def check_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(x is not None for x in board):
        return "Draw"
    return None
    chars = [c if c else " " for c in b]
    print(f" {chars[0]} | {chars[1]} | {chars[2]} ")
    print("---+---+---")
    print(f" {chars[3]} | {chars[4]} | {chars[5]} ")
    print("---+---+---")
    print(f" {chars[6]} | {chars[7]} | {chars[8]} ")

def check_winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b1,c in wins:
        if b[a] and b[a]==b[b1]==b[c]:
            return b[a]
    if all(x is not None for x in b):
        return "Draw"
    return None

def minimax(board, player, ai_player, human_player):
    winner = check_winner(board)
    if winner == ai_player:
        return 1, None
    if winner == human_player:
        return -1, None
    if winner == "Draw":
        return 0, None
    best_score = -2 if player==ai_player else 2
    best_move = None
    for i in range(9):
        if board[i] is None:
            board[i] = player
            score, _ = minimax(board, "O" if player=="X" else "X", ai_player, human_player)
            board[i] = None
            if player==ai_player:
                if score > best_score:
                    best_score, best_move = score, i
            else:
                if score < best_score:
                    best_score, best_move = score, i
    return best_score, best_move

def choose_ai_move(board, ai_player, human_player, difficulty):
    avail = [i for i in range(9) if board[i] is None]
    if not avail:
        return None
    if difficulty == "easy":
        return random.choice(avail)
    if difficulty == "medium":
        # try win
        for i in avail:
            board[i] = ai_player
            if check_winner(board) == ai_player:
                board[i] = None
                return i
            board[i] = None
        # try block human win
        for i in avail:
            board[i] = human_player
            if check_winner(board) == human_player:
                board[i] = None
                return i
            board[i] = None
        # otherwise random
        return random.choice(avail)
    # hard -> perfect play
    _, mv = minimax(board, ai_player, ai_player, human_player)
    if mv is None:
        return random.choice(avail)
    return mv

def ttt_game():
    print("Tic Tac Toe. Modes: 1) 2-player  2) vs AI")
    mode = ""
    while mode not in ("1","2","back"):
        mode = safe_input("mode (1/2) or 'back': ").strip().lower()
        if mode == "back":
            return
    board = [None]*9
    current = "X"
    if mode=="1":
        while True:
            print_board(board)
            wk = check_winner(board)
            if wk:
                print("Result:", wk)
                break
            move = safe_input(f"Player {current} move (1-9) or 'back': ").strip()
            if move.lower()=="back":
                return
            if not move.isdigit() or not (1 <= int(move) <= 9):
                print("Invalid move.")
                continue
            idx = int(move)-1
            if board[idx]:
                print("Cell occupied.")
                continue
            board[idx] = current
            current = "O" if current=="X" else "X"
    else:
        # vs AI: choose difficulty and whether AI is X or O and who starts
        difficulty = ""
        while difficulty not in ("easy","medium","hard"):
            difficulty = safe_input("Choose difficulty (easy/medium/hard) or 'back': ").strip().lower()
            if difficulty == "back":
                return
        ai_player = ""
        while ai_player not in ("x","o","back"):
            ai_player = safe_input("Choose AI as X or O (X plays first) or 'back': ").strip().lower()
            if ai_player == "back":
                return
        ai_player = ai_player.upper()
        human_player = "O" if ai_player=="X" else "X"
        current = "X"  # X always starts
        while True:
            print_board(board)
            wk = check_winner(board)
            if wk:
                print("Result:", wk)
                break
            if current == human_player:
                move = safe_input(f"Your move ({human_player}) 1-9 or 'back': ").strip()
                if move.lower()=="back":
                    return
                if not move.isdigit() or not (1 <= int(move) <= 9):
                    print("Invalid move.")
                    continue
                idx = int(move)-1
                if board[idx]:
                    print("Cell occupied.")
                    continue
                board[idx] = human_player
            else:
                print(f"AI ({ai_player}) thinking ({difficulty})...")
                mv = choose_ai_move(board, ai_player, human_player, difficulty)
                if mv is None:
                    print("No moves left.")
                    current = "O" if current=="X" else "X"
                    continue
                board[mv] = ai_player
                print("AI moved at", mv+1)
            current = "O" if current=="X" else "X"

# ---------- Hangman ----------
WORDLIST = [
    "python","programming","hangman","variable","function","exception","keyboard",
    "computer","science","algorithm","interface","network","database","repository",
    "security","encryption","binary","integer","string","boolean","iteration",
    "recursion","compiler","interpreter","module","package","virtual","environment",
    "development","testing","deployment"
]

HANGMAN_PICS = [
    """
     +---+
     |   |
         |
         |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========
    """,
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========
    """,
]

def hangman_game():
    print("Hangman. Options: 1) Random word (AI chooses)  2) Enter hidden word for another player to guess")
    choice = ""
    while choice not in ("1","2","back"):
        choice = safe_input("1) Random  2) Enter hidden (or 'back'): ").strip().lower()
    if choice=="back":
        return
    if choice=="1":
        secret = random.choice(WORDLIST)
    else:
        print("Enter the secret word (letters only). Input will be hidden on screen if possible.")
        try:
            import getpass
            secret = getpass.getpass("Secret word: ").strip()
        except Exception:
            secret = safe_input("Secret word: ").strip()
        if not secret or not secret.isalpha():
            print("Invalid secret. Aborting.")
            return
    secret = secret.lower()
    guessed = set()
    wrong = 0
    max_wrong = len(HANGMAN_PICS)-1
    # hint rules: a 'hint' command reveals one unrevealed letter but costs 1 wrong life.
    while True:
        print(HANGMAN_PICS[min(wrong, max_wrong)])
        display = " ".join([c if c in guessed else "_" for c in secret])
        print("Word:", display)
        print("Guessed:", " ".join(sorted(guessed)) if guessed else "(none)")
        if all(c in guessed for c in secret):
            print("You win! The word was:", secret)
            return
        if wrong >= max_wrong:
            print("You lost. The word was:", secret)
            return
        action = safe_input("Guess a letter, whole word, or 'hint' (or 'quit'): ").strip().lower()
        if not action:
            continue
        if action in ("quit","back"):
            return
        if action == "hint":
            # reveal one unrevealed letter; costs 1 wrong attempt
            unrevealed = [c for c in set(secret) if c not in guessed]
            if not unrevealed:
                print("No hints available.")
                continue
            reveal = random.choice(unrevealed)
            guessed.add(reveal)
            wrong += 1
            print(f"Hint: revealed letter '{reveal}' (this costs 1 life).")
            continue
        if len(action) == 1:
            if not action.isalpha():
                print("Enter a letter.")
                continue
            if action in guessed:
                print("Already guessed.")
                continue
            guessed.add(action)
            if action not in secret:
                wrong += 1
                print("Wrong!")
            else:
                print("Good!")
        else:
            if not action.isalpha():
                print("Word guesses must be alphabetic.")
                continue
            if action == secret:
                print("You win! The word was:", secret)
                return
            else:
                wrong += 1
                print("Wrong guess for whole word.")

# ---------- Main Menu ----------
def main_menu():
    print("Welcome. Options: 1) Calculator  2) TicTacToe  3) Hangman  4) Quit")
    while True:
        choice = safe_input("Choose (1/2/3/4): ").strip().lower()
        if choice in ("1","calc","calculator"):
            calc_repl()
        elif choice in ("2","ttt","tictactoe","tictac"):
            ttt_game()
        elif choice in ("3","hangman","hang"):
            hangman_game()
        elif choice in ("4","quit","exit"):
            print("Goodbye.")
            return
        elif choice == "":
            continue
        else:
            print("Unknown option.")

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print("An unexpected error occurred:", e)
        sys.exit(1)