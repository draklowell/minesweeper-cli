"""
Minesweeper game
"""

import random
import string


#### CORE GAME FUNCTIONS ####
NEIGHBOURS_SHIFTS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]


def is_visible(table: list[list[int]], position: tuple[int, int]) -> bool:
    """
    Check if the cell at the given position is visible to the player.

    :param table: list[list[int]]
    :param position: tuple[int, int], position in the form of (x, y)

    :returns: bool, True if cell is visible
    """
    if table[position[1]][position[0]] > 0:
        return True

    return False


def get_value(table: list[list[int]], position: tuple[int, int]) -> int | None:
    """
    Get the value of the cell at the given position.

    :param table: list[list[int]]
    :param position: tuple[int, int], position in the form of (x, y)

    :returns: int | None: None if cell is a mine. Int between 0 and 8
    is number of mines around the cell.
    """
    if table[position[1]][position[0]] == 0:
        return None

    return abs(table[position[1]][position[0]]) - 1


def create_table(
    width: int,
    height: int,
    mines_number: int,
    ignore_position: tuple[int, int] | None = None,
    randomizer: random.Random | None = None,
) -> list[list[int]]:
    """
    Create table of the specified size and with randomly placed mines,
    number of which is also specified. You can set specific seed to
    generate mine positions via randomizer parameter.

    Table is a 2D array where each cell (x) is an integer.
    If x is between 1 and 9, then there are x-1 mines around, and cell is visible.
    If x is between -9 and -1, then there are -x-1 mines around, and cell is hidden.
    If x is 0, then there is a mine.

    :param width: int, width of the table
    :param height: int, height of the table
    :param mines_number: int, number of mines placed on the table
    :param ignore_position: tuple[int, int], ignore this positions and its neighbouts
    when placing mines
    :param randomizer: random.Random | None, randomizer to generate positions
    of the mines. If None, creates a new instance of random.Random.

    :returns: list[list[int]]], generated table

    :raises: ValueError, if there are more mines than can be placed
    """
    if randomizer is None:
        randomizer = random.Random()

    table = [[-1] * width for _ in range(height)]
    positions = [(x, y) for y in range(height) for x in range(width)]

    if ignore_position:
        if ignore_position in positions:
            positions.remove(ignore_position)

        for shift_x, shift_y in NEIGHBOURS_SHIFTS:
            neighbour_x = ignore_position[0] + shift_x
            neighbour_y = ignore_position[1] + shift_y
            if (neighbour_x, neighbour_y) in positions:
                positions.remove((neighbour_x, neighbour_y))

    if len(positions) < mines_number:
        raise ValueError(
            f"Table is too small for specified mines number \
                         ({len(positions)} table size, {mines_number} mines"
        )

    mines_positions = randomizer.sample(positions, mines_number)
    # Place generated mines
    for x, y in mines_positions:
        table[y][x] = 0

        # Iterate over all neighbours
        for shift_x, shift_y in NEIGHBOURS_SHIFTS:
            neighbour_x = x + shift_x
            neighbour_y = y + shift_y

            # Check for boundaries
            if neighbour_y < 0 or neighbour_y >= height:
                continue
            if neighbour_x < 0 or neighbour_x >= width:
                continue

            # Increase neighbour's number of mines around if there is no mine
            if table[neighbour_y][neighbour_x] < 0:
                table[neighbour_y][neighbour_x] -= 1

    return table


