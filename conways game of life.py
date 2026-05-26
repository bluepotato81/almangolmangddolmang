"""
Conway's Game of Life — 1D / 2D / 3D
pygame 기반 인터랙티브 시뮬레이터

조작 방법:
  1 / 2 / 3      : 1D / 2D / 3D 모드 전환
  SPACE          : 실행 / 일시정지
  S              : 한 세대 진행
  R              : 랜덤 초기화
  C              : 초기화 (전부 죽임)
  +/-            : 속도 조절

  [1D]
    마우스 클릭  : 셀 토글
    0~9 숫자키   : 빠르게 룰 번호 입력 (마지막 3자리 사용)

  [2D]
    마우스 클릭/드래그 : 셀 그리기 / 지우기

  [3D]
    마우스 드래그  : 시점 회전
    마우스 휠     : 줌 인/아웃
"""

import sys
import math
import random
import pygame
import numpy as np

# ─────────────────────────────────────────────
#  전역 상수
# ─────────────────────────────────────────────
WIN_W, WIN_H = 960, 680
FPS = 60

BG      = (15, 15, 20)
FG      = (220, 220, 230)
ALIVE1D = (130, 100, 220)   # 보라
ALIVE2D = (50,  200, 140)   # 청록
ALIVE3D_NEAR = (80, 220, 160)
ALIVE3D_FAR  = (20,  80,  60)
DEAD_DIM= (35,  35,  45)
UI_BG   = (25,  25,  35)
ACCENT  = (100, 80, 200)
TEXT_DIM= (100, 100, 120)

# ─────────────────────────────────────────────
#  유틸
# ─────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ─────────────────────────────────────────────
#  1D 엘리멘터리 CA
# ─────────────────────────────────────────────
class Life1D:
    W = 160          # 셀 너비
    CELL = 6         # 픽셀/셀
    MAX_HISTORY = 80 # 화면에 보일 세대 수

    def __init__(self):
        self.rule_num = 110
        self._build_rule()
        self.reset()

    def _build_rule(self):
        """룰 번호 → 길이 8 배열"""
        self.rule = [(self.rule_num >> i) & 1 for i in range(8)]

    def reset(self):
        row = np.zeros(self.W, dtype=np.uint8)
        row[self.W // 2] = 1
        self.history = [row]
        self.gen = 0

    def randomize(self):
        row = (np.random.rand(self.W) < 0.5).astype(np.uint8)
        self.history = [row]
        self.gen = 0

    def step(self):
        g = self.history[-1]
        ng = np.zeros(self.W, dtype=np.uint8)
        for x in range(self.W):
            l = int(g[(x - 1) % self.W])
            c = int(g[x])
            r = int(g[(x + 1) % self.W])
            idx = l * 4 + c * 2 + r
            ng[x] = self.rule[idx]
        self.history.append(ng)
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)
        self.gen += 1

    def toggle_cell(self, mx, my, area_rect):
        """클릭 위치 → 셀 토글 (현재 행만)"""
        x = (mx - area_rect.left) // self.CELL
        if 0 <= x < self.W:
            row = self.history[-1].copy()
            row[x] ^= 1
            self.history[-1] = row

    def draw(self, surf, area):
        surf.fill(BG, area)
        cx, cy = area.left, area.top
        for ri, row in enumerate(reversed(self.history)):
            y = cy + (self.MAX_HISTORY - 1 - ri) * self.CELL
            for x in range(self.W):
                if row[x]:
                    t = ri / max(len(self.history) - 1, 1)
                    col = lerp_color((60, 40, 130), ALIVE1D, t)
                    pygame.draw.rect(surf, col,
                                     (cx + x * self.CELL, y,
                                      self.CELL - 1, self.CELL - 1))


