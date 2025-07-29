from .colors import WHITE, CYAN, RED, GREEN, YELLOW, MAGENTA


def log(tag: str, message: str):
    match tag:
        case "INPUT":
            print(f"{MAGENTA}INPUT{WHITE}: {message}")
        case "INFO":
            print(f"{CYAN}INFO{WHITE}: {message}")
        case "WARN":
            print(f"{YELLOW}WARN{WHITE}: {message}")
        case "ERROR":
            print(f"{RED}ERROR{WHITE}: {message}")
        case _:
            print(f"{GREEN}{tag}{WHITE}: {message}")
