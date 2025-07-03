import math
import re

class Calculator:
    """
    A calculator class that handles mathematical expressions with variables, functions,
    and constants. Supports evaluation with error checking and variable assignment.
    """

    def __init__(self):
        """
        Initialize calculator environment with:
        - Predefined mathematical functions
        - Constants
        - Storage for user variables
        """
        self.variables = {}
        self.env = {
            # Trigonometric functions
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'cot': lambda x: 1 / math.tan(x),

            # Roots and logarithms
            'sqrt': math.sqrt,
            'log': math.log,  # log(x, base) or log(x) (natural)
            'ln': math.log,  # Natural logarithm alias
            'log10': math.log10,
            'log2': math.log2,

            # Constants
            'pi': math.pi,
            'e': math.e,

            # User variables
            **self.variables
        }

    def _is_assignment(self, expression):
        """
        Check if expression contains an assignment operation (=)
        but not comparison operators (==, !=, <=, >=).

        Args:
            expression (str): Input expression to check

        Returns:
            bool: True if valid assignment, False otherwise
        """
        return '=' in expression and not re.search(r'==|!=|<=|>=', expression)

    def _validate_variable_name(self, name):
        """
        Validate variable name syntax (must be valid Python identifier).

        Args:
            name (str): Variable name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None

    def _parse_assignment(self, expression):
        """
        Split assignment expression into variable name and value expression.

        Args:
            expression (str): Assignment expression (e.g. "x = 5")

        Returns:
            tuple: (variable_name, value_expression)

        Raises:
            ValueError: If variable name is invalid
        """
        var_name, expr = map(str.strip, expression.split('=', 1))
        if not self._validate_variable_name(var_name):
            raise ValueError(f"Invalid variable name: {var_name}")
        return var_name, expr

    def safe_eval(self, expression):
        """
        Evaluate mathematical expression or handle variable assignment.

        Args:
            expression (str): Expression to evaluate

        Returns:
            float/str: Result of evaluation or assignment confirmation message
                      Returns error messages as strings
        """
        if self._is_assignment(expression):
            var_name, expr = self._parse_assignment(expression)
            result = self._evaluate_expression(expr)
            self.variables[var_name] = result
            self.env[var_name] = result
            return f"Variable {var_name} = {result}"
        return self._evaluate_expression(expression)

    def _evaluate_expression(self, expression):
        """
        Safely evaluate mathematical expression with error handling.

        Steps:
            1. Normalize expression (replace ^ with **, remove spaces)
            2. Validate allowed characters
            3. Check balanced parentheses
            4. Evaluate in restricted environment

        Args:
            expression (str): Expression to evaluate

        Returns:
            float/str: Result or error message

        Raises:
            ValueError: For invalid characters or unbalanced parentheses
        """
        expression = expression.replace('^', '**').replace(' ', '')

        if not re.match(r'^[\w+\-*/().^=,]+$', expression):
            raise ValueError("Invalid characters in the expression")

        if expression.count('(') != expression.count(')'):
            raise ValueError("Unbalanced brackets")

        try:
            return eval(expression, {'__builtins__': None}, self.env)
        except ZeroDivisionError:
            return "Error: division by zero"
        except NameError as e:
            return f"Error: Unknown variable or function {str(e).split()[-1]}"
        except TypeError:
            return "Error: Incorrect number of arguments"
        except Exception as e:
            logger.error(f'Error in "_evaluate_expression", with error - {e}')