def disclose(
    table: list[list[int]],
    position: tuple[int, int],
    recursive_visited: list[tuple[int, int]] | None = None,
) -> bool | None:
    """
    Disclose the cell at the given position.

    :param table: list[list[int]]
    :param position: tuple[int, int], position in the form of (x, y)
    :param recursive_visited: list[tuple[tuple[int, int], bool]] | None, list of visited
    positions in the recursive algorithm

    :returns: bool | None, None if the position is already visible.
    False if the player hit a mine, True otherwise.
    """
    # Check for boundaries
    if (
        position[1] < 0
        or position[1] >= len(table)
        or position[0] < 0
        or position[0] >= len(table[0])
    ):
        return None

    if recursive_visited is None:
        recursive_visited = []

    if position in recursive_visited:
        return None

    recursive_visited.append(position)

    # Check if cell is hidden
    if is_visible(table, position):
        return None

    value = get_value(table, position)

    if value is None:
        return False

    table[position[1]][position[0]] = value + 1

    if value == 0:
        # Disclose neighbours
        for shift_x, shift_y in NEIGHBOURS_SHIFTS:
            neighbour_x = position[0] + shift_x
            neighbour_y = position[1] + shift_y

            disclose(table, (neighbour_x, neighbour_y), recursive_visited)

    return True


def disclose_whole(table: list[list[int]]):
    """
    Disclose all cells in the table.

    :param table: list[list[int]]
    """

    for y, rows in enumerate(table):
        for x, cell in enumerate(rows):
            if cell == 0:
                continue

            table[y][x] = abs(cell)


def is_game_active(table: list[list[int]]) -> bool:
    """
    Check if there are hidden cells without bombs on the table.

    :param table: list[list[int]]
    :returns: bool, True if there are such cells, otherwise False
    """
    for row in table:
        for cell in row:
            if cell < 0:
                return True

    return False


#### GRAPHICS AND INTERACTION GAME FUNCTIONS ####

HELP_TEXT = """
Welcome to Minesweeper Game!
The goal of the game is to uncover all cells that do not contain mines.
Flag cells to mark suspected mines. If you reveal a mine by mistake, 
the game is over!

--------------------------
     Commands Overview
--------------------------

- start or s [difficulty]
    Starts a new game with a preset difficulty.
    Difficulty Levels:
      easy   - 8x8 grid, 10 mines
      normal - 16x16 grid, 40 mines
      hard   - 24x24 grid, 99 mines
    Example: start easy

- start or s [rows] [cols] [mines]
    Starts a new game with custom grid dimensions and mine count.
    Example: start 10 10 20

- display or d
    Displays the current game field.
    Example: display

- flag or f [position]
    Flags a cell you suspect contains a mine.
    Example: flag B3 or f 3B or f 3 b

- hit or h or disclose or reveal or r [position]
    Reveals the cell at the specified position.
    Example: reveal B3 or h 3B or h 3 b

- end or e
    Ends the current game without determining win/loss.
    Example: end

- quit or q or exit
    Quits Minesweeper game entirely.
    Example: quit

- help or ?
    Displays this help menu.
    Example: help

--------------------------
   Position Format
--------------------------

Specify cell positions in one of the following formats:
   [letter][number]    Example: B3
   [number][letter]    Example: 3B
   [letter] [number]   Example: B 3
   [number] [letter]   Example: 3 B

   The letter represents the column, and the number represents the row.
   Also the game is case-insensitive, so 3b and 3B are treated as same.

--------------------------
   How to Play
--------------------------

1. OBJECTIVE:
   Uncover all cells that do not contain mines without revealing a mine. 
   The game ends if you reveal a mine.

2. REVEALING CELLS:
   Start the game by revealing a cell. If a cell has no adjacent mines,
   nearby cells will automatically reveal. If a cell displays a number,
   it indicates how many mines are adjacent to it. Use this info to deduce 
   safe cells.

3. FLAGGING MINES:
   Use the 'flag' command to mark cells where you suspect a mine. This 
   helps keep track of possible mine locations.

4. WINNING AND LOSING:
   WIN by revealing all non-mine cells.
   LOSE if you reveal a cell containing a mine.

5. ENDING AND EXITING:
   Use 'end' to abandon the current game.
   Use 'quit' to leave Minesweeper entirely.

Good luck!
""".strip()


