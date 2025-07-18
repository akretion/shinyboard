from .Colors import WHITE, CYAN, RED, GREEN, YELLOW


def log(tag: str, message: str):
    match tag:
        case "INFO":
            print(f"{CYAN}INFO{WHITE}: {message}")
        case "WARN":
            print(f"{YELLOW}INFO{WHITE}: {message}")
        case "ERROR":
            print(f"{RED}INFO{WHITE}: {message}")
        case _:
            print(f"{GREEN}{tag}{WHITE}: {message}")
