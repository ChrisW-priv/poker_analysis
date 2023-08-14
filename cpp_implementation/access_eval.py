import ctypes
from pathlib import Path

# Get the current directory of the script
current_dir = Path(__file__).resolve().parent
file_path = current_dir / 'build/libpokerlib.so' 
poker_lib = ctypes.CDLL(file_path)

# Define the argument types for the function
poker_lib.evaluate7cards.argtypes = [
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int)
]


def evaluate7cards(sorted_cards: bytearray):
    # Create variables to hold the result values
    result1 = ctypes.c_int()
    result2 = ctypes.c_int()
    sorted_cards_array = (ctypes.c_uint8 * len(sorted_cards))(*sorted_cards)

    # Call the C++ function
    poker_lib.evaluate7cards(sorted_cards_array, ctypes.byref(result1), ctypes.byref(result2))
    modified_result1 = result1.value
    modified_result2 = result2.value

    return modified_result1, modified_result2

