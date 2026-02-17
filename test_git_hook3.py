# This is a test file to verify git hook functionality

def bad_function_name():
    x=1  # Missing space around operator
    return x

class bad_class_name:
    def __init__(self):
        self.variable = 1

# Missing docstring

# Line too long: this line is intentionally very long to test the line length check in the git hook
long_line = "This is a very long line that exceeds the recommended line length limit of 79 characters"

# Using tab instead of spaces for indentation
	def another_bad_function():
		return True

CONSTANT = 10
