import argparse
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime
import re

def tuple_to_readable_cell( row, column ):
    return "ABCDEFGH"[ column ] + str(row+1)

def readable_cell_to_tuple( cell ):
    row    = int( cell[1] ) - 1
    column = ord( cell[0].lower() ) - 97
    return ( row, column )

class Board:

    @classmethod
    def get_starting_board( cls ):
        start_board = [ [" "]*8 for i in range(8) ]
        start_board[3][3] = start_board[4][4] = "W"
        start_board[3][4] = start_board[4][3] = "B"
        return cls( start_board )

    @classmethod
    def load_board( cls, string ):
        empty_board = [ [" "]*8 for i in range(8) ]
        return cls([
            *[ list(line.strip("\n").ljust(8)[:8]) for line in string.split("\n") ],
            *empty_board
        ][:8])

    def __init__( self, rows ):
        self.rows = rows
    def __iter__( self ):
        return iter(self.rows)
    def __repr__( self ):
        return "\n".join([ "".join( row ) for row in self ])

    def get_cell( self, row, column ):
        try:
            cell = self.rows[ row ][ column ]
            return None if cell == " " else cell
        except IndexError:
            return None

    def set_cell( self, row, column, color ):
        if color not in "WB":
            raise ValueError( "Board cell colour must be one of 'W' or 'B'" )
        self.rows[ row ][ column ] = color

    """ Returns {boolean} whether the move was successful. """
    def make_move( self, row, column, color ):

        if color not in "WB":
            raise ValueError( "Board cell colour must be one of 'W' or 'B'" )

        # Check if the cell is free
        if self.get_cell( row, column ):
            print( f"Cell {tuple_to_readable_cell(row, column)} is already occupied." )
            return False

        # Check if the move is legal: is it next to an occupied cell?
        deltas = [ -1, 0, 1 ]
        directions = sum([ [ (i,j) for i in deltas if i or j ] for j in deltas ], [])
        for i, j in directions:
            if self.get_cell( row + i, column + j ):
                break
        else:
            print( f"Cell {tuple_to_readable_cell(row, column)} is not adjacent to any existing occupied cell." )
            return False

        # Check if the move is legal: does it make any captures?
        captures = []
        for i, j in directions:
            check_position = ( row, column )
            current_cell   = color
            captured_cells = []

            while True:
                check_position = ( check_position[0] + i, check_position[1] + j )
                current_cell = self.get_cell( *check_position )
                if current_cell == color or not current_cell:
                    break
                captured_cells.append( check_position )

            if current_cell == color:
                captures.extend( captured_cells )

        if not len(captures):
            print( f"Move at cell {tuple_to_readable_cell(row, column)} does not capture any cells." )
            return False

        # If the move is legal, do it
        self.set_cell( row, column, color )
        for cell in captures:
            self.set_cell( *cell, color )
        return True

def get_savegame_path ( filename ):
    return f"games/{filename}.oth"

def check_file_exists ( filename ):
    return Path( get_savegame_path( filename )).is_file()

def load_game ( filename ):
    with open( get_savegame_path( filename ), "r" ) as file:
        return Board.load_board( file.read() )

def save_game ( filename, board ):
    with open( get_savegame_path( filename ), "w" ) as file:
        file.write( str( board ))

def new_game ( filename ):
    save_game( filename, Board.get_starting_board() )

def make_move ( filename, color, position ):
    board = load_game( filename )
    move_successful = board.make_move( *position, color.upper() )
    return move_successful, board

def draw_game ( filename ):
    light_green  = ( 60,  163, 0   )
    dark_green   = ( 53,  130, 8   )
    black        = ( 0,   0,   0   )
    white        = ( 255, 255, 255 )
    image_height = 512

    square_height = image_height / 8
    coin_colors   = {
        "W": white,
        "B": black
    }

    board = load_game( filename )
    image = Image.new( "RGB", ( image_height, image_height ), color=light_green )
    draw  = ImageDraw.Draw( image )

    for row_index, row in enumerate( board ):

        for column_index, cell in enumerate( row ):

            if row_index % 2 != column_index % 2:
                draw.rectangle(
                    [
                        ( column_index*square_height,     row_index*square_height     ),
                        ( (column_index+1)*square_height, (row_index+1)*square_height )
                    ],
                    fill=dark_green
                )

            if row_index == len(board.rows) - 1:
                draw.text(
                    ( (column_index+0.8)*square_height, (row_index+0.8)*square_height ),
                    text=tuple_to_readable_cell( row_index, column_index )[0],
                    fill=white
                )

            if column_index == 0:
                draw.text(
                    ( (column_index+0.1)*square_height, (row_index+0.1)*square_height ),
                    text=tuple_to_readable_cell( row_index, column_index )[1],
                    fill=white
                )

            if cell not in [ "W", "B" ]:
                continue
            color = coin_colors[ cell ]
            draw.ellipse(
                [
                    ( (column_index+0.1)*square_height, (row_index+0.1)*square_height ),
                    ( (column_index+0.9)*square_height, (row_index+0.9)*square_height )
                ],
                fill=color
            )

    Path( f"output/{filename}" ).mkdir( exist_ok=True )
    image.save( f"output/{filename}/{filename}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png" )

parser     = argparse.ArgumentParser()
subparsers = parser.add_subparsers( dest="subcommand" )

draw_parser = subparsers.add_parser( "draw", help="Draw the specified game." )
draw_parser.add_argument( "filename", help="The name of the file (without extension) in the 'games' directory to draw." )

new_parser = subparsers.add_parser( "new", help="Create a new game with the given filename." )
new_parser.add_argument( "filename", help="The name of the file (without extension) to create." )
new_parser.add_argument( "-f", "--force",  help="Create the game even if it overwrites an existing one.", action="store_true" )

move_parser = subparsers.add_parser( "move", help="Make a move on the specified game." )
move_parser.add_argument( "filename", help="The name of the file (without extension) in the 'games' directory to which to apply the move." )

valid_colors = [ "w", "b", "white", "black" ]
def is_valid_color ( value ):
    if value.lower() not in valid_colors:
        message = f"Expected one of: {', '.join( valid_colors )}"
        print(message)
        raise ValueError( message )
    return value.lower()[0]

valid_position = re.compile( "^[a-h][1-8]$", re.IGNORECASE )
def is_valid_position ( value ):
    if not re.match( valid_position, value ):
        message = f"Expected value to match regex '{valid_position.pattern}'"
        print( message )
        raise ValueError( message )
    return readable_cell_to_tuple( value )

move_parser.add_argument(
    "color",
    help="The colour of the player making the move, either 'w' or 'b'.",
    type=is_valid_color
)
move_parser.add_argument(
    "position",
    help="The position on the game board to make the move, in the form '<column_letter><row_number>', e.g. A1.",
    type=is_valid_position
)

def main ():

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        return

    # This is the only command which can operate without the existence of a file
    if args.subcommand == "new":
        if args.force or not check_file_exists( args.filename ):
            new_game( args.filename )
            draw_game( args.filename )
        else:
            print( f"File '{get_savegame_path( args.filename )}' already exists" )

    # No command after this point can accept a filename which doesn't exist
    elif not check_file_exists( args.filename ):
        print( f"File '{get_savegame_path( args.filename )}' does not exist" )

    elif args.subcommand == "draw":
        draw_game( args.filename )

    elif args.subcommand == "move":
        move_successful, board = make_move( args.filename, args.color, args.position )
        if move_successful:
            save_game( args.filename, board )
            draw_game( args.filename )

if __name__ == "__main__":
    main()