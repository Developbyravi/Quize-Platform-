from sqlalchemy.orm import Session
from app.models.user import User, Participant
from app.models.round import Round
from app.models.question import Question, QuestionOption, TestCase
from app.models.setting import ContestSettings
from app.core.security import get_password_hash
from app.core.config import settings as app_settings
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

    # 2. Seed Admin User idempotently from environment variables
    admin_email = (app_settings.ADMIN_EMAIL or "kr2932429@gmail.com").lower()
    admin_password = app_settings.ADMIN_PASSWORD or "11rr@@TT"

    user_with_email = db.query(User).filter(User.email == admin_email).first()
    if user_with_email:
        user_with_email.role = "admin"
        user_with_email.hashed_password = get_password_hash(admin_password)
        user_with_email.is_active = True
    else:
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            existing_admin.email = admin_email
            existing_admin.hashed_password = get_password_hash(admin_password)
            existing_admin.is_active = True
        else:
            new_admin = User(
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                role="admin",
                is_active=True
            )
            db.add(new_admin)

    db.query(User).filter(User.role == "admin", User.email != admin_email).update({"role": "participant"})
    db.commit()

    # 3. Seed 3 Contest Rounds with exact durations & max marks
    r1 = db.query(Round).filter(Round.round_number == 1).first()
    if not r1:
        r1 = Round(
            round_number=1,
            title="Round 1 — Coding Aptitude",
            description="20 MCQ questions covering C, C++, Java, Python, OOP, DSA, Algorithms and OS concepts.",
            duration_minutes=18,
            max_marks=20.0,
            status="ACTIVE",
            allow_negative_marking=False,
            negative_mark_value=0.0
        )
        db.add(r1)
    else:
        r1.duration_minutes = 18
        r1.max_marks = 20.0
        r1.allow_negative_marking = False
        r1.negative_mark_value = 0.0

    r2 = db.query(Round).filter(Round.round_number == 2).first()
    if not r2:
        r2 = Round(
            round_number=2,
            title="Round 2 — Debug the Code",
            description="3 Debugging Problems in C, Python, and C++. Identify logic/indexing bugs and pass automated test cases.",
            duration_minutes=30,
            max_marks=30.0,
            status="LOCKED"
        )
        db.add(r2)
    else:
        r2.duration_minutes = 30
        r2.max_marks = 30.0

    r3 = db.query(Round).filter(Round.round_number == 3).first()
    if not r3:
        r3 = Round(
            round_number=3,
            title="Round 3 — Final Coding Challenge",
            description="2 Algorithmic Programming Challenges. Evaluated via visible and hidden test cases with partial scoring.",
            duration_minutes=35,
            max_marks=50.0,
            status="LOCKED"
        )
        db.add(r3)
    else:
        r3.duration_minutes = 35
    r3.max_marks = 50.0

    # Prune non-spec demo questions exceeding competition bounds (R1 > 20, R2 > 3, R3 > 2)
    db.query(Question).filter(Question.round_id == 1, Question.order_index > 20).delete(synchronize_session=False)
    db.query(Question).filter(Question.round_id == 2, Question.order_index > 3).delete(synchronize_session=False)
    db.query(Question).filter(Question.round_id == 3, Question.order_index > 2).delete(synchronize_session=False)

    db.commit()

    # 4. Seed Round 1 MCQs (20 Questions - Verbatim from Notepad File)
    mcqs_data = [
        {
            "order": 1,
            "title": "Q1. C — Array Indexing",
            "desc": "What is printed by the following code snippet?",
            "code": "int arr[] = {10, 20, 30, 40};\n\nprintf(\"%d\", arr[1] + arr[3]);",
            "category": "C",
            "explanation": "arr[1] is 20, arr[3] is 40. 20 + 40 = 60.",
            "options": [("A", "40", False), ("B", "50", False), ("C", "60", True), ("D", "70", False)]
        },
        {
            "order": 2,
            "title": "Q2. Python — len()",
            "desc": "What is the output?",
            "code": "x = [10, 20, [30, 40], 50]\nprint(len(x))",
            "category": "Python",
            "explanation": "[30, 40] is one nested list element. Total length is 4.",
            "options": [("A", "4", True), ("B", "5", False), ("C", "3", False), ("D", "Error", False)]
        },
        {
            "order": 3,
            "title": "Q3. Java — Array Index",
            "desc": "What is printed?",
            "code": "int[] arr = {10, 20, 30, 40};\n\nSystem.out.println(arr[arr.length - 2]);",
            "category": "Java",
            "explanation": "arr.length is 4. arr[4 - 2] = arr[2] = 30.",
            "options": [("A", "20", False), ("B", "30", True), ("C", "40", False), ("D", "2", False)]
        },
        {
            "order": 4,
            "title": "Q4. C++ — Default Access",
            "desc": "Consider the code below. What happens?",
            "code": "class Test {\n    int x = 10;\n};\n\nint main() {\n    Test t;\n    cout << t.x;\n}",
            "category": "C++",
            "explanation": "Members of a C++ class are private by default, causing a compilation error.",
            "options": [("A", "Prints 10", False), ("B", "Prints 0", False), ("C", "Compilation error", True), ("D", "Runtime error", False)]
        },
        {
            "order": 5,
            "title": "Q5. Stack — LIFO",
            "desc": "A stack initially contains: 10, 20, 30 where 30 is on top.\nOperations:\npop()\npush(40)\npop()\nWhat is on top after these operations?",
            "code": None,
            "category": "DSA",
            "explanation": "pop() removes 30. push(40) adds 40 on top. pop() removes 40. 20 is left on top.",
            "options": [("A", "10", False), ("B", "20", True), ("C", "30", False), ("D", "40", False)]
        },
        {
            "order": 6,
            "title": "Q6. C — Pass by Value",
            "desc": "What is printed?",
            "code": "void change(int x) {\n    x = 20;\n}\n\nint main() {\n    int x = 10;\n    change(x);\n    printf(\"%d\", x);\n}",
            "category": "C",
            "explanation": "C uses pass-by-value, so the caller's x remains 10.",
            "options": [("A", "10", True), ("B", "20", False), ("C", "30", False), ("D", "Garbage value", False)]
        },
        {
            "order": 7,
            "title": "Q7. Python — *args",
            "desc": "What is printed for args?",
            "code": "def test(a, *args):\n    print(a)\n    print(args)\n\ntest(10, 20, 30)",
            "category": "Python",
            "explanation": "*args captures excess positional arguments as a tuple (20, 30).",
            "options": [("A", "[20, 30]", False), ("B", "(20, 30)", True), ("C", "{20, 30}", False), ("D", "20, 30 as separate values", False)]
        },
        {
            "order": 8,
            "title": "Q8. Python — **kwargs",
            "desc": "What is printed?",
            "code": "def test(**kwargs):\n    print(len(kwargs))\n\ntest(a=10, b=20, c=30)",
            "category": "Python",
            "explanation": "**kwargs captures 3 keyword arguments into a dictionary of length 3.",
            "options": [("A", "0", False), ("B", "2", False), ("C", "3", True), ("D", "Error", False)]
        },
        {
            "order": 9,
            "title": "Q9. Linked List",
            "desc": "You have the head pointer of a singly linked list. Which operation can be performed in O(1) time?",
            "code": None,
            "category": "DSA",
            "explanation": "Inserting a new node before head takes O(1) time by updating pointers.",
            "options": [("A", "Search for a value", False), ("B", "Insert at the beginning", True), ("C", "Insert at the end without a tail pointer", False), ("D", "Find the middle element", False)]
        },
        {
            "order": 10,
            "title": "Q10. Binary Search",
            "desc": "An array is sorted in ascending order:\n5 12 18 25 31 40 52\nUsing binary search, which element is checked first?",
            "code": None,
            "category": "Algorithms",
            "explanation": "Mid index = (0 + 6) // 2 = 3, which holds 25.",
            "options": [("A", "5", False), ("B", "18", False), ("C", "25", True), ("D", "40", False)]
        },
        {
            "order": 11,
            "title": "Q11. Hashing",
            "desc": "A hash table uses h(k) = k % 10. Where will key 27 initially be placed?",
            "code": None,
            "category": "DSA",
            "explanation": "27 % 10 = 7.",
            "options": [("A", "Index 2", False), ("B", "Index 7", True), ("C", "Index 10", False), ("D", "Index 27", False)]
        },
        {
            "order": 12,
            "title": "Q12. Java — Default Array Value",
            "desc": "What is printed?",
            "code": "int[] a = new int[5];\n\na[2] = 10;\n\nSystem.out.println(a[0] + a[2]);",
            "category": "Java",
            "explanation": "Java primitive int arrays initialize to 0. a[0] = 0, a[2] = 10 -> 0 + 10 = 10.",
            "options": [("A", "0", False), ("B", "10", True), ("C", "12", False), ("D", "Garbage value", False)]
        },
        {
            "order": 13,
            "title": "Q13. C++ — Constructor",
            "desc": "If obj is declared and obj.show() is executed, what is printed?",
            "code": "class A {\n    int x;\n\npublic:\n    A() {\n        x = 5;\n    }\n\n    void show() {\n        cout << x;\n    }\n};\n\nA obj;\nobj.show();",
            "category": "C++",
            "explanation": "Constructor sets x = 5, show() prints 5.",
            "options": [("A", "0", False), ("B", "5", True), ("C", "Garbage value", False), ("D", "Compilation error", False)]
        },
        {
            "order": 14,
            "title": "Q14. OOP — Encapsulation",
            "desc": "A programmer declares a variable balance as private and provides deposit() and withdraw() methods to modify it. Which OOP concept is primarily being used?",
            "code": None,
            "category": "OOP",
            "explanation": "Hiding internal state behind public getter/setter methods is encapsulation.",
            "options": [("A", "Inheritance", False), ("B", "Polymorphism", False), ("C", "Encapsulation", True), ("D", "Abstraction only", False)]
        },
        {
            "order": 15,
            "title": "Q15. Time Complexity",
            "desc": "Consider:\nfor(int i = 0; i < n; i++)\n    printf(\"*\");\nIf n becomes twice as large, approximately how many times more iterations occur?",
            "code": None,
            "category": "Algorithms",
            "explanation": "Linear complexity O(n) means doubling n doubles the iterations.",
            "options": [("A", "Same number", False), ("B", "2 times", True), ("C", "4 times", False), ("D", "n times", False)]
        },
        {
            "order": 16,
            "title": "Q16. Python — Arguments",
            "desc": "What is the output?",
            "code": "def f(a, b=2, *args):\n    return a + b + sum(args)\n\nprint(f(1, 3, 4, 5))",
            "category": "Python",
            "explanation": "a=1, b=3, args=(4,5). 1 + 3 + 4 + 5 = 13.",
            "options": [("A", "9", False), ("B", "10", False), ("C", "13", True), ("D", "15", False)]
        },
        {
            "order": 17,
            "title": "Q17. Operating Systems — Deadlock",
            "desc": "Which statement is correct?",
            "code": None,
            "category": "OS",
            "explanation": "Circular wait is one of Coffman's 4 necessary conditions for deadlock.",
            "options": [("A", "Deadlock requires preemption", False), ("B", "Deadlock can occur only with one process", False), ("C", "Circular wait is one of the necessary conditions for deadlock", True), ("D", "Round Robin always causes deadlock", False)]
        },
        {
            "order": 18,
            "title": "Q18. Quicksort",
            "desc": "Which statement is correct about Quicksort?",
            "code": None,
            "category": "Algorithms",
            "explanation": "Quicksort has O(n log n) average time complexity and O(n²) worst-case time complexity.",
            "options": [("A", "Its average-case complexity is O(n)", False), ("B", "Its average-case complexity is O(n log n), but its worst case can be O(n²)", True), ("C", "Its worst-case complexity is always O(n log n)", False), ("D", "Its complexity is always O(n²)", False)]
        },
        {
            "order": 19,
            "title": "Q19. Nested Loop",
            "desc": "What is the time complexity?",
            "code": "for(int i = 1; i <= n; i++) {\n    for(int j = 1; j <= i; j++) {\n        printf(\"*\");\n    }\n}",
            "category": "Algorithms",
            "explanation": "Summation 1 + 2 + ... + n = n(n+1)/2 = O(n²).",
            "options": [("A", "O(n)", False), ("B", "O(log n)", False), ("C", "O(n log n)", False), ("D", "O(n²)", True)]
        },
        {
            "order": 20,
            "title": "Q20. Hashing — Collision",
            "desc": "A hash table has size 7 and uses h(k) = k % 7 with linear probing. Insert: 10, 17, 24. Where will 24 be stored?",
            "code": None,
            "category": "DSA",
            "explanation": "10 % 7 = 3 (idx 3). 17 % 7 = 3 (probes to idx 4). 24 % 7 = 3 (probes to idx 5).",
            "options": [("A", "Index 2", False), ("B", "Index 3", False), ("C", "Index 4", False), ("D", "Index 5", True)]
        }
    ]

    for item in mcqs_data:
        existing_q = db.query(Question).filter(Question.round_id == 1, Question.order_index == item["order"]).first()
        if not existing_q:
            q = Question(
                round_id=1,
                title=item["title"],
                description=item["desc"],
                code_snippet=item["code"],
                category=item["category"],
                marks=1.0,
                negative_marks=0.0,
                difficulty="Easy",
                order_index=item["order"]
            )
            db.add(q)
            db.flush()
            for opt_key, opt_text, is_corr in item["options"]:
                op = QuestionOption(
                    question_id=q.id,
                    option_key=opt_key,
                    option_text=opt_text,
                    is_correct=is_corr
                )
                db.add(op)
        else:
            # Update existing question attributes cleanly without deleting participant data
            existing_q.title = item["title"]
            existing_q.description = item["desc"]
            existing_q.code_snippet = item["code"]
            existing_q.category = item["category"]
            existing_q.marks = 1.0
            existing_q.negative_marks = 0.0

    db.commit()

    # 5. Seed Round 2 Debugging Problems (3 Problems - Verbatim from Notepad File)
    r2_problems = [
        {
            "order": 1,
            "title": "Problem 1 — C: Find the Maximum",
            "desc": "The program is intended to find the largest element in an array. Fix the bugs in the provided C code.",
            "code": "#include <stdio.h>\n\nint main() {\n    int arr[] = {12, 45, 23, 67, 34};\n    int n = 5;\n    int max = 0;\n\n    for (int i = 0; i <= n; i++) {\n        if (arr[i] < max) {\n            max = arr[i];\n        }\n    }\n\n    printf(\"%d\", max);\n\n    return 0;\n}",
            "lang": "c",
            "marks": 10.0,
            "sample_in": "",
            "sample_out": "67",
            "test_cases": [
                ("", "67", False)
            ]
        },
        {
            "order": 2,
            "title": "Problem 2 — Python: Count Even Numbers",
            "desc": "The program should count how many even numbers are present in the list. Fix the bugs in the Python code.",
            "code": "numbers = [3, 8, 12, 7, 10, 15]\ncount = 0\n\nfor i in range(len(numbers) - 1):\n    if numbers[i] % 2 == 1:\n        count += 1\n\nprint(\"Even numbers:\", count)",
            "lang": "python",
            "marks": 10.0,
            "sample_in": "",
            "sample_out": "Even numbers: 3",
            "test_cases": [
                ("", "Even numbers: 3", False)
            ]
        },
        {
            "order": 3,
            "title": "Problem 3 — C++: Reverse an Array",
            "desc": "The program should reverse the array. Identify and fix the indexing and loop termination bugs in C++.",
            "code": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int arr[] = {10, 20, 30, 40, 50};\n    int n = 5;\n\n    for (int i = 0; i < n / 2; i++) {\n        int temp = arr[i];\n        arr[i] = arr[n - i];\n        arr[n - i] = temp;\n    }\n\n    for (int i = 0; i <= n; i++) {\n        cout << arr[i] << \" \";\n    }\n\n    return 0;\n}",
            "lang": "cpp",
            "marks": 10.0,
            "sample_in": "",
            "sample_out": "50 40 30 20 10",
            "test_cases": [
                ("", "50 40 30 20 10", False)
            ]
        }
    ]

    for p in r2_problems:
        existing_q = db.query(Question).filter(Question.round_id == 2, Question.order_index == p["order"]).first()
        if not existing_q:
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
        else:
            existing_q.title = p["title"]
            existing_q.description = p["desc"]
            existing_q.code_snippet = p["code"]
            existing_q.language = p["lang"]
            existing_q.marks = p["marks"]

    db.commit()

    # 6. Seed Round 3 Final Coding Problems (2 Problems - Verbatim from Notepad File)
    r3_problems = [
        {
            "order": 1,
            "title": "Problem 1 — Second Largest Distinct Element",
            "desc": "You are given an array containing N integers. Your task is to find the second largest distinct element in the array.\n\nA value is considered distinct only once. For example, in '10 20 20 15', the largest distinct element is 20, and the second largest distinct element is 15. If the array does not contain at least two different values, print -1.",
            "difficulty": "Easy-Medium",
            "marks": 20.0,
            "lang": "python",
            "input_format": "First line: An integer N representing the number of elements in the array.\nSecond line: N space-separated integers.",
            "output_format": "Print a single integer representing the second largest distinct element. If no second largest distinct element exists, print -1.",
            "constraints": "1 <= N <= 100000\n-10^9 <= A[i] <= 10^9",
            "sample_in": "5\n10 5 20 8 15",
            "sample_out": "15",
            "test_cases": [
                ("5\n10 5 20 8 15", "15", False),
                ("6\n4 9 2 9 7 4", "7", False),
                ("5\n8 8 8 8 8", "-1", False),
                ("-10 -5 -20 -3 -8", "-5", True),
                ("2\n100 50", "50", True),
                ("1\n10", "-1", True),
                ("7\n5 5 5 3 3 2 1", "3", True),
                ("6\n-1 -5 -2 -8 -3 -2", "-3", True),
                ("8\n100 90 80 100 70 90 60 50", "90", True)
            ]
        },
        {
            "order": 2,
            "title": "Problem 2 — Count Vowels",
            "desc": "You are given a string containing English letters and spaces. Your task is to count the total number of vowels present in the string.\n\nThe vowels are: a, e, i, o, u. Both uppercase and lowercase vowels must be counted. Each occurrence of a vowel is counted separately. Spaces are ignored. If there are no vowels, print 0.",
            "difficulty": "Medium",
            "marks": 30.0,
            "lang": "python",
            "input_format": "The input contains one line containing the string.",
            "output_format": "Print a single integer representing the total number of vowels.",
            "constraints": "1 <= length of string <= 100000",
            "sample_in": "Engineering",
            "sample_out": "4",
            "test_cases": [
                ("Engineering", "4", False),
                ("HELLO WORLD", "3", False),
                ("rhythm", "0", False),
                ("Artificial Intelligence", "9", True),
                ("I Love Coding", "5", True),
                ("Programming", "3", True),
                ("AEIOU", "5", True),
                ("aeiou", "5", True),
                ("XYZ", "0", True),
                ("A quick brown fox", "5", True)
            ]
        }
    ]

    for cp in r3_problems:
        existing_q = db.query(Question).filter(Question.round_id == 3, Question.order_index == cp["order"]).first()
        if not existing_q:
            q = Question(
                round_id=3,
                title=cp["title"],
                description=cp["desc"],
                difficulty=cp["difficulty"],
                marks=cp["marks"],
                order_index=cp["order"],
                language=cp["lang"],
                input_format=cp.get("input_format"),
                output_format=cp.get("output_format"),
                constraints=cp.get("constraints"),
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
        else:
            existing_q.title = cp["title"]
            existing_q.description = cp["desc"]
            existing_q.marks = cp["marks"]
            existing_q.input_format = cp.get("input_format")
            existing_q.output_format = cp.get("output_format")
            existing_q.constraints = cp.get("constraints")

    db.commit()
    log_event("DATABASE_SEEDED", "Contest dataset initialized/updated cleanly.")