# ─────────────────────────────────────────────
#  2D 콘웨이 GoL
# ─────────────────────────────────────────────
class Life2D:
    W, H = 96, 80
    CELL = 8

    def __init__(self):
        self.grid = np.zeros((self.H, self.W), dtype=np.uint8)
        self.gen  = 0
        self._painting = None   # True=paint alive, False=paint dead

    def randomize(self):
        self.grid = (np.random.rand(self.H, self.W) < 0.3).astype(np.uint8)
        self.gen = 0

    def clear(self):
        self.grid[:] = 0
        self.gen = 0

    def step(self):
        g = self.grid
        # 이웃 합산 (np.roll 8방향)
        n = (np.roll(g,  1, 0) + np.roll(g, -1, 0) +
             np.roll(g,  1, 1) + np.roll(g, -1, 1) +
             np.roll(np.roll(g,  1, 0),  1, 1) +
             np.roll(np.roll(g,  1, 0), -1, 1) +
             np.roll(np.roll(g, -1, 0),  1, 1) +
             np.roll(np.roll(g, -1, 0), -1, 1))
        self.grid = (((g == 1) & ((n == 2) | (n == 3))) |
                     ((g == 0) &  (n == 3))).astype(np.uint8)
        self.gen += 1

    def cell_at(self, mx, my, area):
        cx = (mx - area.left) // self.CELL
        cy = (my - area.top)  // self.CELL
        if 0 <= cx < self.W and 0 <= cy < self.H:
            return cy, cx
        return None

    def paint(self, mx, my, area):
        rc = self.cell_at(mx, my, area)
        if rc:
            r, c = rc
            if self._painting is None:
                self._painting = not bool(self.grid[r, c])
            self.grid[r, c] = 1 if self._painting else 0

    def stop_paint(self):
        self._painting = None

    def draw(self, surf, area):
        surf.fill(BG, area)
        for r in range(self.H):
            for c in range(self.W):
                if self.grid[r, c]:
                    pygame.draw.rect(surf, ALIVE2D,
                                     (area.left + c * self.CELL,
                                      area.top  + r * self.CELL,
                                      self.CELL - 1, self.CELL - 1))


# ─────────────────────────────────────────────
#  3D GoL (등각 투영)
# ─────────────────────────────────────────────
class Life3D:
    SZ = 18   # 격자 크기

    def __init__(self):
        self.grid = np.zeros((self.SZ,) * 3, dtype=np.uint8)
        self.gen  = 0
        self.birth   = {4, 5}
        self.survive = {5, 6, 7}
        # 카메라
        self.rot_x = 0.45
        self.rot_y = 0.60
        self.zoom  = 1.0
        self._drag_start = None

    def randomize(self):
        self.grid = (np.random.rand(self.SZ, self.SZ, self.SZ) < 0.12).astype(np.uint8)
        self.gen  = 0

    def clear(self):
        self.grid[:] = 0
        self.gen = 0

    def step(self):
        g = self.grid
        n = np.zeros_like(g, dtype=np.int32)
        for dz in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dz == 0 and dy == 0 and dx == 0:
                        continue
                    n += np.roll(np.roll(np.roll(g, dz, 0), dy, 1), dx, 2)
        alive = g.astype(bool)
        ng = np.zeros_like(g)
        for s in self.survive:
            ng[alive  & (n == s)] = 1
        for b in self.birth:
            ng[~alive & (n == b)] = 1
        self.grid = ng
        self.gen += 1

    # ── 투영 ──────────────────────────────────
    def _project(self, x, y, z, cx, cy):
        S = self.SZ
        px, py, pz = x - S/2, y - S/2, z - S/2
        # Y축 회전
        cos_y, sin_y = math.cos(self.rot_y), math.sin(self.rot_y)
        px, pz = px * cos_y + pz * sin_y, -px * sin_y + pz * cos_y
        # X축 회전
        cos_x, sin_x = math.cos(self.rot_x), math.sin(self.rot_x)
        py, pz = py * cos_x - pz * sin_x,  py * sin_x + pz * cos_x
        # 원근
        fov   = 6.0
        scale = self.zoom * 18
        d     = fov + pz
        sx    = cx + px / d * fov * scale
        sy    = cy + py / d * fov * scale
        size  = max(2.0, scale / d * fov * 0.55)
        return sx, sy, pz, size

    def draw(self, surf, area):
        surf.fill(BG, area)
        cx = area.left + area.width  // 2
        cy = area.top  + area.height // 2

        coords = np.argwhere(self.grid)   # shape (N, 3)
        if len(coords) == 0:
            return

        cells = []
        for z, y, x in coords:
            sx, sy, depth, size = self._project(x, y, z, cx, cy)
            cells.append((depth, sx, sy, size))

        # 깊이 정렬 (뒤 → 앞)
        cells.sort(key=lambda c: c[0])
        S2 = self.SZ / 2
        depth_range = S2 * math.sqrt(3)

        for depth, sx, sy, size in cells:
            t = (depth + depth_range) / (2 * depth_range)
            t = max(0.0, min(1.0, t))
            col = lerp_color(ALIVE3D_FAR, ALIVE3D_NEAR, t)
            r = int(size)
            pygame.draw.circle(surf, col, (int(sx), int(sy)), r)
            # 테두리 (depth에 따라 밝기)
            border = lerp_color(col, (200, 255, 220), 0.25)
            pygame.draw.circle(surf, border, (int(sx), int(sy)), r, 1)

    # ── 마우스 이벤트 ──────────────────────────
    def on_mouse_down(self, pos):
        self._drag_start = pos

    def on_mouse_move(self, pos, buttons):
        if buttons[0] and self._drag_start:
            dx = pos[0] - self._drag_start[0]
            dy = pos[1] - self._drag_start[1]
            self.rot_y += dx * 0.012
            self.rot_x += dy * 0.012
            self._drag_start = pos

    def on_scroll(self, direction):
        self.zoom = max(0.4, min(3.0, self.zoom + direction * 0.1))


