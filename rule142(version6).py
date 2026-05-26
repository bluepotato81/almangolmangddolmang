#한 세포만 있어도 무한히 프랙탈을 생성하는 "바이러스 코드"

def update_cells_142(cells):
    num_cells = len(cells)
    next_cells = [0] * num_cells

    for i in range(num_cells):
        left = cells[i - 1] if i > 0 else 0
        current = cells[i]
        right = cells[i + 1] if i < num_cells - 1 else 0

        living_neighbors = left + right

        if current == 0:  # 규칙 1: 죽은 칸인 경우
            if living_neighbors in (1, 2):  # 한쪽 또는 양쪽 다 생존(c) 시 탄생
                next_cells[i] = 1
            else:
                next_cells[i] = 0
        else:  # 규칙 2: 살아있는 칸인 경우
            if living_neighbors == 2:  # 양쪽 다 생존(y) 시 유지
                next_cells[i] = 1
            else:
                next_cells[i] = 0

    return next_cells


def render(cells):
    return "".join("■" if cell == 1 else "□" for cell in cells)


def run_cellular_automata_142(size=100, generations=100):
    print("\n--- 규칙 142 (c + y) 실행 ---")
    cells = [0] * size
    spawn = 46
    cells[spawn : spawn + 8] = [1, 1, 0, 0, 0, 0, 1, 1]

    print(render(cells))
    for _ in range(generations - 1):
        cells = update_cells_142(cells)
        print(render(cells))


if __name__ == "__main__":
    run_cellular_automata_142(size=100, generations=100)