def render_table(
    table: list[list[int]] | None = None,
    flags: list[tuple[int, int]] | None = None,
    view_mines: bool = False,
    width: int = 0,
    height: int = 0,
) -> str:
    """
    Render given table to the text.

    :param table: list[list[int]] | None: table or None if to render an empty table
    :param flags: list[tuple[int, int]] | None: positions of the flags on the table
    :param view_mines: bool, if True, views mines as "X"
    :param width: int, width of the empty table, used only when table is None
    :param height: int, height of the empty table, used only when table is None
    :returns: str, table in the text format
    """
    if table:
        height = len(table)
        width = len(table[0])
    if not flags:
        flags = []

    column_size = 2 if height >= 10 else 1
    lines = [" " * (column_size + 1) + " ".join(string.ascii_uppercase[:width])]
    for y in range(height):
        # line = ""
        line = [f"{y + 1: >{column_size}}"]
        for x in range(width):
            if table:
                cell = (
                    is_visible(table, (x, y)),
                    get_value(table, (x, y)),
                    (x, y) in flags,
                )
            else:
                cell = (x, y) in flags

            match cell:
                # If (mine) and (view_mines)
                case (False, None, _) if view_mines:
                    line.append("X")
                # If (no table and not flagged) or (not visible and not flagged)
                case False | (False, _, False):
                    line.append("?")
                # If (no table and flagged) or (not visible and flagged)
                case True | (False, _, True):
                    line.append("F")
                # If (visible and value is 0)
                case (True, 0, _):
                    line.append(" ")
                # If (visible)
                case (True, value, _):
                    line.append(str(value))
                case _:
                    raise ValueError(f"Unparsed cell occured: {cell}")

        lines.append(" ".join(line))

    return "\n".join(lines)


def read_command() -> str:
    """
    Command read helper. Returns lowered string inputted by the player.

    :returns: str, command read
    """
    return input(">>> ").lower()


def parse_position(argument: list[str]) -> tuple[int, int] | None:
    """
    Parse position, where row is represented by an integer and column
    as a latin letter. If it is invalid, prints message about this to
    stdout and returns None.

    :param argument: list[str], two or one strings, that has integer and
    latin letter
    :returns: tuple[int, int] | None, parsed position or None if string
    format is invalid
    """
    if not 0 < len(argument) < 3:
        print(
            "You have to specify column as a latin letter and row"
            "as an integer after this command"
        )
        return None

    if len(argument) == 2:
        argument = argument[0] + argument[1]
    else:
        argument = argument[0]

    if argument[0] in string.ascii_lowercase:
        row = argument[1:]
        col = argument[0]
    else:
        row = argument[:-1]
        col = argument[-1]

    try:
        row = int(row) - 1
        col = string.ascii_lowercase.index(col)
    except ValueError:
        print(
            "You have to specify column as a latin letter and row"
            "as an integer after this command"
        )
        return None

    return (col, row)


def print_table(
    game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    view_mines: bool = False,
):
    """
    Print current game's table to stdout.

    :param game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    current game data
    :param view_mines: bool, if True, views mines as "X"
    """
    if not game:
        return

    print()
    print(render_table(game[0], game[4], view_mines, game[1], game[2]))


def command_start(
    width: int | str,
    height: int | str,
    mines_number: int | str,
    game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
) -> tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None:
    """
    Command: start new game.

    :param width: int | str, table width, automaticall converts str to int
    :param height: int | str, table height, automaticall converts str to int
    :param mines_number: int | str, mines number, automaticall converts str to int
    :param game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    old game data
    :returns: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    new game data if updated, otherwise returns same as inptuted
    """
    try:
        width = int(width)
        height = int(height)
        mines_number = int(mines_number)
    except ValueError:
        print("Width, height and number of mines must be all integers.")
        return game

    if not (4 <= width <= 26 and 4 <= height <= 26):
        print("Width and height have to be between 4 and 26")
        return game

    if not 1 <= mines_number <= (width * height - 9):
        print(f"Mines number has to be between 1 and {width*height - 9}")
        return game

    game = (None, width, height, mines_number, [])

    print(f"Game started. There are {mines_number} mines.")
    print("Good luck!")
    print_table(game)
    return game