# ─────────────────────────────────────────────
#  UI 헬퍼
# ─────────────────────────────────────────────
def draw_text(surf, text, pos, font, color=FG, anchor='topleft'):
    s = font.render(text, True, color)
    r = s.get_rect(**{anchor: pos})
    surf.blit(s, r)

def draw_panel(surf, rect, title, font_title, font_info, info_lines):
    pygame.draw.rect(surf, UI_BG, rect, border_radius=8)
    pygame.draw.rect(surf, ACCENT, rect, 1, border_radius=8)
    draw_text(surf, title, (rect.left + 10, rect.top + 8), font_title, ALIVE2D)
    for i, line in enumerate(info_lines):
        draw_text(surf, line, (rect.left + 10, rect.top + 32 + i * 18),
                  font_info, TEXT_DIM)


# ─────────────────────────────────────────────
#  메인 앱
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Conway's Game of Life — 1D / 2D / 3D")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont('monospace', 15, bold=True)
    font_info  = pygame.font.SysFont('monospace', 12)
    font_big   = pygame.font.SysFont('monospace', 20, bold=True)

    # ── 시뮬레이터 ──────────────────────────────
    sim1 = Life1D()
    sim2 = Life2D()
    sim3 = Life3D()
    sim3.randomize()
    sim2.randomize()

    # ── 레이아웃 ────────────────────────────────
    SIDEBAR_W = 210
    area = pygame.Rect(0, 50, WIN_W - SIDEBAR_W, WIN_H - 50)
    sidebar = pygame.Rect(WIN_W - SIDEBAR_W, 0, SIDEBAR_W, WIN_H)

    mode = 1          # 1=1D  2=2D  3=3D
    running = False
    speed = 10        # steps/sec
    step_acc = 0.0

    rule_input = '110'   # 1D 룰 입력 버퍼

    # ─────────────────────────────────────────
    while True:
        dt = clock.tick(FPS) / 1000.0

        # ── 이벤트 ──────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── 키보드 ──────────────────────────
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:    mode = 1
                elif ev.key == pygame.K_2:  mode = 2
                elif ev.key == pygame.K_3:  mode = 3
                elif ev.key == pygame.K_SPACE:
                    running = not running
                elif ev.key == pygame.K_s:
                    if mode == 1: sim1.step()
                    elif mode == 2: sim2.step()
                    else:          sim3.step()
                elif ev.key == pygame.K_r:
                    if mode == 1: sim1.randomize()
                    elif mode == 2: sim2.randomize()
                    else:          sim3.randomize()
                elif ev.key == pygame.K_c:
                    if mode == 1: sim1.reset()
                    elif mode == 2: sim2.clear()
                    else:          sim3.clear()
                elif ev.key == pygame.K_PLUS or ev.key == pygame.K_EQUALS:
                    speed = min(60, speed + 2)
                elif ev.key == pygame.K_MINUS:
                    speed = max(1, speed - 2)
                # 1D 룰 숫자 입력
                elif mode == 1 and pygame.K_0 <= ev.key <= pygame.K_9:
                    rule_input += str(ev.key - pygame.K_0)
                    rule_input = rule_input[-3:]
                    v = int(rule_input)
                    if 0 <= v <= 255:
                        sim1.rule_num = v
                        sim1._build_rule()

            # ── 마우스 ──────────────────────────
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if mode == 1 and area.collidepoint(ev.pos):
                    sim1.toggle_cell(*ev.pos, area)
                elif mode == 2 and area.collidepoint(ev.pos):
                    sim2.paint(*ev.pos, area)
                elif mode == 3 and area.collidepoint(ev.pos):
                    sim3.on_mouse_down(ev.pos)

            if ev.type == pygame.MOUSEBUTTONUP:
                sim2.stop_paint()

            if ev.type == pygame.MOUSEMOTION:
                if mode == 2 and pygame.mouse.get_pressed()[0]:
                    sim2.paint(*ev.pos, area)
                elif mode == 3:
                    sim3.on_mouse_move(ev.pos, pygame.mouse.get_pressed())

            if ev.type == pygame.MOUSEWHEEL and mode == 3:
                sim3.on_scroll(ev.y)

        # ── 시뮬레이션 스텝 ────────────────────
        if running:
            step_acc += dt * speed
            while step_acc >= 1.0:
                step_acc -= 1.0
                if mode == 1: sim1.step()
                elif mode == 2: sim2.step()
                else:          sim3.step()

        # ── 그리기 ──────────────────────────────
        screen.fill(BG)

        # 탭 바
        pygame.draw.rect(screen, UI_BG, (0, 0, WIN_W, 50))
        pygame.draw.line(screen, ACCENT, (0, 50), (WIN_W, 50), 1)
        title_text = "Conway's Game of Life"
        draw_text(screen, title_text, (12, 14), font_big, FG)
        for i, (label, m) in enumerate([('1  1D Elementary CA', 1),
                                         ('2  2D Classic GoL',   2),
                                         ('3  3D Spatial GoL',   3)]):
            col = ALIVE2D if mode == m else TEXT_DIM
            bx = 310 + i * 185
            if mode == m:
                pygame.draw.rect(screen, (30, 60, 50), (bx - 6, 5, 178, 38), border_radius=6)
                pygame.draw.rect(screen, ACCENT,       (bx - 6, 5, 178, 38), 1, border_radius=6)
            draw_text(screen, label, (bx, 16), font_title, col)

        # 시뮬레이터 영역
        if mode == 1:
            sim1.draw(screen, area)
        elif mode == 2:
            sim2.draw(screen, area)
        else:
            sim3.draw(screen, area)

        # ── 사이드바 ────────────────────────────
        pygame.draw.rect(screen, UI_BG, sidebar)
        pygame.draw.line(screen, ACCENT, (sidebar.left, 0), (sidebar.left, WIN_H), 1)

        sx = sidebar.left + 10
        sy = 60

        # 상태
        draw_text(screen, '── Status ──', (sx, sy), font_title, ACCENT)
        sy += 22
        if mode == 1:
            gen = sim1.gen; cells = int(sim1.history[-1].sum())
            rule_str = f'rule  {sim1.rule_num}'
        elif mode == 2:
            gen = sim2.gen; cells = int(sim2.grid.sum())
            rule_str = 'B3 / S23'
        else:
            gen = sim3.gen; cells = int(sim3.grid.sum())
            b = ','.join(map(str, sorted(sim3.birth)))
            s = ','.join(map(str, sorted(sim3.survive)))
            rule_str = f'B{b}/S{s}'
        draw_text(screen, f'gen    {gen}',   (sx, sy),      font_info, FG); sy += 18
        draw_text(screen, f'alive  {cells}', (sx, sy),      font_info, FG); sy += 18
        draw_text(screen, rule_str,           (sx, sy),      font_info, FG); sy += 18
        run_col = ALIVE2D if running else (180, 60, 60)
        draw_text(screen, '● RUN' if running else '● PAUSE', (sx, sy), font_info, run_col); sy += 18
        draw_text(screen, f'speed  {speed} gen/s', (sx, sy), font_info, TEXT_DIM); sy += 30

        # 컨트롤 안내
        draw_text(screen, '── Controls ──', (sx, sy), font_title, ACCENT); sy += 22
        controls = [
            ('SPACE', 'run / pause'),
            ('S',     'step once'),
            ('R',     'randomize'),
            ('C',     'clear'),
            ('+/-',   'speed'),
            ('1/2/3', 'mode'),
        ]
        for key, desc in controls:
            draw_text(screen, key,  (sx,      sy), font_info, ALIVE1D)
            draw_text(screen, desc, (sx + 52, sy), font_info, TEXT_DIM)
            sy += 17
        sy += 10

        # 모드별 추가 안내
        draw_text(screen, '── Mode tips ──', (sx, sy), font_title, ACCENT); sy += 22
        if mode == 1:
            tips = ['click  toggle cell',
                    '0-9    type rule #',
                    f'current: rule {sim1.rule_num}',
                    '',
                    'try: 30  chaos',
                    '     90  sierpinski',
                    '    110  universal']
        elif mode == 2:
            tips = ['drag   draw cells',
                    '',
                    'Glider — classic',
                    '  moving pattern',
                    '',
                    'B3/S23 standard',
                    '  Conway rules']
        else:
            tips = ['drag   rotate view',
                    'wheel  zoom',
                    '',
                    f'B: birth {sorted(sim3.birth)}',
                    f'S: survive',
                    f'   {sorted(sim3.survive)}',
                    '',
                    '26 neighbors']
        for tip in tips:
            draw_text(screen, tip, (sx, sy), font_info, TEXT_DIM); sy += 17

        pygame.display.flip()

# ─────────────────────────────────────────────
if __name__ == '__main__':
    main()
