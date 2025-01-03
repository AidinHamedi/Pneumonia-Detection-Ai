import re


def print_Color_V2(Input: str, print_END: str = "\n", start_char: str = "<", end_char: str = ">"):
    """
    Prints colored text to the console using advanced terminal colors.

    Args:
        Input (str): The input string to be printed. '<color>' is used to specify the color of the following text.
        print_END (str): The string appended after the final output. Default is '\\n'.
        start_char (str): The character used as the start of the color specifier. Default is '<'.
        end_char (str): The character used as the end of the color specifier. Default is '>'.

    Examples:
    ~~~python
        print_Color('Hello, World!')
        # Prints 'Hello, World!' in normal color.

        print_Color('<red>Hello in red<green> Hello in green')
        # Prints 'Hello in red' in red and 'Hello in green' in green.

        print_Color('~red!Hello in red', start_char='~', end_char='!')
        # Prints 'Hello, World!' in normal color.

    Note:
        If an invalid color is provided, an error message will be printed.
    """
    color_code = {
        "black": "\x1b[0;30m",
        "red": "\x1b[0;31m",
        "green": "\x1b[0;32m",
        "yellow": "\x1b[0;33m",
        "blue": "\x1b[0;34m",
        "magenta": "\x1b[0;35m",
        "cyan": "\x1b[0;36m",
        "white": "\x1b[0;37m",
        "normal": "\x1b[0m",
        "bg_black": "\x1b[40m",
        "bg_red": "\x1b[41m",
        "bg_green": "\x1b[42m",
        "bg_yellow": "\x1b[43m",
        "bg_blue": "\x1b[44m",
        "bg_magenta": "\x1b[45m",
        "bg_cyan": "\x1b[46m",
        "bg_white": "\x1b[47m",
        "bg_normal": "\x1b[49m",
        "light_gray": "\x1b[0;90m",
        "light_red": "\x1b[0;91m",
        "light_green": "\x1b[0;92m",
        "light_yellow": "\x1b[0;93m",
        "light_blue": "\x1b[0;94m",
        "light_magenta": "\x1b[0;95m",
        "light_cyan": "\x1b[0;96m",
        "light_white": "\x1b[0;97m",
        "bg_light_gray": "\x1b[0;100m",
        "bg_light_red": "\x1b[0;101m",
        "bg_light_green": "\x1b[0;102m",
        "bg_light_yellow": "\x1b[0;103m",
        "bg_light_blue": "\x1b[0;104m",
        "bg_light_magenta": "\x1b[0;105m",
        "bg_light_cyan": "\x1b[0;106m",
        "bg_light_white": "\x1b[0;107m",
    }
    pattern = re.escape(start_char) + r"([^" + re.escape(end_char) + r"]*)" + re.escape(end_char)
    substrings = re.split(pattern, Input)
    current_color = "normal"
    for i, sub_str in enumerate(substrings):
        if i % 2 == 0:
            print(color_code[current_color] + sub_str + color_code["normal"], end="")
            current_color = "normal"
        else:
            color = sub_str.strip()
            if color in color_code:
                current_color = color
            else:
                print(f"\n[print_Color] ERROR: Invalid color!!! The input color: '{color}'")
    print("", end=print_END)
