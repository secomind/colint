class TextModifiers:
    OK = 92  # Bright green
    WARNING = 93  # Bright Yellow
    ERROR = 91  # Bright Red

    BOLD = 1
    UNDERLINE = 4
    STRIKETHROUGH = 9
    INVERSE = 44  # swap background & text color


def format_text(text: str, codes: int | list[int]) -> str:
    """
    Returns a formatted version of the input text. Automatically includes an end formatting character
    at the end of the string.

    Parameters:
    text (str): The text to be formatted
    codes (int | list[int]): formatting codes to be used in the text.
                             Refer to TextModifiers for the useful codes.
                             if a list is passed all modifiers are applied

    Returns:
    formatted_text: the formatted text
    """
    if isinstance(codes, int):
        codes = [codes]
    all_codes = ";".join(map(str, codes))
    return f"\033[{all_codes}m{text}\033[0m"
