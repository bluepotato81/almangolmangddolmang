#이 코드는 번식력이 매우 낮아 별 의미가 없는 "조루 코드"임

def update_cells_136(cells):
    num_cells = len(cells)
    next_cells = [0] * num_cells

    for i in range(num_cells):
        left = cells[i - 1] if i > 0 else 0
        current = cells[i]
        right = cells[i + 1] if i < num_cells - 1 else 0

        living_neighbors = left + right

        if current == 0:  # 규칙 1: 죽은 칸인 경우
            if living_neighbors == 2:  # 양쪽 다 생존(a) 시 탄생
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


def run_cellular_automata_136(size=100, generations=100):
    print("--- 규칙 136 (a + y) 실행 ---")
    cells = [0] * size
    spawn = 46
    cells[spawn : spawn + 8] = [1, 0, 1, 0, 0, 1, 0, 1]

    print(render(cells))
    for _ in range(generations - 1):
        cells = update_cells_136(cells)
        print(render(cells))


if __name__ == "__main__":
    run_cellular_automata_136(size=100, generations=20)  # 금방 전멸하므로 20세대만 출력