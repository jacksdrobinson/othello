# Othello

## Introduction

This is a simple implementation of the game Othello, which provides a command line utility for creating, playing and
rendering games of Othello.

It enforces placement rules, but does not enforce which player's turn it is, nor does it maintain a history of the
past states of the game.

## Installation

You will need Python 3.4+ and [Pillow](https://pypi.org/project/Pillow/) to run this script.

Pillow and PIL (Python Imaging Library) cannot co-exist, so you may need to uninstall PIL if you've installed it
before. To install Pillow, run:

```
pip install Pillow
```

## CLI Reference

```
usage: main.py [-h] {draw,new,move} ...

positional arguments:
  {draw,new,move}
    draw           Draw the specified game.
    new            Create a new game with the given filename.
    move           Make a move on the specified game.

optional arguments:
  -h, --help       show this help message and exit
```

### Draw

```
usage: main.py draw [-h] filename

positional arguments:
  filename    The name of the file (without extension) in the 'games'
              directory to draw.

optional arguments:
  -h, --help  show this help message and exit
```

### New

```
usage: main.py new [-h] [-f] filename

positional arguments:
  filename     The name of the file (without extension) to create.

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  Create the game even if it overwrites an existing one.
```

### Move

```
usage: main.py move [-h] filename color position

positional arguments:
  filename    The name of the file (without extension) in the 'games'
              directory to which to apply the move.
  color       The colour of the player making the move, either 'w' or 'b'.
  position    The position on the game board to make the move, in the form
              '<column_letter><row_number>', e.g. A1.

optional arguments:
  -h, --help  show this help message and exit
```