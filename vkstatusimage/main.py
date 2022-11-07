from oauth import Storage, generate_auth_link, parse_token
from api import get_status, set_status, get_statuses_list, TokenError


class color:
    clear = "\033[0m"
    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"


APPS = ["7362610", "7539087"]

LOGO = rf"""{color.cyan}__   ___  _____ _        _           ___                     
\ \ / / |/ / __| |_ __ _| |_ _  _ __|_ _|_ __  __ _ __ _ ___ 
 \ V /| ' <\__ \  _/ _` |  _| || (_-<| || '  \/ _` / _` / -_)
  \_/ |_|\_\___/\__\__,_|\__|\_,_/__/___|_|_|_\__,_\__, \___|
                                                   |___/     {color.clear}"""
HELP = """commands:
 - app {id}   | select app 
 - set {id}   | set status image by id
 - get        | get current status image id
 - new        | generate token for app
 - list       | preview status image ids for app
 - reset      | reset status image
 - help       | display help
 - exit       | exit from app

apps:
 - 1          | Коронавирус (7362610)
 - 2          | Шаги ВКонтакте (7539087)
"""


def new_token(app_id) -> None:
    global token

    print("Please authorize and paste url/token.")
    print(generate_auth_link(app_id))
    token = parse_token(input("url/token: "))
    storage.update_token(app_id, token)


def print_current_status():
    global token
    status = get_status(token)
    print(f"{status['id']}: {status['name']}")


def change_token():
    global token, storage
    if (token := storage.get_token(current_app)) == "":
        print(f"{color.red}Current token invalid!{color.clear}")
        new_token(current_app)


def process_command() -> None:
    """Take input and parse it."""
    global current_app, token, storage
    command = input(f"{color.cyan}{current_app}>{color.clear} ").split()
    command_len = len(command)

    # if no command skip
    if command_len <= 0:
        return
    # check if args are valid
    elif command[0] in ("app", "set"):
        if command_len == 2 and command[1].isdecimal():
            pass
        else:
            print(f"{color.red}!!! Invalid args !!!{color.clear}")
            return
    elif command_len != 1:
        print(f"{color.red}!!! Invalid args !!!{color.clear}")
        return

    try:
        match command[0]:
            case "app":
                new_app = command[1]                
                # small id
                if int(new_app) - 1 in range(len(APPS)):
                    current_app = APPS[int(new_app) - 1]
                # full app id
                elif len(new_app) == 7:
                    current_app = new_app
                    if new_app not in APPS:
                        print(
                            f"{color.yellow}WARNING: App may not be supported!{color.clear}"
                        )
                else:
                    print(f"{color.red}ERROR: Not supported app id.{color.clear}")
                    return
                print(f"Current app: {current_app}")
                change_token()

            case "set":
                set_status(token, command[1])
                print_current_status()

            case "get":
                print_current_status()

            case "new":
                new_token(current_app)

            case "list":
                for status in get_statuses_list(token):
                    print(f"{status['id']}: {status['name']}")

            case "reset":
                set_status(std_token := storage.get_token("7362610"), 1)
                set_status(std_token, 1)
                print("Status has reset.")

            case "help":
                print(HELP)
                return

            case "exit":
                exit()

            case _:
                print(
                    f"{color.red}!!! Invalid command !!!{color.clear}\nUse 'help' command."
                )
    except TokenError as e:
        print(
            f"{color.red}ERROR: {e.message}{color.clear}\nPlease generate new token with 'new'."
        )


if __name__ == "__main__":
    try:
        current_app = "7362610"
        print(LOGO)
        print(HELP)
        storage = Storage()
        change_token()

        while True:
            process_command()
    except KeyboardInterrupt:
        exit()