"""state.json이 없거나 손상되었을 때 사용하는 기본 퀴즈 데이터."""

from quiz import Quiz


def create_default_quizzes():
    """Python & Git 기초 주제의 기본 퀴즈를 Quiz 인스턴스 목록으로 만들어 반환한다."""
    return [
        Quiz(
            "다음 중 정수(int)형 값은?",
            ['"42"', "3.14", "42", "[42]"],
            3,
            "따옴표로 감싸면 문자열, 소수점이 있으면 실수입니다.",
        ),
        Quiz(
            "numbers = [10, 20, 30] 일 때 20을 꺼내는 코드는?",
            ["numbers[0]", "numbers[1]", "numbers[2]", "numbers[-1]"],
            2,
            "파이썬 인덱스는 0부터 시작합니다.",
        ),
        Quiz(
            "키(key)와 값(value)을 쌍으로 저장하는 자료형은?",
            ["list", "tuple", "dict", "str"],
            3,
            "중괄호 {}로 만들고, d[\"key\"]처럼 꺼냅니다.",
        ),
        Quiz(
            "반복 횟수를 미리 알 수 없고, 조건이 참인 동안 반복할 때 알맞은 문법은?",
            ["for", "while", "if", "def"],
            2,
            "'~하는 동안'이라는 뜻의 영어 단어입니다.",
        ),
        Quiz(
            "클래스로 객체를 만들 때 자동으로 호출되어 속성을 초기화하는 메서드는?",
            ["__str__", "__init__", "__call__", "__del__"],
            2,
            "initialize(초기화)의 줄임말이 들어갑니다.",
        ),
        Quiz(
            "open() 함수로 파일을 UTF-8 인코딩으로 열 때 사용하는 인자는?",
            ['mode="utf-8"', 'encoding="utf-8"', 'charset="utf-8"', 'type="utf-8"'],
            2,
            "문자 인코딩(encoding)을 지정하는 인자입니다.",
        ),
        Quiz(
            "원격 저장소의 변경사항을 가져와 현재 브랜치에 합치는 Git 명령어는?",
            ["git push", "git clone", "git pull", "git commit"],
            3,
            "'당겨오다'라는 뜻의 영어 단어입니다.",
        ),
        Quiz(
            "오류가 발생할 수 있는 코드를 감싸서 예외를 처리할 때 사용하는 문법은?",
            ["try / except", "if / else", "for / in", "with / as"],
            1,
            "'시도하다'라는 뜻의 키워드로 시작합니다.",
        ),
    ]
