"""개별 퀴즈 한 개를 표현하는 Quiz 클래스."""

# 퀴즈 학년(난이도) 목록. 빈 문자열("")은 학년을 지정하지 않은 '미분류' 퀴즈.
GRADES = ("초1", "초2", "초3", "초4", "초5", "초6", "중1", "중2", "중3", "고1", "고2")


class Quiz:
    """문제(question), 선택지 4개(choices), 정답 번호 1~4(answer), 힌트(hint), 학년(grade)을 가진 퀴즈."""

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer, hint="", grade=""):
        self.question = question
        self.choices = list(choices)
        self.answer = answer
        self.hint = hint
        self.grade = grade
        self.validate()

    def validate(self):
        """퀴즈 데이터가 올바른지 검사하고, 문제가 있으면 ValueError를 발생시킨다."""
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("문제(question)는 비어 있지 않은 문자열이어야 합니다.")
        if len(self.choices) != self.CHOICE_COUNT:
            raise ValueError(f"선택지(choices)는 {self.CHOICE_COUNT}개여야 합니다.")
        if not all(isinstance(choice, str) and choice.strip() for choice in self.choices):
            raise ValueError("선택지는 비어 있지 않은 문자열이어야 합니다.")
        # bool은 int의 하위 타입이므로 별도로 제외한다.
        if isinstance(self.answer, bool) or not isinstance(self.answer, int):
            raise ValueError("정답(answer)은 정수여야 합니다.")
        if not 1 <= self.answer <= self.CHOICE_COUNT:
            raise ValueError(f"정답(answer)은 1~{self.CHOICE_COUNT} 사이여야 합니다.")
        if not isinstance(self.hint, str):
            raise ValueError("힌트(hint)는 문자열이어야 합니다.")
        if self.grade != "" and self.grade not in GRADES:
            raise ValueError(f"학년(grade)은 {', '.join(GRADES)} 중 하나이거나 빈 문자열이어야 합니다.")

    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        title = f"[문제 {number}] " if number is not None else ""
        print(f"\n{title}{self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")

    def is_correct(self, user_answer):
        """사용자가 고른 번호가 정답인지 확인한다."""
        return user_answer == self.answer

    def correct_choice(self):
        """정답 선택지의 내용을 반환한다."""
        return self.choices[self.answer - 1]

    def has_hint(self):
        return bool(self.hint.strip())

    def grade_label(self):
        return self.grade or "미분류"

    def to_dict(self):
        """JSON으로 저장할 수 있도록 딕셔너리로 변환한다."""
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
            "grade": self.grade,
        }

    @staticmethod
    def guess_grade(question):
        """'[초3-2 · 분수] ...' 처럼 문제 앞에 붙은 표기에서 학년(초3)을 추정한다. 없으면 ""."""
        if isinstance(question, str) and question.startswith("["):
            tag = question[1:3]
            if tag in GRADES:
                return tag
        return ""

    @classmethod
    def from_dict(cls, data):
        """딕셔너리(JSON 데이터)로부터 Quiz 객체를 만든다. 형식이 틀리면 ValueError."""
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터가 객체(dict) 형식이 아닙니다.")
        try:
            question = data["question"]
            # hint, grade는 나중에 추가된 항목이므로 예전 state.json에 없을 수 있다.
            # grade가 없으면 문제 앞의 [학년 · 단원] 표기에서 추정한다.
            grade = data.get("grade")
            if grade is None:
                grade = cls.guess_grade(question)
            return cls(question, data["choices"], data["answer"], data.get("hint", ""), grade)
        except KeyError as error:
            raise ValueError(f"퀴즈 데이터에 {error} 항목이 없습니다.") from error
        except TypeError as error:
            raise ValueError("퀴즈 선택지 형식이 올바르지 않습니다.") from error
