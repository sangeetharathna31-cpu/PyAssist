"""PyAssist Knowledge Base.
Contains structured data for Python programming concepts, beginner explanations,
code examples, expected outputs, and keyword dictionaries.
"""
from typing import Dict, Any, List

TOPICS: Dict[str, Dict[str, Any]] = {
    "python_intro": {
        "id": "python_intro",
        "title": "What is Python & Introduction",
        "keywords": [
            "what is python", "intro to python", "introduction", "why python",
            "interpreted", "high level", "general purpose", "guido van rossum",
            "python syntax", "indentation", "benefits of python", "python overview"
        ],
        "short_explanation": "Python is a high-level, interpreted, dynamically typed programming language known for readable and clean syntax.",
        "detailed_explanation": (
            "Python was created by Guido van Rossum and released in 1991. It emphasizes code readability with its notable "
            "use of significant whitespace (indentation) instead of curly braces. Python supports multiple programming "
            "paradigms, including procedural, object-oriented, and functional programming.\n\n"
            "Key characteristics:\n"
            "• High-level: Abstracts low-level memory management.\n"
            "• Interpreted: Executes instructions directly line-by-line via the Python Virtual Machine (PVM).\n"
            "• Dynamically Typed: Variable types are determined at runtime.\n"
            "• Batteries Included: Massive standard library covering web development, data science, file I/O, and more."
        ),
        "code_example": (
            "# A simple greeting and basic calculation in Python\n"
            "user_name = \"Coder\"\n"
            "print(f\"Hello, {user_name}! Welcome to Python.\")\n\n"
            "numbers = [1, 2, 3, 4, 5]\n"
            "print(f\"Sum of numbers: {sum(numbers)}\")"
        ),
        "expected_output": (
            "Hello, Coder! Welcome to Python.\n"
            "Sum of numbers: 15"
        ),
        "related_topics": ["variables_types", "operators", "functions_params", "control_flow_if"]
    },

    "variables_types": {
        "id": "variables_types",
        "title": "Variables and Data Types",
        "keywords": [
            "variables", "data types", "int", "float", "string", "bool", "boolean",
            "dynamic typing", "variable declaration", "type checking", "type()",
            "integer", "floating point", "str"
        ],
        "short_explanation": "Variables store data values in memory without requiring explicit type declaration in Python.",
        "detailed_explanation": (
            "In Python, variables are created the moment you assign a value using the assignment operator (=). "
            "You do not need to declare their type beforehand (dynamic typing). Every value is an object with an intrinsic type.\n\n"
            "Core built-in scalar types:\n"
            "• int: Arbitrary precision integers (e.g., 42, -5)\n"
            "• float: Double precision floating-point numbers (e.g., 3.14159)\n"
            "• str: Sequence of Unicode characters enclosed in quotes (e.g., 'hello')\n"
            "• bool: Boolean values (True or False)\n"
            "• NoneType: Represents the absence of a value (None)\n\n"
            "You can inspect an object's type with the built-in type() function."
        ),
        "code_example": (
            "age = 21                 # int\n"
            "gpa = 3.85               # float\n"
            "name = \"Alex\"            # str\n"
            "is_enrolled = True       # bool\n\n"
            "print(name, \"is\", age, \"years old.\")\n"
            "print(\"Type of gpa:\", type(gpa).__name__)\n"
            "print(\"Type of is_enrolled:\", type(is_enrolled).__name__)"
        ),
        "expected_output": (
            "Alex is 21 years old.\n"
            "Type of gpa: float\n"
            "Type of is_enrolled: bool"
        ),
        "related_topics": ["type_conversion", "operators", "equals_vs_assign", "strings_methods"]
    },

    "type_conversion": {
        "id": "type_conversion",
        "title": "Type Conversion & Casting",
        "keywords": [
            "type conversion", "type casting", "casting", "int()", "float()", "str()",
            "bool()", "implicit conversion", "explicit conversion", "convert type",
            "string to int", "int to string"
        ],
        "short_explanation": "Type conversion converts a value from one data type into another either implicitly or explicitly.",
        "detailed_explanation": (
            "Python supports two forms of type conversion:\n"
            "1. Implicit Conversion: Python automatically upgrades compatible types without data loss (e.g., adding an int to a float yields a float).\n"
            "2. Explicit Conversion (Casting): The developer manually converts a type using constructor functions like int(), float(), str(), or bool().\n\n"
            "Be cautious with invalid string conversions (e.g., int('abc')), which raise a ValueError."
        ),
        "code_example": (
            "# Implicit conversion\n"
            "x = 10     # int\n"
            "y = 2.5    # float\n"
            "result = x + y\n"
            "print(f\"Implicit: {result} ({type(result).__name__})\")\n\n"
            "# Explicit conversion (Casting)\n"
            "age_str = \"25\"\n"
            "age_int = int(age_str) + 5\n"
            "print(f\"Explicit: {age_int} ({type(age_int).__name__})\")"
        ),
        "expected_output": (
            "Implicit: 12.5 (float)\n"
            "Explicit: 30 (int)"
        ),
        "related_topics": ["variables_types", "operators", "common_errors"]
    },

    "operators": {
        "id": "operators",
        "title": "Operators in Python",
        "keywords": [
            "operators", "arithmetic operators", "comparison operators", "logical operators",
            "modulus", "floor division", "exponentiation", "and", "or", "not",
            "+", "-", "*", "/", "//", "%", "**"
        ],
        "short_explanation": "Operators are special symbols that carry out arithmetic, comparison, assignment, and logical computations.",
        "detailed_explanation": (
            "Python provides rich categories of operators:\n"
            "• Arithmetic: + (add), - (sub), * (mul), / (float div), // (floor div), % (modulo), ** (power)\n"
            "• Comparison: == (equal), != (not equal), <, >, <=, >= (returns bool)\n"
            "• Logical: and (both true), or (either true), not (inverts bool)\n"
            "• Membership: in, not in (checks membership in collections)\n"
            "• Identity: is, is not (checks object memory identity)"
        ),
        "code_example": (
            "a = 17\n"
            "b = 5\n\n"
            "print(f\"{a} / {b}  = {a / b}\")    # Float division\n"
            "print(f\"{a} // {b} = {a // b}\")   # Floor division\n"
            "print(f\"{a} % {b}  = {a % b}\")    # Modulo (remainder)\n"
            "print(f\"{a} ** 2  = {a ** 2}\")   # Exponentiation"
        ),
        "expected_output": (
            "17 / 5  = 3.4\n"
            "17 // 5 = 3\n"
            "17 % 5  = 2\n"
            "17 ** 2  = 289"
        ),
        "related_topics": ["equals_vs_assign", "is_vs_equals", "control_flow_if"]
    },

    "control_flow_if": {
        "id": "control_flow_if",
        "title": "Conditional Statements (if, elif, else)",
        "keywords": [
            "if statement", "elif", "else", "conditional statements", "branching",
            "conditions", "if-else", "nested if", "ternary operator", "decision making"
        ],
        "short_explanation": "Conditional statements allow programs to execute specific blocks of code depending on boolean expressions.",
        "detailed_explanation": (
            "The if-elif-else construct evaluates conditions sequentially. When a condition evaluates to True, its indented "
            "block executes and subsequent elif/else blocks are bypassed.\n\n"
            "Python also supports a one-line ternary conditional: 'x if condition else y'."
        ),
        "code_example": (
            "score = 85\n\n"
            "if score >= 90:\n"
            "    grade = \"A\"\n"
            "elif score >= 80:\n"
            "    grade = \"B\"\n"
            "elif score >= 70:\n"
            "    grade = \"C\"\n"
            "else:\n"
            "    grade = \"F\"\n\n"
            "status = \"Passed\" if score >= 70 else \"Failed\"\n"
            "print(f\"Score: {score} | Grade: {grade} | Status: {status}\")"
        ),
        "expected_output": (
            "Score: 85 | Grade: {grade} | Status: Passed\n"
            "Score: 85 | Grade: B | Status: Passed"
        ),
        "related_topics": ["operators", "for_loops", "while_loops", "equals_vs_assign"]
    },

    "for_loops": {
        "id": "for_loops",
        "title": "for Loops & range()",
        "keywords": [
            "for loop", "for loops", "explain for loops", "looping", "iteration",
            "range", "range()", "iterate list", "enumerate", "loop example"
        ],
        "short_explanation": "A for loop iterates over the items of any sequence (such as a list, tuple, string, or range).",
        "detailed_explanation": (
            "Unlike traditional C-style for loops with index counters, Python's for loop operates as a 'for-each' iterator.\n\n"
            "Common iteration patterns:\n"
            "• range(start, stop, step): Generates an arithmetic progression of numbers.\n"
            "• Direct iteration: for item in collection:\n"
            "• enumerate(iterable): Yields index and item pairs simultaneously.\n"
            "• for ... else: The else block runs only if the loop completed without encountering a 'break'."
        ),
        "code_example": (
            "# Iterating through a list with enumerate\n"
            "languages = [\"Python\", \"JavaScript\", \"Rust\"]\n\n"
            "for index, lang in enumerate(languages, start=1):\n"
            "    print(f\"{index}. {lang}\")\n\n"
            "# Using range to compute squares\n"
            "squares = []\n"
            "for n in range(1, 5):\n"
            "    squares.append(n * n)\n"
            "print(\"Squares:\", squares)"
        ),
        "expected_output": (
            "1. Python\n"
            "2. JavaScript\n"
            "3. Rust\n"
            "Squares: [1, 4, 9, 16]"
        ),
        "related_topics": ["while_loops", "loop_control", "list_comprehensions", "lists_methods"]
    },

    "while_loops": {
        "id": "while_loops",
        "title": "while Loops",
        "keywords": [
            "while loop", "while loops", "condition loop", "infinite loop",
            "while true", "while condition"
        ],
        "short_explanation": "A while loop repeatedly executes a target statement as long as a given boolean condition is True.",
        "detailed_explanation": (
            "Use a while loop when the number of iterations is not known in advance and depends on dynamic runtime conditions.\n\n"
            "Remember to update the loop condition variable inside the loop body to avoid infinite loops."
        ),
        "code_example": (
            "count = 1\n"
            "total = 0\n\n"
            "while count <= 5:\n"
            "    total += count\n"
            "    count += 1\n\n"
            "print(f\"Sum of 1 through 5 is {total}\")"
        ),
        "expected_output": (
            "Sum of 1 through 5 is 15"
        ),
        "related_topics": ["for_loops", "loop_control", "control_flow_if"]
    },

    "loop_control": {
        "id": "loop_control",
        "title": "break, continue, and pass Statements",
        "keywords": [
            "break", "continue", "pass", "loop control", "stop loop", "skip iteration",
            "placeholder", "break statement", "continue statement", "pass statement"
        ],
        "short_explanation": "break terminates a loop, continue skips the rest of the current iteration, and pass is a null statement placeholder.",
        "detailed_explanation": (
            "• break: Immediately terminates the innermost enclosing loop.\n"
            "• continue: Skips the remaining code in the current iteration and jumps directly to the next loop cycle.\n"
            "• pass: Acts as a syntactic placeholder where code is required by grammar but no action is needed (useful when stubbing empty functions or classes)."
        ),
        "code_example": (
            "print(\"Testing break and continue:\")\n"
            "for num in range(1, 8):\n"
            "    if num == 3:\n"
            "        continue  # skip 3\n"
            "    if num == 6:\n"
            "        break     # stop loop before 6\n"
            "    print(num, end=\" \")\n\n"
            "def unfinished_function():\n"
            "    pass  # to be implemented later\n\n"
            "print(\"\\nDone!\")"
        ),
        "expected_output": (
            "Testing break and continue:\n"
            "1 2 4 5 \n"
            "Done!"
        ),
        "related_topics": ["for_loops", "while_loops", "functions_params"]
    },

    "strings_methods": {
        "id": "strings_methods",
        "title": "Strings and Common String Methods",
        "keywords": [
            "strings", "string methods", "str methods", "strip", "split", "join",
            "replace", "format", "f-string", "slicing", "string indexing", "upper", "lower"
        ],
        "short_explanation": "Strings in Python are immutable sequences of Unicode characters with numerous built-in transformation methods.",
        "detailed_explanation": (
            "Because strings are immutable, any method that modifies a string returns a new string rather than altering the original in-place.\n\n"
            "Popular methods:\n"
            "• .strip(): Removes leading and trailing whitespace\n"
            "• .split(delimiter): Splits string into a list of substrings\n"
            "• .join(iterable): Joins items with the string as separator\n"
            "• .replace(old, new): Replaces occurrences of a substring\n"
            "• f-strings: Formatted string literals introduced in Python 3.6 (e.g., f\"{value}\")\n"
            "• Slicing: s[start:stop:step]"
        ),
        "code_example": (
            "raw_text = \"   Python,Data Science,AI   \"\n"
            "cleaned = raw_text.strip()\n"
            "topics = cleaned.split(\",\")\n\n"
            "print(\"Cleaned topics list:\", topics)\n"
            "joined = \" | \".join(topics)\n"
            "print(\"Joined formatted:\", joined)\n"
            "print(\"Reversed name:\", \"Python\"[::-1])"
        ),
        "expected_output": (
            "Cleaned topics list: ['Python', 'Data Science', 'AI']\n"
            "Joined formatted: Python | Data Science | AI\n"
            "Reversed name: nohtyP"
        ),
        "related_topics": ["lists_methods", "mutable_vs_immutable", "variables_types"]
    },

    "lists_methods": {
        "id": "lists_methods",
        "title": "Lists and Common List Methods",
        "keywords": [
            "lists", "list methods", "append", "extend", "pop", "remove",
            "sort", "reverse", "insert", "list indexing", "mutable sequence",
            "what is a list", "how to use lists"
        ],
        "short_explanation": "A list is an ordered, mutable collection of elements that can hold items of diverse types.",
        "detailed_explanation": (
            "Lists are written with square brackets []. They allow duplicates and their elements can be modified, reordered, added, or removed in-place.\n\n"
            "Common methods:\n"
            "• .append(x): Adds item x to the end\n"
            "• .extend(iterable): Appends all items from an iterable\n"
            "• .insert(i, x): Inserts item x at index i\n"
            "• .remove(x): Removes first occurrence of value x\n"
            "• .pop([i]): Removes and returns item at index i (default last)\n"
            "• .sort(): Sorts the list in-place\n"
            "• .reverse(): Reverses elements in-place"
        ),
        "code_example": (
            "fruits = [\"apple\", \"banana\", \"cherry\"]\n"
            "fruits.append(\"mango\")\n"
            "fruits.insert(1, \"blueberry\")\n"
            "print(\"After additions:\", fruits)\n\n"
            "removed_item = fruits.pop()\n"
            "print(\"Popped item:\", removed_item)\n"
            "fruits.sort()\n"
            "print(\"Sorted list:\", fruits)"
        ),
        "expected_output": (
            "After additions: ['apple', 'blueberry', 'banana', 'cherry', 'mango']\n"
            "Popped item: mango\n"
            "Sorted list: ['apple', 'banana', 'blueberry', 'cherry']"
        ),
        "related_topics": ["tuples_immutability", "lists_vs_tuples", "lists_vs_dicts", "list_comprehensions"]
    },

    "tuples_immutability": {
        "id": "tuples_immutability",
        "title": "Tuples and Immutability",
        "keywords": [
            "tuples", "tuple", "what is a tuple", "immutability", "immutable sequence",
            "tuple unpacking", "packing", "tuple methods", "tuple example", "single element tuple"
        ],
        "short_explanation": "A tuple is an ordered, immutable collection of elements defined with parentheses ().",
        "detailed_explanation": (
            "Once created, elements in a tuple cannot be changed, added, or removed. This immutability gives tuples several advantages:\n"
            "1. Safety: Protects data from unintended modifications.\n"
            "2. Hashable: Can be used as dictionary keys and set elements (if all contents are hashable).\n"
            "3. Performance: Slightly more memory-efficient than lists.\n\n"
            "Note: A single-element tuple requires a trailing comma: (42,)."
        ),
        "code_example": (
            "# Creating and unpacking a tuple\n"
            "point = (10, 20, 30)\n"
            "x, y, z = point  # Unpacking\n\n"
            "print(f\"Coordinates: X={x}, Y={y}, Z={z}\")\n"
            "print(\"Count of 20:\", point.count(20))\n"
            "print(\"Index of 30:\", point.index(30))"
        ),
        "expected_output": (
            "Coordinates: X=10, Y=20, Z=30\n"
            "Count of 20: 1\n"
            "Index of 30: 2"
        ),
        "related_topics": ["lists_vs_tuples", "lists_methods", "mutable_vs_immutable"]
    },

    "lists_vs_tuples": {
        "id": "lists_vs_tuples",
        "title": "Difference Between Lists and Tuples",
        "keywords": [
            "lists and tuples", "difference between list and tuple", "list vs tuple",
            "list and tuple", "explain lists and tuples", "compare list and tuple",
            "when to use tuple", "when to use list"
        ],
        "short_explanation": "Lists are mutable and defined with square brackets [], while tuples are immutable and defined with parentheses ().",
        "detailed_explanation": (
            "Key differences between Lists and Tuples:\n\n"
            "1. Mutability:\n"
            "   • List: Mutable (can append, pop, sort, reassign elements).\n"
            "   • Tuple: Immutable (cannot modify after creation).\n\n"
            "2. Syntax:\n"
            "   • List: [1, 2, 3]\n"
            "   • Tuple: (1, 2, 3)\n\n"
            "3. Performance & Memory:\n"
            "   • Tuples consume slightly less memory and can be slightly faster to instantiate.\n\n"
            "4. Use Cases:\n"
            "   • Lists: Collections of homogeneous items that change over time (e.g., shopping cart).\n"
            "   • Tuples: Fixed collections of heterogeneous items representing records (e.g., (latitude, longitude))."
        ),
        "code_example": (
            "# List (mutable)\n"
            "my_list = [1, 2, 3]\n"
            "my_list[0] = 99\n"
            "print(\"Modified list:\", my_list)\n\n"
            "# Tuple (immutable)\n"
            "my_tuple = (1, 2, 3)\n"
            "try:\n"
            "    my_tuple[0] = 99  # Raises TypeError\n"
            "except TypeError as e:\n"
            "    print(\"Tuple modification failed:\", e)"
        ),
        "expected_output": (
            "Modified list: [99, 2, 3]\n"
            "Tuple modification failed: 'tuple' object does not support item assignment"
        ),
        "related_topics": ["lists_methods", "tuples_immutability", "lists_vs_sets", "mutable_vs_immutable"]
    },

    "sets_operations": {
        "id": "sets_operations",
        "title": "Sets and Set Operations",
        "keywords": [
            "sets", "set", "set operations", "union", "intersection", "difference",
            "symmetric difference", "unique items", "duplicate removal", "add", "discard"
        ],
        "short_explanation": "A set is an unordered collection of unique, immutable (hashable) elements defined with curly braces {}.",
        "detailed_explanation": (
            "Sets do not allow duplicate items and do not maintain element insertion order for indexing. "
            "They are internally implemented as hash tables, making membership testing (in) run in O(1) average time.\n\n"
            "Mathematical set operations:\n"
            "• Union (|): All elements from both sets\n"
            "• Intersection (&): Elements present in both sets\n"
            "• Difference (-): Elements in set A but not in set B\n"
            "• Symmetric Difference (^): Elements in either set, but not both"
        ),
        "code_example": (
            "devs_a = {\"Alice\", \"Bob\", \"Charlie\"}\n"
            "devs_b = {\"Charlie\", \"David\", \"Eve\"}\n\n"
            "print(\"Union:\", devs_a | devs_b)\n"
            "print(\"Intersection:\", devs_a & devs_b)\n"
            "print(\"Only in A:\", devs_a - devs_b)\n\n"
            "# Removing duplicates from a list\n"
            "numbers = [1, 2, 2, 3, 4, 4, 4, 5]\n"
            "unique_numbers = list(set(numbers))\n"
            "print(\"Unique list:\", unique_numbers)"
        ),
        "expected_output": (
            "Union: {'Alice', 'Bob', 'Charlie', 'David', 'Eve'}\n"
            "Intersection: {'Charlie'}\n"
            "Only in A: {'Alice', 'Bob'}\n"
            "Unique list: [1, 2, 3, 4, 5]"
        ),
        "related_topics": ["lists_vs_sets", "dictionaries_methods", "lists_methods"]
    },

    "lists_vs_sets": {
        "id": "lists_vs_sets",
        "title": "Difference Between Lists and Sets",
        "keywords": [
            "difference between a list and a set", "list vs set", "list and set",
            "compare list and set", "what is the difference between a list and a set",
            "when to use set over list"
        ],
        "short_explanation": "Lists are ordered collections allowing duplicates, whereas sets are unordered collections of unique items with O(1) lookup.",
        "detailed_explanation": (
            "Comparison of Lists vs Sets:\n\n"
            "1. Order & Indexing:\n"
            "   • List: Preserves insertion order, supports indexing (list[0]) and slicing.\n"
            "   • Set: Unordered, does not support index lookups (set[0] raises TypeError).\n\n"
            "2. Duplicates:\n"
            "   • List: Allows duplicate items ([1, 1, 2]).\n"
            "   • Set: Automatically discards duplicates ({1, 1, 2} becomes {1, 2}).\n\n"
            "3. Membership Testing Performance:\n"
            "   • List: O(N) linear search time.\n"
            "   • Set: O(1) average constant time via hash tables.\n\n"
            "4. Element Types:\n"
            "   • List: Can hold any object including other lists.\n"
            "   • Set: Can only store hashable (immutable) objects."
        ),
        "code_example": (
            "my_list = [\"apple\", \"banana\", \"apple\", \"orange\"]\n"
            "my_set = set(my_list)\n\n"
            "print(\"List length:\", len(my_list))  # Preserves duplicate\n"
            "print(\"Set length:\", len(my_set))    # Removed duplicate\n"
            "print(\"Is 'banana' in set?\", \"banana\" in my_set)  # Fast O(1)"
        ),
        "expected_output": (
            "List length: 4\n"
            "Set length: 3\n"
            "Is 'banana' in set? True"
        ),
        "related_topics": ["sets_operations", "lists_methods", "dictionaries_methods"]
    },

    "dictionaries_methods": {
        "id": "dictionaries_methods",
        "title": "Dictionaries and Dictionary Methods",
        "keywords": [
            "dictionaries", "dictionary", "dict", "dict methods", "keys", "values",
            "items", "get()", "key-value", "hash map", "mapping", "update()", "pop()"
        ],
        "short_explanation": "A dictionary is a mutable collection of key-value pairs where keys must be unique and hashable.",
        "detailed_explanation": (
            "Dictionaries are written with curly braces {key: value}. Starting in Python 3.7, dictionaries preserve insertion order.\n\n"
            "Crucial methods:\n"
            "• .get(key, default): Safely retrieves value without raising KeyError if key is missing\n"
            "• .keys(): Returns view of dictionary keys\n"
            "• .values(): Returns view of values\n"
            "• .items(): Returns view of (key, value) pairs for iteration\n"
            "• .update(other_dict): Merges key-value pairs\n"
            "• .pop(key): Removes key and returns its value"
        ),
        "code_example": (
            "student = {\n"
            "    \"name\": \"Sarah\",\n"
            "    \"course\": \"Computer Science\",\n"
            "    \"year\": 2\n"
            "}\n\n"
            "# Safe access with .get()\n"
            "print(\"GPA:\", student.get(\"gpa\", \"Not recorded\"))\n\n"
            "# Iterating with .items()\n"
            "for key, val in student.items():\n"
            "    print(f\"{key.capitalize()}: {val}\")"
        ),
        "expected_output": (
            "GPA: Not recorded\n"
            "Name: Sarah\n"
            "Course: Computer Science\n"
            "Year: 2"
        ),
        "related_topics": ["lists_vs_dicts", "sets_operations", "mutable_vs_immutable"]
    },

    "lists_vs_dicts": {
        "id": "lists_vs_dicts",
        "title": "Difference Between a List and a Dictionary",
        "keywords": [
            "difference between a list and a dictionary", "list vs dictionary", "list and dictionary",
            "list vs dict", "what is the difference between a list and a dictionary",
            "compare list and dict"
        ],
        "short_explanation": "Lists store ordered sequences indexed by integers (0, 1, 2), while dictionaries store key-value mappings indexed by custom keys.",
        "detailed_explanation": (
            "Key differences:\n\n"
            "1. Data Structure:\n"
            "   • List: Sequential collection of items indexed by position: [item0, item1, ...]\n"
            "   • Dictionary: Associative mapping of unique keys to values: {key: value, ...}\n\n"
            "2. Access Method:\n"
            "   • List: Accessed via numerical zero-based index (e.g., list[0]).\n"
            "   • Dict: Accessed via meaningful keys (e.g., dict['email']).\n\n"
            "3. Syntax:\n"
            "   • List: items = ['apple', 'banana']\n"
            "   • Dict: prices = {'apple': 0.99, 'banana': 0.59}\n\n"
            "4. When to Use:\n"
            "   • Use a list when you need an ordered sequence of elements.\n"
            "   • Use a dictionary when data is associated with specific descriptive identifiers."
        ),
        "code_example": (
            "# List: Access by index\n"
            "fruits_list = [\"apple\", \"banana\"]\n"
            "print(\"List item at 0:\", fruits_list[0])\n\n"
            "# Dictionary: Access by label/key\n"
            "fruit_prices = {\"apple\": 1.25, \"banana\": 0.75}\n"
            "print(\"Price of apple:\", fruit_prices[\"apple\"])"
        ),
        "expected_output": (
            "List item at 0: apple\n"
            "Price of apple: 1.25"
        ),
        "related_topics": ["lists_methods", "dictionaries_methods", "lists_vs_tuples"]
    },

    "functions_params": {
        "id": "functions_params",
        "title": "Functions and Parameters in Python",
        "keywords": [
            "functions", "what are functions in python", "function parameters", "arguments",
            "def", "positional arguments", "keyword arguments", "default parameters",
            "*args", "**kwargs", "define function"
        ],
        "short_explanation": "Functions are reusable blocks of code defined with the def keyword that accept arguments and return results.",
        "detailed_explanation": (
            "Functions break programs into modular, readable, and maintainable units.\n\n"
            "Parameter types:\n"
            "• Positional arguments: Passed in matching order\n"
            "• Default/Keyword arguments: Have preset values (e.g., def greet(name='Guest'):)\n"
            "• *args: Collects arbitrary positional arguments as a tuple\n"
            "• **kwargs: Collects arbitrary keyword arguments as a dictionary"
        ),
        "code_example": (
            "def calculate_total(subtotal, tax_rate=0.08, *discounts, **metadata):\n"
            "    total = subtotal * (1 + tax_rate)\n"
            "    for discount in discounts:\n"
            "        total -= discount\n"
            "    print(f\"Processing order for: {metadata.get('customer', 'Anonymous')}\")\n"
            "    return round(total, 2)\n\n"
            "final_price = calculate_total(100.0, 0.08, 10, customer=\"Jane\")\n"
            "print(f\"Final price: ${final_price}\")"
        ),
        "expected_output": (
            "Processing order for: Jane\n"
            "Final price: $98.0"
        ),
        "related_topics": ["return_values", "lambda_expressions", "scope_legb"]
    },

    "return_values": {
        "id": "return_values",
        "title": "Return Values and None in Functions",
        "keywords": [
            "return value", "return statement", "return none", "returning multiple values",
            "tuple return", "void function", "function output"
        ],
        "short_explanation": "The return statement ends a function execution and sends the computed result back to the caller.",
        "detailed_explanation": (
            "In Python, if a function reaches the end of its body without executing an explicit return statement, "
            "it automatically returns None.\n\n"
            "Python also allows returning multiple values separated by commas; under the hood, Python packs them into a tuple."
        ),
        "code_example": (
            "def min_max(numbers):\n"
            "    if not numbers:\n"
            "        return None, None\n"
            "    return min(numbers), max(numbers)  # Returns a tuple\n\n"
            "lowest, highest = min_max([4, 12, 1, 99, 23])\n"
            "print(f\"Lowest: {lowest}, Highest: {highest}\")"
        ),
        "expected_output": (
            "Lowest: 1, Highest: 99"
        ),
        "related_topics": ["functions_params", "tuples_immutability", "lambda_expressions"]
    },

    "lambda_expressions": {
        "id": "lambda_expressions",
        "title": "Lambda Expressions (Anonymous Functions)",
        "keywords": [
            "lambda", "lambda expressions", "anonymous function", "inline function",
            "map", "filter", "sorted key", "lambda syntax"
        ],
        "short_explanation": "A lambda function is a small anonymous function defined using the lambda keyword that evaluates a single expression.",
        "detailed_explanation": (
            "Syntax: lambda arguments: expression\n\n"
            "Unlike standard functions defined with def, a lambda cannot contain statements or annotations and is restricted "
            "to a single expression whose evaluation is implicitly returned. They are most commonly passed as sorting keys "
            "to functions like sorted(), or used with map() and filter()."
        ),
        "code_example": (
            "# Sorting complex tuples by their second element\n"
            "students = [(\"Alice\", 88), (\"Bob\", 95), (\"Charlie\", 78)]\n"
            "students.sort(key=lambda item: item[1], reverse=True)\n"
            "print(\"Ranked by grade:\", students)\n\n"
            "# Quick squaring function\n"
            "square = lambda x: x * x\n"
            "print(\"Square of 9:\", square(9))"
        ),
        "expected_output": (
            "Ranked by grade: [('Bob', 95), ('Alice', 88), ('Charlie', 78)]\n"
            "Square of 9: 81"
        ),
        "related_topics": ["functions_params", "list_comprehensions", "decorators"]
    },

    "list_comprehensions": {
        "id": "list_comprehensions",
        "title": "List Comprehensions",
        "keywords": [
            "list comprehension", "list comprehensions", "explain list comprehensions",
            "comprehension syntax", "filter list", "compact loop", "generator vs comprehension"
        ],
        "short_explanation": "List comprehensions offer a concise, readable syntax for creating new lists based on existing iterables.",
        "detailed_explanation": (
            "Syntax: [expression for item in iterable if condition]\n\n"
            "Advantages:\n"
            "1. Concise: Replaces multi-line loop-and-append patterns with a single line.\n"
            "2. Fast: Comprehensions run at C-speed in the Python bytecode interpreter.\n"
            "3. Readable: Clearly expresses the mapping and filtering intent.\n\n"
            "You can also create dictionary comprehensions ({k: v for ...}) and set comprehensions ({x for ...})."
        ),
        "code_example": (
            "numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n\n"
            "# Filter even numbers and square them\n"
            "even_squares = [n * n for n in numbers if n % 2 == 0]\n"
            "print(\"Even squares:\", even_squares)\n\n"
            "# Convert words to uppercase\n"
            "words = [\"python\", \"fastapi\", \"sqlite\"]\n"
            "shouted = [w.upper() for w in words]\n"
            "print(\"Uppercase:\", shouted)"
        ),
        "expected_output": (
            "Even squares: [4, 16, 36, 64, 100]\n"
            "Uppercase: ['PYTHON', 'FASTAPI', 'SQLITE']"
        ),
        "related_topics": ["for_loops", "lists_methods", "lambda_expressions"]
    },

    "classes_objects": {
        "id": "classes_objects",
        "title": "Classes and Objects (Object-Oriented Programming)",
        "keywords": [
            "classes and objects", "explain classes and objects", "oop", "object oriented",
            "class", "object", "instance", "methods", "attributes", "blueprint", "oop in python"
        ],
        "short_explanation": "A class is a blueprint for creating objects that bundle data (attributes) and behavior (methods) together.",
        "detailed_explanation": (
            "Python is an object-oriented language. A class defines attributes and methods, while an object is a concrete instance "
            "created from that class.\n\n"
            "Core OOP concepts:\n"
            "• Class: The template or blueprint (e.g., class Car:)\n"
            "• Object / Instance: A specific manifestation (e.g., my_car = Car())\n"
            "• Attributes: Variables belonging to the object or class\n"
            "• Methods: Functions defined within a class that operate on instances"
        ),
        "code_example": (
            "class Book:\n"
            "    def __init__(self, title, author, pages):\n"
            "        self.title = title\n"
            "        self.author = author\n"
            "        self.pages = pages\n\n"
            "    def summary(self):\n"
            "        return f\"'{self.title}' by {self.author} ({self.pages} pages)\"\n\n"
            "book1 = Book(\"Fluent Python\", \"Luciano Ramalho\", 792)\n"
            "print(book1.summary())"
        ),
        "expected_output": (
            "'Fluent Python' by Luciano Ramalho (792 pages)"
        ),
        "related_topics": ["constructors_self", "inheritance", "common_errors"]
    },

    "constructors_self": {
        "id": "constructors_self",
        "title": "Constructors (__init__) and self",
        "keywords": [
            "constructors", "constructor", "__init__", "self", "what is self",
            "instance variables", "initialize object", "dunder init"
        ],
        "short_explanation": "__init__ is the initializer method automatically called when an object is instantiated, and self refers to the current instance.",
        "detailed_explanation": (
            "• __init__: Known as a dunder (double underscore) or special method. It initializes the object's instance attributes.\n"
            "• self: Explicit reference to the current instance of the class. Python automatically passes the instance as the first argument "
            "to instance methods, allowing each object to maintain its own unique state."
        ),
        "code_example": (
            "class BankAccount:\n"
            "    def __init__(self, account_holder, starting_balance=0.0):\n"
            "        self.account_holder = account_holder\n"
            "        self.balance = starting_balance\n\n"
            "    def deposit(self, amount):\n"
            "        self.balance += amount\n"
            "        return self.balance\n\n"
            "acc = BankAccount(\"Jordan\", 100.0)\n"
            "acc.deposit(50.0)\n"
            "print(f\"{acc.account_holder}'s balance: ${acc.balance}\")"
        ),
        "expected_output": (
            "Jordan's balance: $150.0"
        ),
        "related_topics": ["classes_objects", "inheritance"]
    },

    "inheritance": {
        "id": "inheritance",
        "title": "Inheritance and Polymorphism",
        "keywords": [
            "inheritance", "subclass", "superclass", "parent class", "child class",
            "super()", "method overriding", "polymorphism", "multiple inheritance"
        ],
        "short_explanation": "Inheritance allows a child class to inherit attributes and methods from a parent class, promoting code reuse.",
        "detailed_explanation": (
            "Inheritance allows you to create specialized classes based on generalized ones.\n\n"
            "• super(): Built-in function used to invoke methods from the parent class (most commonly inside __init__).\n"
            "• Method Overriding: When a subclass provides a customized implementation of a method already defined in its parent class.\n"
            "• Polymorphism: Different classes can implement the same method interface, allowing them to be used interchangeably."
        ),
        "code_example": (
            "class Animal:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n\n"
            "    def speak(self):\n"
            "        return \"Generic sound\"\n\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        return f\"{self.name} says Woof!\"\n\n"
            "d = Dog(\"Buddy\")\n"
            "print(d.speak())"
        ),
        "expected_output": (
            "Buddy says Woof!"
        ),
        "related_topics": ["classes_objects", "constructors_self"]
    },

    "exception_handling": {
        "id": "exception_handling",
        "title": "Exception Handling (try, except, finally)",
        "keywords": [
            "exception handling", "what is exception handling", "try except", "try",
            "except", "finally", "else block", "raise", "custom exception",
            "handle errors", "try catch in python"
        ],
        "short_explanation": "Exception handling allows programs to gracefully catch, handle, and recover from runtime errors without crashing.",
        "detailed_explanation": (
            "Python handles runtime errors via exceptions using the try-except-else-finally statement.\n\n"
            "Blocks:\n"
            "• try: Contains code that might raise an exception.\n"
            "• except: Catches and handles specific exceptions.\n"
            "• else: Runs only if NO exceptions were raised in the try block.\n"
            "• finally: Always runs regardless of whether an exception occurred (ideal for cleanup such as closing files).\n"
            "• raise: Manually triggers an exception."
        ),
        "code_example": (
            "def safe_divide(a, b):\n"
            "    try:\n"
            "        result = a / b\n"
            "    except ZeroDivisionError:\n"
            "        return \"Error: Cannot divide by zero!\"\n"
            "    except TypeError:\n"
            "        return \"Error: Inputs must be numerical!\"\n"
            "    else:\n"
            "        return f\"Result: {result}\"\n"
            "    finally:\n"
            "        # Always runs for clean up\n"
            "        pass\n\n"
            "print(safe_divide(10, 2))\n"
            "print(safe_divide(10, 0))"
        ),
        "expected_output": (
            "Result: 5.0\n"
            "Error: Cannot divide by zero!"
        ),
        "related_topics": ["common_errors", "file_handling"]
    },

    "file_handling": {
        "id": "file_handling",
        "title": "File Handling in Python (read, write, with)",
        "keywords": [
            "file handling", "how do i read a text file in python", "read file",
            "write file", "open()", "with statement", "context manager",
            "read text file", "reading files", "readline", "readlines"
        ],
        "short_explanation": "Python handles files using the open() function and context managers ('with' statement) for automatic resource cleanup.",
        "detailed_explanation": (
            "Always use the 'with open(...) as file:' context manager. It guarantees that the file stream is closed "
            "even if an exception occurs during reading or writing.\n\n"
            "Common file modes:\n"
            "• 'r': Read mode (default)\n"
            "• 'w': Write mode (truncates existing file or creates new)\n"
            "• 'a': Append mode (writes to end of file)\n"
            "• 'r+': Read and write\n\n"
            "Reading methods:\n"
            "• file.read(): Reads entire file as single string\n"
            "• file.readline(): Reads one line at a time\n"
            "• file.readlines(): Reads all lines into a list"
        ),
        "code_example": (
            "# Writing to a file\n"
            "with open(\"demo.txt\", \"w\", encoding=\"utf-8\") as f:\n"
            "    f.write(\"Line 1: Python file I/O\\nLine 2: Safe with context managers\")\n\n"
            "# Reading from the file\n"
            "with open(\"demo.txt\", \"r\", encoding=\"utf-8\") as f:\n"
            "    content = f.read()\n\n"
            "print(content)"
        ),
        "expected_output": (
            "Line 1: Python file I/O\n"
            "Line 2: Safe with context managers"
        ),
        "related_topics": ["exception_handling", "strings_methods"]
    },

    "modules_packages": {
        "id": "modules_packages",
        "title": "Modules and Packages in Python",
        "keywords": [
            "module", "package", "what is a python module", "modules and packages",
            "__init__.py", "standard library", "third party packages", "pip"
        ],
        "short_explanation": "A module is a single Python file containing code, while a package is a directory of modules containing an __init__.py file.",
        "detailed_explanation": (
            "• Module: Any Python file ending in .py containing functions, classes, and variables (e.g., math.py).\n"
            "• Package: A folder containing multiple module files and an __init__.py file (optional in modern namespace packages, "
            "but standard for declaring packages). Packages organize modules hierarchically using dotted notation.\n\n"
            "Python comes with a rich standard library (math, os, sys, datetime, json) and supports thousands of third-party "
            "packages via pip from PyPI."
        ),
        "code_example": (
            "# Importing standard library modules\n"
            "import math\n"
            "from datetime import datetime\n\n"
            "current_year = datetime.now().year\n"
            "pi_val = math.pi\n\n"
            "print(f\"Year: {current_year}\")\n"
            "print(f\"Square root of 64: {math.sqrt(64)}\")\n"
            "print(f\"Pi rounded: {round(pi_val, 4)}\")"
        ),
        "expected_output": (
            "Year: 2026\n"
            "Square root of 64: 8.0\n"
            "Pi rounded: 3.1416"
        ),
        "related_topics": ["import_statements", "functions_params"]
    },

    "import_statements": {
        "id": "import_statements",
        "title": "Import Statements & Aliasing",
        "keywords": [
            "import", "from import", "import as", "aliasing", "importing",
            "relative import", "circular import", "import statement"
        ],
        "short_explanation": "Import statements make definitions and code from other modules accessible in your current Python file.",
        "detailed_explanation": (
            "Common import styles:\n"
            "• import module_name: Imports module; access via module_name.item\n"
            "• from module_name import item: Imports item directly into current namespace\n"
            "• import module_name as alias: Renames module locally for brevity (e.g., import numpy as np)\n"
            "• from module_name import *: Avoid wildcard imports in production as they pollute namespace and create name collisions."
        ),
        "code_example": (
            "# Different import styles\n"
            "import random as rnd\n"
            "from math import ceil, floor\n\n"
            "number = 7.3\n"
            "print(\"Ceiling:\", ceil(number))\n"
            "print(\"Floor:\", floor(number))\n"
            "print(\"Random choice:\", rnd.choice([\"Heads\", \"Tails\"]))"
        ),
        "expected_output": (
            "Ceiling: 8\n"
            "Floor: 7\n"
            "Random choice: Heads  # (or Tails)"
        ),
        "related_topics": ["modules_packages", "functions_params"]
    },

    "iterators_generators": {
        "id": "iterators_generators",
        "title": "Iterators and Generators (yield)",
        "keywords": [
            "iterators", "generators", "yield", "generator", "iter", "next",
            "generator expression", "lazy evaluation", "memory efficiency"
        ],
        "short_explanation": "Generators are functions that yield values one at a time using 'yield', enabling memory-efficient lazy iteration.",
        "detailed_explanation": (
            "• Iterator: An object with __iter__() and __next__() methods that produces values sequentially.\n"
            "• Generator: A convenient way to write iterators using standard function syntax with the yield keyword.\n\n"
            "When a generator encounters yield, execution is paused, preserving local state, and the value is yielded. "
            "Execution resumes on the next call to next(). This avoids loading large sequences into RAM all at once."
        ),
        "code_example": (
            "def countdown(n):\n"
            "    while n > 0:\n"
            "        yield n\n"
            "        n -= 1\n\n"
            "gen = countdown(3)\n"
            "print(next(gen))\n"
            "print(next(gen))\n"
            "print(next(gen))\n"
            "# next(gen) now raises StopIteration"
        ),
        "expected_output": (
            "3\n"
            "2\n"
            "1"
        ),
        "related_topics": ["for_loops", "list_comprehensions", "decorators"]
    },

    "decorators": {
        "id": "decorators",
        "title": "Basic Decorators in Python",
        "keywords": [
            "decorators", "decorator", "@decorator", "wrapper function",
            "higher order functions", "functools.wraps", "timer decorator",
            "function decoration"
        ],
        "short_explanation": "A decorator is a function that takes another function as an argument, extends its behavior, and returns a new function.",
        "detailed_explanation": (
            "Decorators use the convenient @decorator_name syntax above a function definition.\n\n"
            "They are widely used for:\n"
            "• Logging and performance profiling\n"
            "• Access control / authentication guards\n"
            "• Input validation and caching (memoization)\n\n"
            "Always use @functools.wraps(func) on wrapper functions to preserve original function names and docstrings."
        ),
        "code_example": (
            "import functools\n\n"
            "def announce(func):\n"
            "    @functools.wraps(func)\n"
            "    def wrapper(*args, **kwargs):\n"
            "        print(\"--- Function is about to run ---\")\n"
            "        result = func(*args, **kwargs)\n"
            "        print(\"--- Function has finished ---\")\n"
            "        return result\n"
            "    return wrapper\n\n"
            "@announce\n"
            "def greet(name):\n"
            "    print(f\"Hello, {name}!\")\n\n"
            "greet(\"Sam\")"
        ),
        "expected_output": (
            "--- Function is about to run ---\n"
            "Hello, Sam!\n"
            "--- Function has finished ---"
        ),
        "related_topics": ["functions_params", "lambda_expressions"]
    },

    "equals_vs_assign": {
        "id": "equals_vs_assign",
        "title": "Difference Between == and =",
        "keywords": [
            "what is the difference between == and =", "== vs =", "== versus =",
            "equality vs assignment", "double equals vs single equals", "equal sign",
            "assignment operator", "comparison operator", "difference between = and =="
        ],
        "short_explanation": "The single equal sign (=) is for assignment, while the double equal sign (==) is for comparing equality.",
        "detailed_explanation": (
            "A frequent point of confusion for beginners:\n\n"
            "1. Single Equals (=):\n"
            "   • Assignment Operator: Stores a value into a variable.\n"
            "   • Example: age = 20 assigns 20 to the variable age.\n\n"
            "2. Double Equals (==):\n"
            "   • Comparison Operator: Evaluates whether two values are equal and returns a boolean (True or False).\n"
            "   • Example: age == 20 evaluates to True if age is 20, False otherwise.\n\n"
            "Using = inside an if statement condition is a SyntaxError in Python (unlike C/C++)."
        ),
        "code_example": (
            "# Assignment with '='\n"
            "expected_pin = 1234\n"
            "user_pin = 1234\n\n"
            "# Comparison with '=='\n"
            "is_valid = (user_pin == expected_pin)\n"
            "print(\"Is pin correct?\", is_valid)\n\n"
            "if user_pin == 1234:\n"
            "    print(\"Access granted!\")"
        ),
        "expected_output": (
            "Is pin correct? True\n"
            "Access granted!"
        ),
        "related_topics": ["is_vs_equals", "operators", "variables_types", "control_flow_if"]
    },

    "is_vs_equals": {
        "id": "is_vs_equals",
        "title": "Difference Between is and ==",
        "keywords": [
            "is versus ==", "is vs ==", "difference between is and ==", "identity vs equality",
            "memory identity", "value equality", "id()", "is None"
        ],
        "short_explanation": "== checks if values are equal, while 'is' checks if both variables refer to the exact same object in memory.",
        "detailed_explanation": (
            "• == (Equality): Compares the contents/values of objects (calls the __eq__ method).\n"
            "• is (Identity): Compares memory addresses (id(a) == id(b)).\n\n"
            "Key guideline: Always use 'is None' or 'is not None' to check for None singletons. For numerical and string values, use ==."
        ),
        "code_example": (
            "list_a = [1, 2, 3]\n"
            "list_b = [1, 2, 3]\n"
            "list_c = list_a\n\n"
            "print(\"list_a == list_b:\", list_a == list_b)  # True: identical values\n"
            "print(\"list_a is list_b:\", list_a is list_b)  # False: distinct objects in RAM\n"
            "print(\"list_a is list_c:\", list_a is list_c)  # True: same reference"
        ),
        "expected_output": (
            "list_a == list_b: True\n"
            "list_a is list_b: False\n"
            "list_a is list_c: True"
        ),
        "related_topics": ["equals_vs_assign", "mutable_vs_immutable", "operators"]
    },

    "mutable_vs_immutable": {
        "id": "mutable_vs_immutable",
        "title": "Mutable versus Immutable Objects",
        "keywords": [
            "mutable versus immutable", "mutable vs immutable", "mutability",
            "immutable objects", "mutable objects", "in place modification",
            "side effects", "pass by object reference"
        ],
        "short_explanation": "Mutable objects can have their contents altered in-place, while immutable objects cannot be modified after creation.",
        "detailed_explanation": (
            "Python data types fall into two fundamental camps:\n\n"
            "• Mutable: Lists, Dictionaries, Sets, custom classes. Can be altered in-place without changing their memory ID.\n"
            "• Immutable: Integers, Floats, Strings, Tuples, Booleans, FrozenSets. Any modification creates a brand new object in memory.\n\n"
            "Pitfall: Never use a mutable object (like a list or dict) as a default parameter in a function definition!"
        ),
        "code_example": (
            "# Immutable example (string)\n"
            "greeting = \"hello\"\n"
            "new_greeting = greeting.replace(\"h\", \"H\")\n"
            "print(\"Original:\", greeting)      # Unchanged\n"
            "print(\"Modified:\", new_greeting)  # New object\n\n"
            "# Mutable example (list)\n"
            "colors = [\"red\", \"blue\"]\n"
            "colors.append(\"green\")\n"
            "print(\"Mutated list:\", colors)    # Changed in-place"
        ),
        "expected_output": (
            "Original: hello\n"
            "Modified: Hello\n"
            "Mutated list: ['red', 'blue', 'green']"
        ),
        "related_topics": ["lists_vs_tuples", "strings_methods", "tuples_immutability"]
    },

    "common_errors": {
        "id": "common_errors",
        "title": "Common Beginner Errors in Python",
        "keywords": [
            "common beginner errors", "beginner errors", "syntaxerror", "indentationerror",
            "nameerror", "typeerror", "indexerror", "keyerror", "python errors",
            "debugging python", "traceback"
        ],
        "short_explanation": "Understanding common exceptions like SyntaxError, NameError, and TypeError makes debugging much faster.",
        "detailed_explanation": (
            "Most common beginner exceptions:\n\n"
            "1. SyntaxError: Code violates Python grammar rules (e.g., missing colon at end of if statement).\n"
            "2. IndentationError: Inconsistent spaces or tabs.\n"
            "3. NameError: Accessing a variable or function that has not been defined or spelled incorrectly.\n"
            "4. TypeError: Performing an operation on incompatible types (e.g., '10' + 5).\n"
            "5. IndexError: Accessing a list index that is out of range.\n"
            "6. KeyError: Looking up a non-existent key in a dictionary.\n"
            "7. AttributeError: Calling a method or attribute that doesn't exist on that object."
        ),
        "code_example": (
            "# Safe dictionary lookup avoiding KeyError\n"
            "data = {\"user\": \"Maria\"}\n"
            "# data[\"role\"] would raise KeyError!\n"
            "role = data.get(\"role\", \"Default User\")\n"
            "print(\"Role retrieved safely:\", role)\n\n"
            "# Safe list indexing avoiding IndexError\n"
            "items = [10, 20]\n"
            "idx = 5\n"
            "if idx < len(items):\n"
            "    print(items[idx])\n"
            "else:\n"
            "    print(f\"Index {idx} is out of bounds!\")"
        ),
        "expected_output": (
            "Role retrieved safely: Default User\n"
            "Index 5 is out of bounds!"
        ),
        "related_topics": ["exception_handling", "dictionaries_methods", "lists_methods"]
    },

    "scope_legb": {
        "id": "scope_legb",
        "title": "Scope and the LEGB Rule",
        "keywords": [
            "scope", "legb", "legb rule", "global keyword", "nonlocal keyword",
            "variable scope", "local scope", "enclosing scope", "global scope", "built-in scope"
        ],
        "short_explanation": "Python resolves variable names using the LEGB rule: Local, Enclosing, Global, and Built-in scopes.",
        "detailed_explanation": (
            "When you reference a variable, Python searches for it in this exact order:\n"
            "1. L - Local: Variables defined inside current function\n"
            "2. E - Enclosing: Variables defined in outer enclosing functions (closures)\n"
            "3. G - Global: Variables defined at top-level of module\n"
            "4. B - Built-in: Predefined Python built-ins (len, range, print)\n\n"
            "Use the global keyword to modify a module-level variable inside a function, and nonlocal for enclosing functions."
        ),
        "code_example": (
            "counter = 0  # Global\n\n"
            "def outer():\n"
            "    msg = \"Hello\"  # Enclosing\n"
            "    def inner():\n"
            "        tag = \"[Log]\"  # Local\n"
            "        print(f\"{tag} {msg} | Counter: {counter}\")\n"
            "    inner()\n\n"
            "outer()"
        ),
        "expected_output": (
            "[Log] Hello | Counter: 0"
        ),
        "related_topics": ["functions_params", "variables_types"]
    }
}
