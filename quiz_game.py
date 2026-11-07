"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

import json
import os
from pathlib import Path

from default_quizzes import create_default_quizzes
from quiz import Quiz

# 프로젝트 루트(이 파일이 있는 폴더)의 state.json
STATE_FILE = Path(__file__).resolve().parent / "state.json"


class QuizGame:
    """메뉴 표시, 사용자 입력, 각 기능 실행을 담당한다."""

    MENU_ITEMS = (
        (1, "퀴즈 풀기"),
        (2, "퀴즈 추가"),
        (3, "퀴즈 목록"),
        (4, "점수 확인"),
        (0, "종료"),
    )

    def __init__(self, state_file=STATE_FILE):
        self.state_file = Path(state_file)
        self.quizzes = []
        self.best_score = None  # 아직 퀴즈를 풀지 않았으면 None
        self.running = True

    # ------------------------------------------------------------ 실행 흐름
    def run(self):
        """메뉴를 반복 출력하고, Ctrl+C / EOF가 와도 안전하게 종료한다."""
        print("=" * 40)
        print("   Python & Git 기초 퀴즈 게임")
        print("=" * 40)
        self.load_state()
        try:
            while self.running:
                self.show_menu()
                choice = self.read_number("메뉴를 선택하세요: ", 0, len(self.MENU_ITEMS) - 1)
                self.handle_menu(choice)
        except (KeyboardInterrupt, EOFError):
            print("\n\n[안내] 입력이 중단되었습니다. 데이터를 저장하고 안전하게 종료합니다.")
            self.save_state()
        print("이용해 주셔서 감사합니다. 안녕히 가세요!")

    def show_menu(self):
        print("\n---------- 메뉴 ----------")
        for number, label in self.MENU_ITEMS:
            print(f"  {number}. {label}")
        print("--------------------------")

    def handle_menu(self, choice):
        if choice == 1:
            self.play_quiz()
        elif choice == 2:
            self.add_quiz()
        elif choice == 3:
            self.list_quizzes()
        elif choice == 4:
            self.show_score()
        elif choice == 0:
            self.save_state()
            self.running = False

    # ------------------------------------------------------------ 기능 (구현 예정)
    def play_quiz(self):
        """저장된 퀴즈를 차례로 출제하고, 정답 여부와 최종 결과를 보여준다."""
        if not self.quizzes:
            print("[안내] 등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록해 주세요.")
            return

        total = len(self.quizzes)
        print(f"\n=== 퀴즈 풀기 (총 {total}문제) ===")
        print("정답 번호(1~4)를 입력하세요.")

        correct_count = 0
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            user_answer = self.read_number("정답: ", 1, quiz.CHOICE_COUNT)
            if quiz.is_correct(user_answer):
                correct_count += 1
                print("  [O] 정답입니다!")
            else:
                print(f"  [X] 오답입니다. 정답은 {quiz.answer}번 ({quiz.correct_choice()}) 입니다.")

        self.show_result(correct_count, total)

    def show_result(self, correct_count, total):
        """퀴즈를 모두 푼 뒤 결과를 출력한다."""
        print("\n========== 결과 ==========")
        print(f"  맞힌 문제: {correct_count} / {total}")
        print(f"  정답률   : {correct_count / total * 100:.0f}%")
        print("==========================")

    def add_quiz(self):
        print("[안내] 퀴즈 추가 기능은 준비 중입니다.")

    def list_quizzes(self):
        print("[안내] 퀴즈 목록 기능은 준비 중입니다.")

    def show_score(self):
        print("[안내] 점수 확인 기능은 준비 중입니다.")

    # ------------------------------------------------------------ 입력 처리
    def read_number(self, prompt, minimum, maximum):
        """공백 제거 후 정수로 변환하고, 빈 입력/문자/범위 밖 숫자는 다시 입력받는다."""
        while True:
            raw = input(prompt).strip()
            if not raw:
                print("[안내] 입력이 비어 있습니다. 다시 입력해 주세요.")
                continue
            try:
                number = int(raw)
            except ValueError:
                print(f"[안내] 숫자로 입력해 주세요. (입력값: {raw})")
                continue
            if not minimum <= number <= maximum:
                print(f"[안내] {minimum}~{maximum} 사이의 숫자를 입력해 주세요.")
                continue
            return number

    # ------------------------------------------------------------ 파일 저장/불러오기
    def load_state(self):
        """state.json을 읽는다. 없으면 기본 데이터, 손상되었으면 백업 후 기본 데이터로 복구."""
        try:
            with open(self.state_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.apply_state(data)
        except FileNotFoundError:
            print("[안내] 저장 파일(state.json)이 없어 기본 퀴즈 데이터로 시작합니다.")
            self.reset_to_default()
            self.save_state()
            return
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            print(f"[경고] state.json이 손상되었습니다: {error}")
            self.recover_from_corruption()
            return
        except OSError as error:
            print(f"[경고] state.json을 읽을 수 없습니다: {error}")
            print("[안내] 이번 실행은 기본 퀴즈 데이터로 진행합니다.")
            self.reset_to_default()
            return
        print(f"[안내] 저장된 퀴즈 {len(self.quizzes)}개를 불러왔습니다.")

    def apply_state(self, data):
        """JSON에서 읽은 딕셔너리를 검사한 뒤 게임 속성에 반영한다."""
        if not isinstance(data, dict):
            raise ValueError("최상위 데이터가 객체(dict) 형식이 아닙니다.")
        raw_quizzes = data.get("quizzes")
        if not isinstance(raw_quizzes, list):
            raise ValueError("quizzes 항목이 목록(list)이 아닙니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]

        best_score = data.get("best_score")
        if best_score is not None and (
            isinstance(best_score, bool) or not isinstance(best_score, int) or best_score < 0
        ):
            raise ValueError("best_score 값이 올바르지 않습니다.")

        self.quizzes = quizzes
        self.best_score = best_score

    def to_state(self):
        """현재 게임 상태를 JSON으로 저장할 딕셔너리로 만든다."""
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }

    def save_state(self):
        """state.json에 UTF-8로 저장한다. 임시 파일에 먼저 쓴 뒤 교체해 파일 손상을 막는다."""
        temp_file = self.state_file.with_name(self.state_file.name + ".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(self.to_state(), file, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.state_file)
            return True
        except OSError as error:
            print(f"[오류] 데이터를 저장하지 못했습니다: {error}")
            return False

    def reset_to_default(self):
        self.quizzes = create_default_quizzes()
        self.best_score = None

    def recover_from_corruption(self):
        """손상된 파일을 state.json.bak으로 백업하고 기본 데이터로 초기화한다."""
        backup_file = self.state_file.with_name(self.state_file.name + ".bak")
        try:
            os.replace(self.state_file, backup_file)
            print(f"[안내] 손상된 파일은 {backup_file.name}(으)로 백업했습니다.")
        except OSError:
            pass
        print("[안내] 기본 퀴즈 데이터로 복구합니다.")
        self.reset_to_default()
        self.save_state()
