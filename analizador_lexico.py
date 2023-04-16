import unicodedata
from sys import stdin
from io import TextIOWrapper

stdin.reconfigure(encoding='utf-8')


class Token:

    def __init__(self, token_name, row, column):
        self.token_name = token_name
        self.row = row
        self.column = column

    def __repr__(self):
        return ("<" +
                self.token_name + ", " +
                str(self.row) + ", " +
                str(self.column) +
                ">")

class Id(Token):

    def __init__(self, token_name, row, column, value):
        super().__init__(token_name, row, column)
        self.value = value

    def __repr__(self):
        return ("<" +
                self.token_name + ", " +
                self.value + ", " +
                str(self.row) + ", " +
                str(self.column) +
                ">")


class Error(Token):

    def __init__(self, token_name, row, column):
        super().__init__(token_name, row, column)

    def __repr__(self):
        return (">>> " +
                self.token_name + " " +
                "(Linea: " + str(self.row) + ", " +
                "Posicion: " + str(self.column) + ")"
                )


def main():
    row = 0
    all_tokens = list()
    input_stream = TextIOWrapper(stdin.buffer, encoding='utf-8')
    for line in stdin:
        if line == '':  # If empty string is read then stop the loop
            break
        all_tokens = all_tokens + get_tokens(line, row, 0, [])
        if len(all_tokens) > 0 and all_tokens[-1].token_name == "Error lexico":
            break
        row += 1
    print(
        unicodedata.normalize("NFKD",
                              "\n".join(token.__repr__() for token in all_tokens)))


def is_reserved_word(word):
    """
        1. Check if the current word is on the reserve_words list.

    :param word:  "TextWindow"
    :return: True
    """
    reserve_words = ["TextWindow", "If", "Or", "And", "Array", "Sub", "Else", "ElseIf",
                     "For", "EndFor", "While", "EndWhile", "EndIf", "Goto", "To",
                     "True", "False", "Then", "EndSub", "Program", "Step", "Stack",
                     "Clock", "File", "Flickr", "GraphicsWindow", "Dictionary", "Desktop",
                     "ImageList", "Math", "Mouse", "Network", "Shapes", "Sound", "Text",
                     "TextWindow", "Timer", "Turtle"]
    return word in reserve_words


def is_token_operator(word, token_operators):
    return word in token_operators.keys()


def get_token_operator(line, column, token_operators):
    token_operator = None
    length = len(line)
    if column < length:
        if column < length - 1 and is_token_operator(line[column] + line[column + 1], token_operators):
            token_operator = line[column] + line[column + 1]
        elif is_token_operator(line[column], token_operators):
            token_operator = line[column]
    return token_operator


def get_word(line, column):
    """
    :param line: String of characters of only one line of the source code
    :param column: Current line's column index
    :return:
        word: a line's substring of characters
    """
    initial_column = column
    length = len(line)
    while column < length - 1 and is_valid_word_character(line[column + 1]):
        column += 1
    return line[initial_column:column + 1]


def is_valid_word_character(character):
    return character.isalnum() or character == "_"


def is_valid_numeric_character(character, has_period):
    return character.isdigit() or (character == "." and not has_period)


def get_number(line, column):
    """
    :param line: String of characters of only one line of the source code
    :param column: Current line's column index
    :return:
        word: a line's substring of valid number. Example:
            Valid: 3.3215 One period or none are allowed
            Invalid: 3.332514.32 double periods are not allowed
    """
    initial_column = column
    length = len(line)
    has_period = False
    while column < length - 1 and is_valid_numeric_character(line[column + 1], has_period):
        if line[column + 1] == "." and has_period:
            break
        elif line[column + 1] == ".":
            has_period = True
        column += 1
    return line[initial_column:column + 1]


def update_column(column, add):
    return column + add


def get_text(line, column):
    initial_column = column
    length = len(line)
    while column < length - 1 and line[column + 1] != '"':
        column += 1
    return line[initial_column:column + 2]


def get_tokens(line, row, column, tokens):
    """
    function that returns a list of tokens of the given line

    :param line:
    :param row:
    :param column:
    :param tokens:
    :return:
    """
    token_operators = {
        "=": "tkn_equals",
        ".": "tkn_period",
        ",": "tkn_comma",
        ":": "tkn_colon",
        "[": "tkn_left_brac",
        "]": "tkn_right_brac",
        "(": "tkn_left_paren",
        ")": "tkn_right_paren",
        "+": "tkn_plus",
        "-": "tkn_minus",
        "*": "tkn_times",
        "/": "tkn_div",
        "<>": "tkn_diff",
        "<": "tkn_less",
        "<=": "tkn_leq",
        ">": "tkn_greater",
        ">=": "tkn_geq"
    }

    token = None
    if column < len(line):
        word = ""
        if line[column] == "'":
            # "end condition"
            return tokens
        elif line[column].isalpha():
            word = get_word(line, column)
            if is_reserved_word(word):
                token = Token(word, row + 1, column + 1)
            else:
                token = Id("id", row + 1, column + 1, word)
        elif line[column] == '"':
            word = get_text(line, column)
            token = Id("tkn_text", row + 1, column + 1, word[1:-1])
        elif line[column].isdigit():
            word = get_number(line, column)
            token = Id("tkn_number", row + 1, column + 1, word)
        elif is_token_operator(line[column], token_operators):
            word = get_token_operator(line, column, token_operators)
            token_operator = token_operators.get(word)
            token = Token(token_operator, row + 1, column + 1)
        elif line[column] in ["{", "}", "!", "_"]:
            token = Error("Error lexico", row + 1, column + 1)
            column = column + len(line)

        if token is not None and column == 0:
            return get_tokens(line, row, update_column(column, len(word)), tokens + [token])
        elif token is not None:
            return get_tokens(line, row, update_column(column, len(word)), tokens + [token])
        return get_tokens(line, row, update_column(column, len(word) + 1), tokens)
    return tokens


if __name__ == "__main__":
    main()


