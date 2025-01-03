# the print_Color func
def print_Color(
    Input: str,
    colors: list,
    print_END: str = "\n",
    advanced_mode: bool = False,
    return_str: bool = False,
):
    """
    Prints colored text to the console using advanced terminal colors.

    Args:
        Input (str): The input string to be printed. In advanced mode, '~*' is used to separate different parts of the string to be printed in different colors.
        colors (list): A list of colors for the text. In non-advanced mode, only the first color in the list is used. In advanced mode, each color corresponds to a part of the input string separated by '~*'.
        print_END (str): The string appended after the final output. Default is '\\n'.
        advanced_mode (bool): If True, enables advanced mode that allows multiple colors in one string. Default is False.
        return_str (bool): If True, returns the colored string instead of printing it. Default is False.
    Examples:
    ~~~python
        print_Color('Hello, World!', ['green'])
        # Prints 'Hello, World!' in green.

        print_Color('~*Hello in green~*Hello in red', ['green', 'red'], advanced_mode=True)
        # Prints 'Hello in green' in green and 'Hello in red' in red.

    Note:
        The advanced terminal colors can be used by providing the escape sequences directly in the colors list.
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
        "bold": "\x1b[1m",
        "underline": "\x1b[4m",
        "blink": "\x1b[5m",
    }
    return_temp = ""
    if not advanced_mode:
        if colors[0] in color_code:
            if return_str:
                return color_code[colors[0]] + Input + "\x1b[0m"
            print(color_code[colors[0]] + Input + "\x1b[0m", end=print_END)
        else:
            print("[print_Color] ERROR: Invalid color input!!!")
    else:
        substrings = Input.split("~*")
        if len(substrings) != len(colors) + 1:
            print("[print_Color] ERROR: Number of colors and number of '~*' don't match!!!")
        else:
            for sub_str, color in zip(substrings, ["normal"] + colors):
                if color in color_code:
                    if return_str:
                        return_temp += color_code[color] + sub_str + "\x1b[0m"
                    else:
                        print(color_code[color] + sub_str + "\x1b[0m", end="")
                else:
                    print(f"\n[print_Color] ERROR: Invalid color!!! The input color: '{color}' input list index: {colors.index(color)}")
            print("", end=print_END)
            if return_str:
                return return_temp


# the func end
