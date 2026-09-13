from sqlalchemy.orm import Session
from app.models.user import User, Participant
from app.models.round import Round
from app.models.question import Question, QuestionOption, TestCase
from app.models.setting import ContestSettings
from app.core.security import get_password_hash
from app.core.logging import log_event

def seed_database(db: Session):
    # 1. Seed Contest Settings if empty
    settings = db.query(ContestSettings).first()
    if not settings:
        settings = ContestSettings(
            contest_title="Engineering Day Coding Challenge",
            subtitle="Engineering Day 2026 — Coding Competition",
            maintenance_mode=False,
            lock_all_participants=False,
            leaderboard_visible=True,
            leaderboard_frozen=False,
            max_cheating_warnings=3,
            max_participants=100
        )
        db.add(settings)

    # 2. Seed Admin User
    admin = db.query(User).filter(User.email == "admin@engday.edu").first()
    if not admin:
        admin = User(
            email="admin@engday.edu",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)

    # 3. Seed 3 Contest Rounds
    r1 = db.query(Round).filter(Round.round_number == 1).first()
    if not r1:
        r1 = Round(
            round_number=1,
            title="Round 1 — Coding Aptitude",
            description="20 Multiple Choice Questions covering Programming Concepts, DSA, Time Complexity, OOP, C/C++, Java & Python.",
            duration_minutes=20,
            max_marks=100.0,
            status="ACTIVE",
            allow_negative_marking=True,
            negative_mark_value=0.25
        )
        db.add(r1)

    r2 = db.query(Round).filter(Round.round_number == 2).first()
    if not r2:
        r2 = Round(
            round_number=2,
            title="Round 2 — Debug the Code",
            description="5 Debugging Challenges. Identify logic bugs, syntax issues, and memory leaks across C, C++, Java, and Python.",
            duration_minutes=35,
            max_marks=100.0,
            status="LOCKED"
        )
        db.add(r2)

    r3 = db.query(Round).filter(Round.round_number == 3).first()
    if not r3:
        r3 = Round(
            round_number=3,
            title="Round 3 — Final Coding Challenge",
            description="3 Algorithmic Programming Challenges ranging from Easy to Hard difficulty. Partial scoring based on passed test cases.",
            duration_minutes=60,
            max_marks=150.0,
            status="LOCKED"
        )
        db.add(r3)

    db.commit()

    # 4. Seed Round 1 MCQs (20 Questions)
    if db.query(Question).filter(Question.round_id == 1).count() == 0:
        mcqs_data = [
            {
                "title": "C++ Post-increment Output",
                "desc": "What is the output of the following C++ code snippet?",
                "code": "#include <iostream>\nusing namespace std;\nint main() {\n    int x = 5;\n    cout << x++;\n    return 0;\n}",
                "marks": 5.0,
                "category": "C++",
                "options": [("A", "4", False), ("B", "5", True), ("C", "6", False), ("D", "Compilation Error", False)]
            },
            {
                "title": "Time Complexity of Binary Search",
                "desc": "What is the worst-case time complexity of Binary Search on a sorted array of size N?",
                "code": None,
                "marks": 5.0,
                "category": "DSA",
                "options": [("A", "O(N)", False), ("B", "O(N log N)", False), ("C", "O(log N)", True), ("D", "O(1)", False)]
            },
            {
                "title": "Python List Mutability",
                "desc": "What will be printed after executing the following Python code?",
                "code": "a = [1, 2, 3]\nb = a\nb.append(4)\nprint(len(a))",
                "marks": 5.0,
                "category": "Python",
                "options": [("A", "3", False), ("B", "4", True), ("C", "Error", False), ("D", "None", False)]
            },
            {
                "title": "Java Object Reference",
                "desc": "In Java, what happens when an object reference is passed to a method?",
                "code": None,
                "marks": 5.0,
                "category": "Java",
                "options": [("A", "Passed by value of the reference", True), ("B", "Passed strictly by reference", False), ("C", "Object is cloned", False), ("D", "Compilation fails", False)]
            },
            {
                "title": "Stack LIFO Principle",
                "desc": "Which data structure follows the Last-In-First-Out (LIFO) property?",
                "code": None,
                "marks": 5.0,
                "category": "DSA",
                "options": [("A", "Queue", False), ("B", "Stack", True), ("C", "Array", False), ("D", "Tree", False)]
            },
            {
                "title": "OOP Polymorphism Concept",
                "desc": "Which OOP concept enables a single method name to behave differently depending on the calling object?",
                "code": None,
                "marks": 5.0,
                "category": "OOP",
                "options": [("A", "Encapsulation", False), ("B", "Abstraction", False), ("C", "Polymorphism", True), ("D", "Inheritance", False)]
            },
            {
                "title": "C Pointer Dereference",
                "desc": "What is the output of the following C code?",
                "code": "#include <stdio.h>\nint main() {\n    int a = 10;\n    int *p = &a;\n    *p = 20;\n    printf(\"%d\", a);\n    return 0;\n}",
                "marks": 5.0,
                "category": "C",
                "options": [("A", "10", False), ("B", "20", True), ("C", "Garbage value", False), ("D", "Address of a", False)]
            },
            {
                "title": "Recursion Base Case",
                "desc": "What happens if a recursive function lacks a proper base case?",
                "code": None,
                "marks": 5.0,
                "category": "DSA",
                "options": [("A", "Executes once and returns", False), ("B", "Stack Overflow Error", True), ("C", "Runs in O(1) time", False), ("D", "Returns 0", False)]
            },
            {
                "title": "Python Dictionary Keys",
                "desc": "Which of the following data types CANNOT be used as a key in a Python dictionary?",
                "code": None,
                "marks": 5.0,
                "category": "Python",
                "options": [("A", "Integer", False), ("B", "String", False), ("C", "Tuple", False), ("D", "List", True)]
            },
            {
                "title": "C++ Destructor Syntax",
                "desc": "How is a destructor declared in a C++ class named 'Student'?",
                "code": None,
                "marks": 5.0,
                "category": "C++",
                "options": [("A", "~Student()", True), ("B", "void Student()", False), ("C", "delete Student()", False), ("D", "Student(~)", False)]
            },
            {
                "title": "Queue FIFO Principle",
                "desc": "In a standard FIFO Queue, where are new elements inserted?",
                "code": None,
                "marks": 5.0,
                "category": "DSA",
                "options": [("A", "Front", False), ("B", "Rear", True), ("C", "Middle", False), ("D", "Top", False)]
            },
            {
                "title": "Java Final Keyword",
                "desc": "What does declaring a variable with the 'final' keyword in Java enforce?",
                "code": None,
                "marks": 5.0,
                "category": "Java",
                "options": [("A", "Variable becomes private", False), ("B", "Value cannot be modified once assigned", True), ("C", "Variable is stored on stack", False), ("D", "Variable is static", False)]
            },
            {
                "title": "Quick Sort Worst Case Complexity",
                "desc": "What is the worst-case time complexity of Quick Sort?",
                "code": None,
                "marks": 5.0,
                "category": "Algorithms",
                "options": [("A", "O(N log N)", False), ("B", "O(N^2)", True), ("C", "O(N)", False), ("D", "O(log N)", False)]
            },
            {
                "title": "C String Terminator",
                "desc": "What character is automatically appended to terminate a standard string in C?",
                "code": None,
                "marks": 5.0,
                "category": "C",
                "options": [("A", "\\n", False), ("B", "\\0", True), ("C", "\\t", False), ("D", "EOF", False)]
            },
            {
                "title": "Python Generator Keyword",
                "desc": "Which keyword is used to yield values incrementally in a Python generator function?",
                "code": None,
                "marks": 5.0,
                "category": "Python",
                "options": [("A", "return", False), ("B", "yield", True), ("C", "generate", False), ("D", "emit", False)]
            },
            {
                "title": "Hash Table Collision Resolution",
                "desc": "Which technique resolves hash table collisions by creating a linked list at each bucket?",
                "code": None,
                "marks": 5.0,
                "category": "DSA",
                "options": [("A", "Open Addressing", False), ("B", "Chaining", True), ("C", "Linear Probing", False), ("D", "Double Hashing", False)]
            },
            {
                "title": "C++ Virtual Function",
                "desc": "Why are virtual functions used in C++?",
                "code": None,
                "marks": 5.0,
                "category": "C++",
                "options": [("A", "To achieve runtime polymorphism", True), ("B", "To prevent class inheritance", False), ("C", "To speed up compilation", False), ("D", "To overload operators", False)]
            },
            {
                "title": "Java Garbage Collection",
                "desc": "Which part of Java Memory Architecture is managed by the Garbage Collector?",
                "code": None,
                "marks": 5.0,
                "category": "Java",
                "options": [("A", "Call Stack", False), ("B", "Heap Memory", True), ("C", "Method Area", False), ("D", "Program Counter", False)]
            },
            {
                "title": "Graph Traversal BFS Data Structure",
                "desc": "Which data structure is fundamentally used to implement Breadth-First Search (BFS)?",
                "code": None,
                "marks": 5.0,
                "category": "DSA",
                "options": [("A", "Stack", False), ("B", "Queue", True), ("C", "Priority Queue", False), ("D", "Array", False)]
            },
            {
                "title": "Python Slicing Negative Step",
                "desc": "What is the result of 'hello'[::-1] in Python?",
                "code": None,
                "marks": 5.0,
                "category": "Python",
                "options": [("A", "'hello'", False), ("B", "'olleh'", True), ("C", "'h'", False), ("D", "SyntaxError", False)]
            }
        ]
        for i, m in enumerate(mcqs_data, 1):
            q = Question(
                round_id=1,
                title=m["title"],
                description=m["desc"],
                code_snippet=m["code"],
                category=m["category"],
                marks=m["marks"],
                negative_marks=0.25,
                difficulty="Easy",
                order_index=i
            )
            db.add(q)
            db.flush()
            for opt_key, opt_text, is_corr in m["options"]:
                op = QuestionOption(
                    question_id=q.id,
                    option_key=opt_key,
                    option_text=opt_text,
                    is_correct=is_corr
                )
                db.add(op)
        db.commit()

    # 5. Seed Round 2 Debugging Problems (5 Problems)
    if db.query(Question).filter(Question.round_id == 2).count() == 0:
        debug_problems = [
            {
                "title": "Debug Python Array Sum Bug",
                "desc": "Fix the buggy Python function that calculates the sum of all elements in an array. The current code has an off-by-one index error.",
                "code": "def solve(arr):\n    total = 0\n    # BUG: Range goes up to len(arr) - 1, missing the last element!\n    for i in range(len(arr) - 1):\n        total += arr[i]\n    return total\n\nimport sys\nif __name__ == '__main__':\n    lines = sys.stdin.read().split()\n    if lines:\n        arr = [int(x) for x in lines]\n        print(solve(arr))\n",
                "lang": "python",
                "marks": 20.0,
                "order": 1,
                "sample_in": "1 2 3 4 5",
                "sample_out": "15",
                "test_cases": [
                    ("1 2 3 4 5", "15", False),
                    ("10 20 30", "60", True),
                    ("-5 5 10", "10", True)
                ]
            },
            {
                "title": "Debug C Max Element Logic",
                "desc": "Fix the C program below. The initial maximum is incorrectly set to 0, which fails when all array elements are negative.",
                "code": "#include <stdio.h>\nint main() {\n    int n;\n    if (scanf(\"%d\", &n) != 1) return 0;\n    int arr[100];\n    for(int i = 0; i < n; i++) {\n        scanf(\"%d\", &arr[i]);\n    }\n    // BUG: int max_val = 0 fails for negative numbers!\n    int max_val = 0;\n    for(int i = 0; i < n; i++) {\n        if (arr[i] > max_val) max_val = arr[i];\n    }\n    printf(\"%d\\n\", max_val);\n    return 0;\n}\n",
                "lang": "c",
                "marks": 20.0,
                "order": 2,
                "sample_in": "3\n-10 -5 -20",
                "sample_out": "-5",
                "test_cases": [
                    ("3\n-10 -5 -20", "-5", False),
                    ("4\n1 9 3 4", "9", True),
                    ("1\n-100", "-100", True)
                ]
            },
            {
                "title": "Debug C++ Reverse String Memory Bug",
                "desc": "Fix the C++ code for reversing a string. The loop bound swaps characters twice, returning the original string unchanged.",
                "code": "#include <iostream>\n#include <string>\n#include <algorithm>\nusing namespace std;\n\nint main() {\n    string s;\n    if (!(cin >> s)) return 0;\n    int n = s.length();\n    // BUG: Loop goes to n instead of n/2, swapping twice!\n    for (int i = 0; i < n; i++) {\n        swap(s[i], s[n - i - 1]);\n    }\n    cout << s << endl;\n    return 0;\n}\n",
                "lang": "cpp",
                "marks": 20.0,
                "order": 3,
                "sample_in": "code",
                "sample_out": "edoc",
                "test_cases": [
                    ("code", "edoc", False),
                    ("engineering", "gnireenigne", True),
                    ("a", "a", True)
                ]
            },
            {
                "title": "Debug Java Factorial Zero Bug",
                "desc": "Fix the Java Factorial program. Initializing the result variable to 0 causes all factorials to output 0.",
                "code": "import java.util.Scanner;\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (!sc.hasNextInt()) return;\n        int n = sc.nextInt();\n        // BUG: int fact = 0 multiplies everything by zero!\n        long fact = 0;\n        for (int i = 1; i <= n; i++) {\n            fact *= i;\n        }\n        System.out.println(fact);\n    }\n}\n",
                "lang": "java",
                "marks": 20.0,
                "order": 4,
                "sample_in": "5",
                "sample_out": "120",
                "test_cases": [
                    ("5", "120", False),
                    ("1", "1", True),
                    ("6", "720", True)
                ]
            },
            {
                "title": "Debug Python Palindrome Case-Sensitivity",
                "desc": "Fix the Python palindrome checker function to handle case-insensitivity and ignore spaces.",
                "code": "import sys\ndef is_palindrome(s):\n    # BUG: Does not convert to lowercase or strip spaces!\n    return s == s[::-1]\n\nif __name__ == '__main__':\n    s = sys.stdin.read().strip()\n    if is_palindrome(s):\n        print('YES')\n    else:\n        print('NO')\n",
                "lang": "python",
                "marks": 20.0,
                "order": 5,
                "sample_in": "Racecar",
                "sample_out": "YES",
                "test_cases": [
                    ("Racecar", "YES", False),
                    ("madam", "YES", True),
                    ("hello", "NO", True)
                ]
            }
        ]
        for p in debug_problems:
            q = Question(
                round_id=2,
                title=p["title"],
                description=p["desc"],
                code_snippet=p["code"],
                language=p["lang"],
                marks=p["marks"],
                order_index=p["order"],
                sample_input=p["sample_in"],
                sample_output=p["sample_out"]
            )
            db.add(q)
            db.flush()
            for inp, out, is_hid in p["test_cases"]:
                tc = TestCase(
                    question_id=q.id,
                    input_data=inp,
                    expected_output=out,
                    is_hidden=is_hid
                )
                db.add(tc)
        db.commit()

    # 6. Seed Round 3 Final Coding Problems (3 Problems: Easy, Medium, Hard)
    if db.query(Question).filter(Question.round_id == 3).count() == 0:
        coding_problems = [
            {
                "title": "Problem A: Two Sum Target",
                "desc": "Given an array of integers `nums` and an integer `target`, return the 0-based indices of the two numbers such that they add up to target.\nInput format: First line contains N and Target. Second line contains N integers.\nOutput format: Print two space-separated indices in ascending order.",
                "difficulty": "Easy",
                "marks": 40.0,
                "order": 1,
                "lang": "python",
                "sample_in": "4 9\n2 7 11 15",
                "sample_out": "0 1",
                "test_cases": [
                    ("4 9\n2 7 11 15", "0 1", False),
                    ("3 6\n3 2 4", "1 2", True),
                    ("2 10\n5 5", "0 1", True),
                    ("5 0\n-3 4 3 90 0", "0 2", True)
                ]
            },
            {
                "title": "Problem B: Longest Substring Without Repeating Characters",
                "desc": "Given a string `s`, find the length of the longest substring without repeating characters.\nInput format: A single line string `s`.\nOutput format: Print an integer representing the maximum substring length.",
                "difficulty": "Medium",
                "marks": 50.0,
                "order": 2,
                "lang": "python",
                "sample_in": "abcabcbb",
                "sample_out": "3",
                "test_cases": [
                    ("abcabcbb", "3", False),
                    ("bbbbb", "1", True),
                    ("pwwkew", "3", True),
                    ("abcdefg", "7", True)
                ]
            },
            {
                "title": "Problem C: Minimum Path Sum in Grid",
                "desc": "Given an `m x n` grid filled with non-negative numbers, find a path from top left to bottom right, which minimizes the sum of all numbers along its path. You can only move either down or right at any point in time.\nInput format: First line contains `m` and `n`. Following `m` lines contain `n` integers each.\nOutput format: Print the minimum path sum.",
                "difficulty": "Hard",
                "marks": 60.0,
                "order": 3,
                "lang": "python",
                "sample_in": "3 3\n1 3 1\n1 5 1\n4 2 1",
                "sample_out": "7",
                "test_cases": [
                    ("3 3\n1 3 1\n1 5 1\n4 2 1", "7", False),
                    ("2 3\n1 2 3\n4 5 6", "12", True),
                    ("1 1\n5", "5", True),
                    ("3 3\n1 2 5\n3 2 1\n4 1 1", "6", True)
                ]
            }
        ]
        for cp in coding_problems:
            q = Question(
                round_id=3,
                title=cp["title"],
                description=cp["desc"],
                difficulty=cp["difficulty"],
                marks=cp["marks"],
                order_index=cp["order"],
                language=cp["lang"],
                sample_input=cp["sample_in"],
                sample_output=cp["sample_out"]
            )
            db.add(q)
            db.flush()
            for inp, out, is_hid in cp["test_cases"]:
                tc = TestCase(
                    question_id=q.id,
                    input_data=inp,
                    expected_output=out,
                    is_hidden=is_hid
                )
                db.add(tc)
        db.commit()

    log_event("DATABASE_SEEDED", "Contest seed data initialized successfully.")
