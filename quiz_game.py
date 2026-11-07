"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random

from console_input import ConsoleInput
from default_quizzes import create_default_quizzes
from quiz import Quiz
from storage import StateLoadError, StateSaveError, StateStorage


class QuizGame:
    """퀴즈 목록과 최고 점수를 관리하고, 메뉴에 따라 각 기능을 실행한다.

    - 입력 검증은 ConsoleInput에, 파일 읽기/쓰기는 StateStorage에 맡긴다.
    - QuizGame은 게임 진행 규칙과 데이터(퀴즈, 점수) 관리에 집중한다.
    """

    POINTS_PER_QUESTION = 10

    def __init__(self, storage=None, console=None):
        self.storage = storage or StateStorage()
        self.console = console or ConsoleInput()
        self.quizzes = []
        self.best_score = None  # 아직 퀴즈를 풀지 않았으면 None
        self.running = True
        # (메뉴 번호, 이름, 실행할 메서드) - 메뉴를 추가할 때 여기만 고치면 된다.
        self.menu_items = [
            (1, "퀴즈 풀기", self.play_quiz),
            (2, "퀴즈 추가", self.add_quiz),
            (3, "퀴즈 목록", self.list_quizzes),
            (4, "점수 확인", self.show_score),
            (0, "종료", self.quit),
        ]

    # ------------------------------------------------------------ 실행 흐름
    def run(self):
        """메뉴를 반복 출력하고, Ctrl+C / EOF가 와도 저장 후 안전하게 종료한다."""
        self.show_title()
        try:
            self.load_state()
            while self.running:
                self.show_menu()
                self.handle_menu(self.select_menu())
        except (KeyboardInterrupt, EOFError):
            print("\n\n[안내] 입력이 중단되었습니다. 데이터를 저장하고 안전하게 종료합니다.")
            self.save_state()
        print("이용해 주셔서 감사합니다. 안녕히 가세요!")

    def show_title(self):
        print("=" * 40)
        print("   Python & Git 기초 퀴즈 게임")
        print("=" * 40)

    def show_menu(self):
        print("\n---------- 메뉴 ----------")
        for number, label, _ in self.menu_items:
            print(f"  {number}. {label}")
        print("--------------------------")

    def select_menu(self):
        numbers = [number for number, _, _ in self.menu_items]
        return self.console.read_number("메뉴를 선택하세요: ", min(numbers), max(numbers))

    def handle_menu(self, choice):
        for number, _, action in self.menu_items:
            if number == choice:
                action()
                return

    def quit(self):
        self.save_state()
        self.running = False

    # ------------------------------------------------------------ 퀴즈 풀기 / 점수
    def play_quiz(self):
        """저장된 퀴즈를 차례로 출제하고, 정답 여부와 최종 결과를 보여준다."""
        if not self.quizzes:
            print("[안내] 등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록해 주세요.")
            return

        available = len(self.quizzes)
        print(f"\n=== 퀴즈 풀기 (등록된 문제 {available}개) ===")
        total = self.console.read_number(f"몇 문제를 풀까요? (1~{available}): ", 1, available)
        # random.sample: 원본 목록은 그대로 두고, 중복 없이 무작위로 total개를 뽑는다.
        questions = random.sample(self.quizzes, total)
        print(f"\n문제 순서는 무작위입니다. 정답 번호(1~{Quiz.CHOICE_COUNT})를 입력하세요.")

        correct_count = 0
        for number, quiz in enumerate(questions, start=1):
            if self.ask_question(quiz, number):
                correct_count += 1

        score = correct_count * self.POINTS_PER_QUESTION
        self.show_result(correct_count, total, score)
        self.update_best_score(score)

    def ask_question(self, quiz, number):
        """문제 하나를 출제하고 정답 여부를 반환한다."""
        quiz.display(number)
        user_answer = self.console.read_number("정답: ", 1, Quiz.CHOICE_COUNT)
        if quiz.is_correct(user_answer):
            print("  [O] 정답입니다!")
            return True
        print(f"  [X] 오답입니다. 정답은 {quiz.answer}번 ({quiz.correct_choice()}) 입니다.")
        return False

    def show_result(self, correct_count, total, score):
        """퀴즈를 모두 푼 뒤 결과를 출력한다."""
        print("\n========== 결과 ==========")
        print(f"  맞힌 문제: {correct_count} / {total}")
        print(f"  정답률   : {correct_count / total * 100:.0f}%")
        print(f"  점수     : {score}점")
        print("==========================")

    def update_best_score(self, score):
        """이번 점수를 최고 점수와 비교해 더 높으면 갱신하고 파일에 저장한다."""
        if self.best_score is None:
            print(f"[안내] 첫 기록! 최고 점수가 {score}점으로 저장되었습니다.")
            self.best_score = score
        elif score > self.best_score:
            print(f"[안내] 최고 점수 갱신! {self.best_score}점 -> {score}점")
            self.best_score = score
        else:
            print(f"[안내] 현재 최고 점수는 {self.best_score}점입니다.")
        self.save_state()

    def show_score(self):
        """저장된 최고 점수를 보여준다."""
        print("\n=== 점수 확인 ===")
        if self.best_score is None:
            print("[안내] 아직 퀴즈를 풀지 않았습니다. '퀴즈 풀기'로 도전해 보세요!")
            return
        print(f"  최고 점수: {self.best_score}점 (문제당 {self.POINTS_PER_QUESTION}점)")

    # ------------------------------------------------------------ 퀴즈 관리
    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록하고 파일에 저장한다."""
        print("\n=== 퀴즈 추가 ===")
        question = self.console.read_text("문제: ")
        choices = self.read_choices()
        answer = self.console.read_number(
            f"정답 번호 (1~{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT
        )
        new_quiz = Quiz(question, choices, answer)

        print("\n[미리보기]")
        new_quiz.display()
        print(f"  정답: {answer}번")
        if not self.console.read_yes_no("이 퀴즈를 등록할까요? (y/n): "):
            print("[안내] 퀴즈 등록을 취소했습니다.")
            return

        self.quizzes.append(new_quiz)
        if self.save_state():
            print(f"[안내] 퀴즈가 등록되었습니다. (현재 {len(self.quizzes)}문제)")

    def read_choices(self):
        """서로 다른 선택지 4개를 입력받는다."""
        choices = []
        while len(choices) < Quiz.CHOICE_COUNT:
            choice = self.console.read_text(f"선택지 {len(choices) + 1}: ")
            if choice in choices:
                print("[안내] 이미 입력한 선택지와 같습니다. 다른 내용을 입력해 주세요.")
                continue
            choices.append(choice)
        return choices

    def list_quizzes(self):
        """등록된 퀴즈의 문제, 선택지, 정답을 모두 보여준다."""
        if not self.quizzes:
            print("[안내] 등록된 퀴즈가 없습니다. '퀴즈 추가'로 퀴즈를 등록해 주세요.")
            return

        print(f"\n=== 퀴즈 목록 (총 {len(self.quizzes)}문제) ===")
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            print(f"  -> 정답: {quiz.answer}번")

    # ------------------------------------------------------------ 상태 저장/불러오기
    def load_state(self):
        """state.json을 불러온다. 없으면 기본 데이터, 손상되었으면 백업 후 기본 데이터로 복구."""
        try:
            data = self.storage.load()
            if data is None:
                print("[안내] 저장 파일(state.json)이 없어 기본 퀴즈 데이터로 시작합니다.")
                self.reset_to_default()
                self.save_state()
                return
            self.apply_state(data)
        except (StateLoadError, ValueError) as error:
            print(f"[경고] state.json을 불러오지 못했습니다: {error}")
            self.recover_from_corruption()
            return
        print(f"[안내] 저장된 퀴즈 {len(self.quizzes)}개를 불러왔습니다.")

    def apply_state(self, data):
        """JSON에서 읽은 딕셔너리를 검사한 뒤 게임 속성에 반영한다. 형식이 틀리면 ValueError."""
        if not isinstance(data, dict):
            raise ValueError("최상위 데이터가 객체(dict) 형식이 아닙니다.")
        raw_quizzes = data.get("quizzes")
        if not isinstance(raw_quizzes, list):
            raise ValueError("quizzes 항목이 목록(list)이 아닙니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]

        best_score = data.get("best_score")
        if best_score is not None and not self.is_valid_score(best_score):
            raise ValueError("best_score 값이 올바르지 않습니다.")

        self.quizzes = quizzes
        self.best_score = best_score

    @staticmethod
    def is_valid_score(value):
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0

    def to_state(self):
        """현재 게임 상태를 state.json 스키마에 맞는 딕셔너리로 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }

    def save_state(self):
        """현재 상태를 저장한다. 성공하면 True, 실패하면 안내 후 False."""
        try:
            self.storage.save(self.to_state())
        except StateSaveError as error:
            print(f"[오류] 데이터를 저장하지 못했습니다: {error}")
            return False
        return True

    def reset_to_default(self):
        self.quizzes = create_default_quizzes()
        self.best_score = None

    def recover_from_corruption(self):
        """손상된 파일을 백업하고 기본 퀴즈 데이터로 초기화한다."""
        backup_path = self.storage.backup_corrupted()
        if backup_path is not None:
            print(f"[안내] 기존 파일은 {backup_path.name}(으)로 백업했습니다.")
        print("[안내] 기본 퀴즈 데이터로 복구합니다.")
        self.reset_to_default()
        self.save_state()
