def update_cells(cells):
    """현재 세대의 세포 상태를 규칙 102에 따라 다음 세대로 업데이트합니다.
    양 끝 경계 바깥은 항상 '죽은 상태(0)'로 가정합니다."""
    num_cells = len(cells)
    next_cells = [0] * num_cells

    for i in range(num_cells):
        # 고정 경계 조건 (Fixed Boundary Conditions)
        # 왼쪽 끝(0)이면 왼쪽 이웃은 없으므로 0, 아니면 i-1
        left = cells[i - 1] if i > 0 else 0
        current = cells[i]
        # 오른쪽 끝(num_cells-1)이면 오른쪽 이웃은 없으므로 0, 아니면 i+1
        right = cells[i + 1] if i < num_cells - 1 else 0

        # 주변에 살아있는 이웃의 수 (왼쪽 + 오른쪽)
        living_neighbors = left + right

        if current == 0:  # 규칙 1: 죽은 칸인 경우
            if living_neighbors == 1:
                next_cells[i] = 1
            else:
                next_cells[i] = 0
        else:  # 규칙 2: 살아있는 칸인 경우
            if living_neighbors == 1:
                next_cells[i] = 1
            else:
                next_cells[i] = 0

    return next_cells


def render(cells):
    """세포들의 상태를 문자열로 시각화합니다. (1은 ■, 0은 □)"""
    return "".join("■" if cell == 1 else "□" for cell in cells)


def run_cellular_automata(size=100, generations=100):
    """셀룰러 오토마타를 생성하고 지정된 세대만큼 실행합니다."""
    # 초기 상태 설정
    cells = [0] * size
    spawn = 46
    cells[spawn : spawn + 8] = [1, 0, 0, 0, 0, 0, 0, 1]

    # 첫 번째 세대 출력
    print(render(cells))

    # 세대 반복
    for _ in range(generations - 1):
        cells = update_cells(cells)
        print(render(cells))


# 실행 (크기 100칸, 100세대 동안 진행)
if __name__ == "__main__":
    run_cellular_automata(size=100, generations=100)