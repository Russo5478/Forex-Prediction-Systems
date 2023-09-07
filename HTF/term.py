from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
import re
import traceback

autocomplete_words = ["--help", "--exit", "--positions", "--user"]
word_completer = WordCompleter(autocomplete_words)

class MainClass:
    def __init__(self) -> None:
        self.first_run = False
        self.menu = '''
                    =============== FX Correlation Menu ===============
                    [1] Help commands {-h, --help}
                    [2] See open positions {-p, --positions}
                    [3] Create new position {-c, --create}\n'''
        self.main_tag = "?$> "
        self.keyword_functions = {
            "--user": lambda args: self.handle_user_command(args),
            "--positions": lambda args=None: print("All positions here"),
            "--exit": lambda args=None: self.safe_exit(),
            "--help": lambda args=None: print(self.menu),

            "-h": lambda args=None: print(self.menu),
            "-e": lambda args=None: self.safe_exit(),
            "-p": lambda args=None: print("All positions here"),
        }
        self.history = FileHistory('command_history.txt')

        self.main_function()

    def handle_user_command(self, args):
        # Check if the command starts with '--user'
        if not args.startswith("username=") or not "password=" in args or not "id=" in args:
            print(args)
            print("Invalid --user command format. Use: --user username=user1, password=pass1, id=98855")
            return

        # Parse the username, password, and id from the args string
        user_info = self.parse_user_args(args)
        if user_info:
            print(f"Username: {user_info['username']}")
            print(f"Password: {user_info['password']}")
            print(f"ID: {user_info['id']}")
        else:
            print(args)
            print("Invalid --user command format. Use: --user username=user1, password=pass1, id=98855")

    def parse_user_args(self, args):
        # Use regular expressions to extract username, password, and id from the args string
        pattern = r"username=([\w\d]+),\s*password=([\w\d]+),\s*id=(\d+)"
        match = re.match(pattern, args)
        if match:
            return {
                "username": match.group(1),
                "password": match.group(2),
                "id": match.group(3)
            }
        else:
            return None

    def handle_main_input(self, main_input):
        words = main_input.split()

        i = 0
        while i < len(words):
            keyword = words[i]
            if keyword in self.keyword_functions:
                keyword_function = self.keyword_functions[keyword]
                if i + 1 < len(words):
                    argument = words[i + 1]
                    keyword_function(argument)
                    i += 2
                else:
                    keyword_function()
                    i += 1
            else:
                i += 1

    def safe_exit(self):
        exit()

    def main_function(self):
        while True:
            try:
                if not self.first_run:
                    self.first_run = True
                    user_input = prompt(self.menu + self.main_tag, completer=word_completer, history=self.history)
                    self.handle_main_input(user_input)

                else:
                    user_input = prompt(self.main_tag, completer=word_completer, history=self.history)
                    self.handle_main_input(user_input)

            except KeyboardInterrupt:
                self.safe_exit()
                break

            except Exception as console_error:
                traceback.print_exc()
                print(f"{console_error}")
                input("Press Enter to exit!")
                self.safe_exit()
                break


if __name__ == '__main__':
    MainClass()
