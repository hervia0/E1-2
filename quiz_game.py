"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import random
import unicodedata
from datetime import datetime

from console_input import ConsoleInput
from default_quizzes import create_default_quizzes
from quiz import GRADES, Quiz
from storage import StateLoadError, StateSaveError, StateStorage

ALL_GRADES_LABEL = "전체"


class QuizGame:
    """퀴즈 목록과 최고 점수를 관리하고, 메뉴에 따라 각 기능을 실행한다.

    - 입력 검증은 ConsoleInput에, 파일 읽기/쓰기는 StateStorage에 맡긴다.
    - QuizGame은 게임 진행 규칙과 데이터(퀴즈, 점수) 관리에 집중한다.
    """

    POINTS_PER_QUESTION = 10
    HINT_PENALTY = 5

    def __init__(self, storage=None, console=None):
        self.storage = storage or StateStorage()
        self.console = console or ConsoleInput()
        self.quizzes = []
        self.best_score = None  # 아직 퀴즈를 풀지 않았으면 None
        # 게임 1회 = {"played_at", "grade", "total", "correct", "hints_used", "score"}
        self.history = []
        self.running = True
        # (메뉴 번호, 이름, 실행할 메서드) - 메뉴를 추가할 때 여기만 고치면 된다.
        self.menu_items = [
            (1, "퀴즈 풀기", self.play_quiz),
            (2, "퀴즈 추가", self.add_quiz),
            (3, "퀴즈 목록", self.list_quizzes),
            (4, "점수 확인", self.show_score),
            (5, "퀴즈 삭제", self.delete_quiz),
            (6, "게임 기록", self.show_history),
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
        print("   초1~고2 수학 퀴즈 게임")
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

        print("\n=== 퀴즈 풀기 ===")
        grade_label, pool = self.select_grade()
        available = len(pool)
        print(f"\n[{grade_label}] 문제 {available}개 중에서 출제합니다.")
        total = self.console.read_number(f"몇 문제를 풀까요? (1~{available}): ", 1, available)
        # random.sample: 원본 목록은 그대로 두고, 중복 없이 무작위로 total개를 뽑는다.
        questions = random.sample(pool, total)
        print(f"\n문제 순서는 무작위입니다. 정답 번호(1~{Quiz.CHOICE_COUNT})를 입력하세요.")
        print(f"힌트가 필요하면 h를 입력하세요. (힌트를 보고 맞히면 {self.HINT_PENALTY}점 차감)")

        correct_count = 0
        hints_used = 0
        score = 0
        for number, quiz in enumerate(questions, start=1):
            is_correct, used_hint = self.ask_question(quiz, number)
            if used_hint:
                hints_used += 1
            if is_correct:
                correct_count += 1
                score += self.question_points(used_hint)

        self.show_result(grade_label, correct_count, total, hints_used, score)
        self.record_history(grade_label, total, correct_count, hints_used, score)
        self.update_best_score(score)  # 최고 점수 비교 후 기록과 함께 저장

    # ------------------------------------------------------------ 학년 선택
    def count_by_grade(self):
        """학년별 퀴즈 개수를 {학년: 개수} 딕셔너리로 반환한다."""
        counts = {}
        for quiz in self.quizzes:
            counts[quiz.grade] = counts.get(quiz.grade, 0) + 1
        return counts

    def show_grade_options(self, zero_label, with_counts=True):
        """0번(zero_label)과 1~11번 학년 목록을 한 줄에 4개씩 출력한다."""
        counts = self.count_by_grade()
        if with_counts:
            print(f"   0. {zero_label} ({len(self.quizzes)}문제)")
        else:
            print(f"   0. {zero_label}")
        cells = []
        for number, grade in enumerate(GRADES, start=1):
            cell = f"{number:>4}. {grade}"
            if with_counts:
                cell += f" ({counts.get(grade, 0):>2}문제)"
            cells.append(cell)
        for start in range(0, len(cells), 4):
            print("".join(cells[start:start + 4]))

    def select_grade(self):
        """학년을 선택받아 (학년 이름, 해당 학년 퀴즈 목록)을 반환한다. 0번은 전체."""
        print("\n--- 학년 선택 ---")
        self.show_grade_options(ALL_GRADES_LABEL)
        while True:
            choice = self.console.read_number(
                f"학년 번호를 선택하세요 (0~{len(GRADES)}): ", 0, len(GRADES)
            )
            if choice == 0:
                return ALL_GRADES_LABEL, list(self.quizzes)
            grade = GRADES[choice - 1]
            pool = [quiz for quiz in self.quizzes if quiz.grade == grade]
            if pool:
                return grade, pool
            print(f"[안내] {grade} 퀴즈가 없습니다. 다른 학년을 선택해 주세요.")

    def ask_question(self, quiz, number):
        """문제 하나를 출제하고 (정답 여부, 힌트 사용 여부)를 반환한다."""
        quiz.display(number)
        used_hint = False
        while True:
            answer = self.console.read_number_or_command(
                "정답(힌트: h): ", 1, Quiz.CHOICE_COUNT, commands=("h",)
            )
            if answer != "h":
                break
            used_hint = self.show_hint(quiz, used_hint)

        if quiz.is_correct(answer):
            points = self.question_points(used_hint)
            print(f"  [O] 정답입니다! (+{points}점)")
            return True, used_hint
        print(f"  [X] 오답입니다. 정답은 {quiz.answer}번 ({quiz.correct_choice()}) 입니다.")
        return False, used_hint

    def show_hint(self, quiz, already_used):
        """힌트를 출력하고, 이번 문제에서 힌트를 사용했는지 여부를 반환한다."""
        if not quiz.has_hint():
            print("  [안내] 이 문제에는 힌트가 없습니다.")
            return already_used
        if already_used:
            print(f"  [힌트] {quiz.hint}")
        else:
            print(f"  [힌트] {quiz.hint}  (이 문제는 맞혀도 {self.HINT_PENALTY}점 차감)")
        return True

    def question_points(self, used_hint):
        """정답 1문제의 점수. 힌트를 사용했으면 차감한다."""
        if used_hint:
            return self.POINTS_PER_QUESTION - self.HINT_PENALTY
        return self.POINTS_PER_QUESTION

    def show_result(self, grade_label, correct_count, total, hints_used, score):
        """퀴즈를 모두 푼 뒤 결과를 출력한다."""
        print("\n========== 결과 ==========")
        print(f"  학년     : {grade_label}")
        print(f"  맞힌 문제: {correct_count} / {total}")
        print(f"  정답률   : {correct_count / total * 100:.0f}%")
        print(f"  힌트 사용: {hints_used}회")
        print(f"  점수     : {score}점 / {total * self.POINTS_PER_QUESTION}점 만점")
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

    def record_history(self, grade_label, total, correct_count, hints_used, score):
        """게임 1회의 결과를 날짜/시간, 선택한 학년과 함께 기록 목록에 추가한다."""
        self.history.append(
            {
                "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "grade": grade_label,
                "total": total,
                "correct": correct_count,
                "hints_used": hints_used,
                "score": score,
            }
        )

    def show_score(self):
        """저장된 최고 점수를 보여준다."""
        print("\n=== 점수 확인 ===")
        if self.best_score is None:
            print("[안내] 아직 퀴즈를 풀지 않았습니다. '퀴즈 풀기'로 도전해 보세요!")
            return
        print(
            f"  최고 점수: {self.best_score}점 "
            f"(문제당 {self.POINTS_PER_QUESTION}점, 힌트 사용 시 -{self.HINT_PENALTY}점)"
        )
        if not self.history:
            return
        print(f"  플레이 횟수: {len(self.history)}회 (자세한 내용은 '게임 기록' 메뉴)")

        best_by_grade = self.best_scores_by_grade()
        print("\n  [학년별 최고 기록]")
        for grade in (ALL_GRADES_LABEL,) + GRADES:
            if grade in best_by_grade:
                record = best_by_grade[grade]
                print(
                    f"   {self.pad(grade, 4)}  {record['score']:>4}점  "
                    f"({record['correct']}/{record['total']}문제 정답)"
                )

    def best_scores_by_grade(self):
        """게임 기록에서 학년별로 점수가 가장 높은 기록을 골라 {학년: 기록}으로 반환한다."""
        best = {}
        for record in self.history:
            grade = record.get("grade", ALL_GRADES_LABEL)  # 학년 선택 이전 기록은 전체로 본다.
            if grade not in best or record["score"] > best[grade]["score"]:
                best[grade] = record
        return best

    def show_history(self):
        """지금까지의 모든 게임 기록을 오래된 순서로 보여준다."""
        print("\n=== 게임 기록 ===")
        if not self.history:
            print("[안내] 아직 게임 기록이 없습니다.")
            return
        print(
            f"   No  {self.pad('날짜/시간', 19)}  {self.pad('학년', 4)}  "
            f"{self.pad('문제수', 6)}  정답  힌트  점수"
        )
        for number, record in enumerate(self.history, start=1):
            grade = record.get("grade", ALL_GRADES_LABEL)
            print(
                f"  {number:>3}  {record['played_at']:<19}  {self.pad(grade, 4)}  "
                f"{record['total']:>6}  {record['correct']:>4}  "
                f"{record['hints_used']:>4}  {record['score']:>4}"
            )

    @staticmethod
    def pad(text, width):
        """한글처럼 화면에서 2칸을 차지하는 글자를 고려해 text를 width칸에 맞춰 왼쪽 정렬한다."""
        display_width = sum(
            2 if unicodedata.east_asian_width(char) in ("W", "F") else 1 for char in text
        )
        return text + " " * max(0, width - display_width)

    # ------------------------------------------------------------ 퀴즈 관리
    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록하고 파일에 저장한다."""
        print("\n=== 퀴즈 추가 ===")
        print("이 퀴즈의 학년(난이도)을 선택하세요.")
        self.show_grade_options("미분류 (학년 지정 안 함)", with_counts=False)
        grade_number = self.console.read_number(
            f"학년 번호 (0~{len(GRADES)}): ", 0, len(GRADES)
        )
        grade = GRADES[grade_number - 1] if grade_number else ""

        question = self.console.read_text("문제: ")
        if grade:
            # 기본 퀴즈와 같은 형식으로 문제 앞에 [학년]을 붙인다.
            question = f"[{grade}] {question}"
        choices = self.read_choices()
        answer = self.console.read_number(
            f"정답 번호 (1~{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT
        )
        hint = self.console.read_optional_text("힌트 (없으면 Enter): ")
        new_quiz = Quiz(question, choices, answer, hint, grade)

        print("\n[미리보기]")
        new_quiz.display()
        print(f"  학년: {new_quiz.grade_label()}")
        print(f"  정답: {answer}번")
        if new_quiz.has_hint():
            print(f"  힌트: {hint}")
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
            if quiz.has_hint():
                print(f"  -> 힌트: {quiz.hint}")

    def delete_quiz(self):
        """번호를 골라 퀴즈를 삭제하고 파일에 반영한다. 0을 입력하면 취소한다."""
        if not self.quizzes:
            print("[안내] 삭제할 퀴즈가 없습니다.")
            return

        print(f"\n=== 퀴즈 삭제 (총 {len(self.quizzes)}문제) ===")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"  {number}. {quiz.question}")
        index = self.console.read_number(
            "삭제할 퀴즈 번호 (취소: 0): ", 0, len(self.quizzes)
        )
        if index == 0:
            print("[안내] 삭제를 취소했습니다.")
            return

        target = self.quizzes[index - 1]
        if not self.console.read_yes_no(f"'{target.question}' 퀴즈를 삭제할까요? (y/n): "):
            print("[안내] 삭제를 취소했습니다.")
            return

        self.quizzes.pop(index - 1)
        if self.save_state():
            print(f"[안내] 퀴즈를 삭제했습니다. (남은 문제 {len(self.quizzes)}개)")

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

        # history는 나중에 추가된 항목이므로, 예전 state.json에 없으면 빈 목록으로 둔다.
        history = data.get("history", [])
        if not isinstance(history, list) or not all(self.is_valid_record(r) for r in history):
            raise ValueError("history 항목의 형식이 올바르지 않습니다.")

        self.quizzes = quizzes
        self.best_score = best_score
        self.history = history

    @classmethod
    def is_valid_record(cls, record):
        if not isinstance(record, dict) or not isinstance(record.get("played_at"), str):
            return False
        # grade는 학년 선택 기능과 함께 추가된 항목이므로 없어도 된다.
        if "grade" in record and not isinstance(record["grade"], str):
            return False
        return all(
            cls.is_valid_score(record.get(key))
            for key in ("total", "correct", "hints_used", "score")
        )

    @staticmethod
    def is_valid_score(value):
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0

    def to_state(self):
        """현재 게임 상태를 state.json 스키마에 맞는 딕셔너리로 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
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
        self.history = []

    def recover_from_corruption(self):
        """손상된 파일을 백업하고 기본 퀴즈 데이터로 초기화한다."""
        backup_path = self.storage.backup_corrupted()
        if backup_path is not None:
            print(f"[안내] 기존 파일은 {backup_path.name}(으)로 백업했습니다.")
        print("[안내] 기본 퀴즈 데이터로 복구합니다.")
        self.reset_to_default()
        self.save_state()
