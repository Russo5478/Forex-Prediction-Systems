# Get user input
user_input = input("Enter a command: ")

# Split the input string into words
words = user_input.split()

# Define a dictionary to map keywords to their corresponding functions
keyword_functions = {
    "--user": lambda args: print(f"User argument: {args}"),
    "--pass": lambda args: print(f"Password argument: {args}"),
    "--role": lambda args: print(f"Role argument: {args}"),
    "--help": lambda args=None: print("Help command executed" if args is None else f"Help argument: {args}"),  # Handle the "help" command here
    # Add more keywords and corresponding functions as needed
}

# Initialize a list to store the executed commands
executed_commands = []

# Iterate through the words to find and execute keyword functions
i = 0
while i < len(words):
    keyword = words[i]
    if keyword in keyword_functions:
        keyword_function = keyword_functions[keyword]
        if i + 1 < len(words):
            argument = words[i + 1]
            keyword_function(argument)
            executed_commands.append((keyword, argument))
            i += 2
        else:
            # No argument provided; call the keyword function without an argument
            keyword_function()
            executed_commands.append((keyword, None))
            i += 1
    else:
        i += 1

# Check if any commands were executed
if executed_commands:
    print("Executed Commands:")
    for keyword, argument in executed_commands:
        print(f"Keyword: {keyword}, Argument: {argument}")
else:
    print("No valid keywords found in the input.")
