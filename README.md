# Minesweeper Game

### Introduction
This is a text-based implementation of the classic Minesweeper game. The game generates a minefield where players uncover cells to find safe spaces while avoiding mines. Players can also flag suspected mines to help them further.

### Features

- Customizable grid size and mine count.
- Command-line interface for user interaction.
- Auto-revealing of empty cells.
- Flagging system for suspected mines.
- Win condition when all non-mine cells are revealed.

### How to Play

The following commands can be used in the game:

`start [difficulty]` or `s [difficulty]`

Starts a new game with preset difficulty levels:

- easy (8x8, 10 mines)

- normal (16x16, 40 mines)

- hard (24x24, 99 mines)

Example: `start easy`

`start [rows] [cols] [mines]` or `s [rows] [cols] [mines]`

Starts a game with custom dimensions.

Example: `start 10 10 20`

`display` or `d`

Shows the current game field.

`flag [position]` or `f [position]`

Flags or unflags a suspected mine.

Example: `flag B3`

`reveal [position]` or `r [position]`

Reveals the specified cell.

Example: `reveal C4`

`end` or `e`

Ends the current game.

`quit` or `q`

Exits the Minesweeper game.

`help` or `?`

Displays the help menu.

#### Position Formatting

Positions can be entered in different formats:

`[Letter][Number]` (e.g., `B3`)

`[Number][Letter]` (e.g., `3B`)

`[Letter] [Number]` (e.g., `B 3`)

`[Number] [Letter]` (e.g., `3 B`)

The letter represents the column, and the number represents the row.

Input is case-insensitive (b3 and B3 are equivalent).

### Running the script

First of all, you need to install Python 3.x. After that you can run the script with following command:

```bash
python minesweeper.py
```
