"""사용자 입력을 받아 검증하는 ConsoleInput 클래스."""


class ConsoleInput:
    """모든 입력은 앞뒤 공백을 제거한 뒤 검사하고, 잘못되면 안내 후 다시 입력받는다.

    Ctrl+C(KeyboardInterrupt)와 입력 종료(EOFError)는 여기서 잡지 않고
    호출한 쪽(QuizGame.run)으로 전달해 저장 후 안전하게 종료하도록 한다.
    """

    EMPTY_MESSAGE = "[안내] 입력이 비어 있습니다. 다시 입력해 주세요."

    def read_text(self, prompt):
        """비어 있지 않은 문자열을 입력받는다."""
        while True:
            text = input(prompt).strip()
            if text:
                return text
            print(self.EMPTY_MESSAGE)

    def read_optional_text(self, prompt):
        """빈 입력도 허용하는 문자열 입력. (선택 항목용)"""
        return input(prompt).strip()

    def read_number(self, prompt, minimum, maximum):
        """minimum~maximum 범위의 정수를 입력받는다."""
        while True:
            raw = input(prompt).strip()
            number = self.parse_number(raw, minimum, maximum)
            if number is not None:
                return number

    def read_number_or_command(self, prompt, minimum, maximum, commands):
        """범위 내 정수 또는 commands에 포함된 명령어(소문자) 하나를 입력받는다."""
        while True:
            raw = input(prompt).strip()
            if raw.lower() in commands:
                return raw.lower()
            number = self.parse_number(raw, minimum, maximum)
            if number is not None:
                return number

    def read_yes_no(self, prompt):
        """y/n 질문에 대한 답을 True/False로 반환한다."""
        while True:
            answer = input(prompt).strip().lower()
            if answer in ("y", "yes", "예", "네"):
                return True
            if answer in ("n", "no", "아니오", "아니요"):
                return False
            if not answer:
                print(self.EMPTY_MESSAGE)
            else:
                print("[안내] y 또는 n으로 입력해 주세요.")

    def parse_number(self, raw, minimum, maximum):
        """문자열을 정수로 바꾼다. 실패하면 안내 메시지를 출력하고 None을 반환한다."""
        if not raw:
            print(self.EMPTY_MESSAGE)
            return None
        try:
            number = int(raw)
        except ValueError:
            print(f"[안내] 숫자로 입력해 주세요. (입력값: {raw})")
            return None
        if not minimum <= number <= maximum:
            print(f"[안내] {minimum}~{maximum} 사이의 숫자를 입력해 주세요.")
            return None
        return number
