def update_cells_30(cells):
    """규칙 30(Rule 30)에 따라 다음 세대로 업데이트합니다.
    양 끝 경계 바깥은 항상 '죽은 상태(0)'입니다."""
    num_cells = len(cells)
    next_cells = [0] * num_cells

    for i in range(num_cells):
        # 고정 경계 조건 (Fixed Boundary Conditions)
        left = cells[i - 1] if i > 0 else 0
        current = cells[i]
        right = cells[i + 1] if i < num_cells - 1 else 0

        # 규칙 30의 8가지 상태 매핑
        if left == 1 and current == 1 and right == 1: next_cells[i] = 0
        elif left == 1 and current == 1 and right == 0: next_cells[i] = 0
        elif left == 1 and current == 1 and right == 1: next_cells[i] = 0 # 1 0 1 케이스
        elif left == 1 and current == 0 and right == 1: next_cells[i] = 0
        elif left == 1 and current == 0 and right == 0: next_cells[i] = 1
        elif left == 0 and current == 1 and right == 1: next_cells[i] = 1
        elif left == 0 and current == 1 and right == 0: next_cells[i] = 1
        elif left == 0 and current == 0 and right == 1: next_cells[i] = 1
        elif left == 0 and current == 0 and right == 0: next_cells[i] = 0

    return next_cells


def render(cells):
    """세포들의 상태를 문자열로 시각화합니다. (1은 ■, 0은 □)"""
    return "".join("■" if cell == 1 else "□" for cell in cells)


def run_cellular_automata_30(size=100, generations=100):
    """셀룰러 오토마타를 생성하고 지정된 세대만큼 실행합니다."""
    # 초기 상태 설정
    cells = [0] * size
    spawn = 46
    cells[spawn : spawn + 8] = [0, 0, 0, 0, 0, 0, 1, 1]

    # 첫 번째 세대 출력
    print(render(cells))

    # 세대 반복
    for _ in range(generations - 1):
        cells = update_cells_30(cells)
        print(render(cells))


# 실행 (크기 100칸, 100세대 동안 진행)
if __name__ == "__main__":
    run_cellular_automata_30(size=100, generations=500)