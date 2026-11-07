"""게임 전체 흐름을 관리하는 QuizGame 클래스."""

from default_quizzes import create_default_quizzes


class QuizGame:
    """메뉴 표시, 사용자 입력, 각 기능 실행을 담당한다."""

    MENU_ITEMS = (
        (1, "퀴즈 풀기"),
        (2, "퀴즈 추가"),
        (3, "퀴즈 목록"),
        (4, "점수 확인"),
        (0, "종료"),
    )

    def __init__(self):
        self.quizzes = create_default_quizzes()
        self.running = True

    # ------------------------------------------------------------ 실행 흐름
    def run(self):
        """메뉴를 반복 출력하고, Ctrl+C / EOF가 와도 안전하게 종료한다."""
        print("=" * 40)
        print("   Python & Git 기초 퀴즈 게임")
        print("=" * 40)
        try:
            while self.running:
                self.show_menu()
                choice = self.read_number("메뉴를 선택하세요: ", 0, len(self.MENU_ITEMS) - 1)
                self.handle_menu(choice)
        except (KeyboardInterrupt, EOFError):
            print("\n\n[안내] 입력이 중단되어 프로그램을 안전하게 종료합니다.")
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