def command_flag(
    argument: list[str],
    game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
) -> tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None:
    """
    Command: flag or unflag cell.

    :param argument: list[str], two or one strings, that has integer and
    latin letter
    :param argument: list[str],
    :param game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    old game data
    :returns: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    new game data if updated, otherwise returns same as inptuted
    """
    if not game:
        print("Game is not started.")
        return game

    position = parse_position(argument)
    if not position:
        return game

    # Check for boundaries
    if (
        position[1] < 0
        or position[1] >= game[1]
        or position[0] < 0
        or position[0] >= game[2]
    ):
        print("Position is already visible or is out of range.")
        return game

    if is_visible(game[0], position):
        print("Position is already visible or is out of range.")
        return game

    if position in game[4]:
        game[4].remove(position)
    else:
        game[4].append(position)
    print_table(game)
    return game


def command_hit(
    argument: list[str],
    game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
) -> tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None:
    """
    Command: hit cell.

    :param argument: list[str], two or one strings, that has integer and
    latin letter
    :param game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    old game data
    :returns: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    new game data if updated, otherwise returns same as inptuted
    """
    if not game:
        print("Game is not started.")
        return game

    position = parse_position(argument)
    if not position:
        return game

    if not game[0]:
        game = (create_table(game[1], game[2], game[3], position),) + game[1:]

    outcome = disclose(game[0], position)
    match outcome:
        case None:
            print("Position is already visible or is out of range.")
        case False:
            print("Unfortunately, you hit a mine.")
            disclose_whole(game[0])
            print_table(game, True)
            game = None
        case True if is_game_active(game[0]):
            print_table(game)
        case True:
            print("Congratulations! You won, good job!")
            print_table(game, True)
            game = None

    return game


def parse_command(
    command: str,
    game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
) -> tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None:
    """
    Parse command inputted by the player.

    :param command: str, player-inputted command
    :param game: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    old game data
    :returns: tuple[list[list[int]] | None, int, int, int, list[tuple[int, int]]] | None,
    new game data if updated, otherwise returns same as inptuted
    """
    match command.split():
        case ["start", "hard"] | ["s", "hard"]:
            game = command_start(24, 24, 99, game)
        case ["start", "normal"] | ["s", "normal"]:
            game = command_start(16, 16, 40, game)
        case ["start", "easy"] | ["s", "easy"]:
            game = command_start(8, 8, 10, game)
        case ["start", width, height, mines_number] | [
            "s",
            width,
            height,
            mines_number,
        ]:
            game = command_start(width, height, mines_number, game)
        case ["flag", *argument] | ["f", *argument]:
            game = command_flag(argument, game)
        case ["end"] | ["e"]:
            if not game:
                print("Game is not started.")
                return game

            disclose_whole(game[0])
            print_table(game, True)
            game = None
        case ["display"] | ["d"]:
            if not game:
                print("Game is not started.")
                return game

            print_table(game)
        case ["help"] | ["?"]:
            print(HELP_TEXT)
        case []:
            pass
        case (
            ["hit", *argument]
            | ["h", *argument]
            | ["disclose", *argument]
            | ["reveal", *argument]
            | ["r", *argument]
        ):
            game = command_hit(argument, game)
        case _:
            print("Invalid command or arguments, please, type help for instructions.")

    return game


def main():
    """
    Main code of the game
    """
    print("Welcome to Minesweeper game!")
    print("Type help or ? for help menu and instructions.")

    # Variable that holds all game parameters
    game = None

    for command in iter(read_command, "quit"):
        # Aliases for quit
        if command in ["q", "exit"]:
            break

        game = parse_command(command, game)

    print("Thank you for playing. Goodbye!")


if __name__ == "__main__":
    main()
