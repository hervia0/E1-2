"""개별 퀴즈 한 개를 표현하는 Quiz 클래스."""


class Quiz:
    """문제(question), 선택지 4개(choices), 정답 번호 1~4(answer)를 가진 퀴즈."""

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = list(choices)
        self.answer = answer
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

    def to_dict(self):
        """JSON으로 저장할 수 있도록 딕셔너리로 변환한다."""
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리(JSON 데이터)로부터 Quiz 객체를 만든다. 형식이 틀리면 ValueError."""
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터가 객체(dict) 형식이 아닙니다.")
        try:
            return cls(data["question"], data["choices"], data["answer"])
        except KeyError as error:
            raise ValueError(f"퀴즈 데이터에 {error} 항목이 없습니다.") from error
        except TypeError as error:
            raise ValueError("퀴즈 선택지 형식이 올바르지 않습니다.") from error
