import glob
import os
import random

import pygame

# ---------------------------------------------------------------
# วางรูปไว้ในโฟลเดอร์ images/ ข้างๆไฟล์นี้ แล้วตั้งชื่อตามนี้ (นามสกุลอะไรก็ได้ jpg/png/webp)
#   images/BG.*             -> พื้นหลังท้องฟ้า
#   images/sao.*            -> โปสเตอร์ Sword Art Online
#   images/sg.*             -> โปสเตอร์ Spirit Chronicles
#   images/wt.*             -> โปสเตอร์ World Trigger
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")

W, H = 900, 830
POSTER_BOX = (380, 460)

QUESTIONS = [
    {"img": "sao", "answer": "Sword Art Online"},
    {"img": "sg", "answer": "Spirit Chronicles"},
    {"img": "wt", "answer": "World Trigger"},
]

# ตัวเลือกหลอก (เพิ่มเองได้)
FAKE_NAMES = [
    "Attack on Titan", "Naruto", "Bleach", "Re:Zero", "Overlord",
    "Fairy Tail", "Black Clover", "Mushoku Tensei", "Konosuba",
    "Fate/Zero", "Toradora", "Haikyuu!!", "One Piece", "Hunter x Hunter",
    "Sword Oratoria", "No Game No Life", "Accel World", "Log Horizon",
]


def find_image(name):
    files = glob.glob(os.path.join(IMG_DIR, name + ".*"))
    return files[0] if files else None


def load_fit(name, box):
    """โหลดรูปแล้วย่อให้พอดีกล่อง (รักษาสัดส่วน) ถ้าไม่เจอไฟล์คืน None"""
    path = find_image(name)
    if not path:
        return None
    img = pygame.image.load(path).convert_alpha()
    iw, ih = img.get_size()
    scale = min(box[0] / iw, box[1] / ih)
    return pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))


def load_cover(name, size):
    path = find_image(name)
    if not path:
        return None
    img = pygame.image.load(path).convert()
    iw, ih = img.get_size()
    scale = max(size[0] / iw, size[1] / ih)
    img = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
    return img


def make_choices(answer):
    pool = [n for n in FAKE_NAMES if n != answer]
    # เอาชื่อจากข้ออื่นมาเป็นตัวหลอกด้วย
    pool += [q["answer"] for q in QUESTIONS if q["answer"] != answer]
    wrongs = random.sample(list(set(pool)), 3)
    choices = wrongs + [answer]
    random.shuffle(choices)
    return choices


def draw_text(surf, font, text, color, pos, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Anime Quiz")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 34)
    big = pygame.font.SysFont(None, 56)

    bg = load_cover("BG", (W, H))
    posters = {q["img"]: load_fit(q["img"], POSTER_BOX) for q in QUESTIONS}

    # ตัวเลือก 2x2 อยู่ใต้รูป
    buttons = [
        pygame.Rect(40 + (i % 2) * 420, 590 + (i // 2) * 90, 400, 70)
        for i in range(4)
    ]
    play_btn = pygame.Rect(W // 2 - 130, H // 2, 260, 80)
    back_btn = pygame.Rect(W // 2 - 130, H // 2 + 60, 260, 70)
    title_font =pygame.font.SysFont(None, 110)

    def new_game():
        order = QUESTIONS[:]
        random.shuffle(order)
        return order

    order = new_game()
    idx = 0
    score = 0
    choices = make_choices(order[0]["answer"])
    picked = None  # index ที่เลือก
    state = "menu"  # menu / ask / feedback / done

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            # ---------- หน้า menu ----------
            if state == "menu":
                start = False
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and play_btn.collidepoint(e.pos):
                    start = True
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        start = True
                    elif e.key == pygame.K_ESCAPE:
                        running = False
                if start:
                    order = new_game()
                    idx, score, picked = 0, 0, None
                    choices = make_choices(order[0]["answer"])
                    state = "ask"
                continue

            choice_idx = None
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if state == "ask":
                    for i, r in enumerate(buttons):
                        if r.collidepoint(e.pos):
                            choice_idx = i
                elif state == "done":
                    if back_btn.collidepoint(e.pos):
                        choice_idx = "next"
                else:
                    choice_idx = "next"
            if e.type == pygame.KEYDOWN:
                if state == "ask" and e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    choice_idx = e.key - pygame.K_1
                elif state != "ask" and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    choice_idx = "next"
                if e.key == pygame.K_ESCAPE:
                    running = False

            if choice_idx is None:
                continue

            if state == "ask" and isinstance(choice_idx, int):
                picked = choice_idx
                if choices[picked] == order[idx]["answer"]:
                    score += 1
                state = "feedback"
            elif state == "feedback":
                idx += 1
                if idx >= len(order):
                    state = "done"
                else:
                    choices = make_choices(order[idx]["answer"])
                    picked = None
                    state = "ask"
            elif state == "done":
                state = "menu"

        # ---------- วาด ----------
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((60, 140, 230))

        if state == "menu":
            draw_text(screen, title_font, "Anime Quiz", (0, 0, 0), (W // 2, H // 2 - 140), True)
            hover = play_btn.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (140, 230, 140) if hover else (255, 255, 255), play_btn, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), play_btn, 4, border_radius=10)
            draw_text(screen, big, "Play", (0, 0, 0), play_btn.center, True)
        elif state == "done":
            draw_text(screen, big, "Finished!", (0, 0, 0), (W // 2, H // 2 - 90), True)
            draw_text(screen, big, f"Score: {score} / {len(order)}", (0, 0, 0), (W // 2, H // 2 - 10), True)
            hover = back_btn.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (140, 230, 140) if hover else (255, 255, 255), back_btn, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), back_btn, 4, border_radius=10)
            draw_text(screen, font, "Back to Menu", (0, 0, 0), back_btn.center, True)
        else:
            q = order[idx]
            poster = posters.get(q["img"])
            if poster:
                screen.blit(poster, (W // 2 - poster.get_width() // 2, 95))
            else:
                box = pygame.Rect(0, 95, *POSTER_BOX)
                box.centerx = W // 2
                pygame.draw.rect(screen, (200, 200, 200), box)
                draw_text(screen, font, f"missing: images/{q['img']}.*", (200, 0, 0), (box.x + 20, box.y + 20))

            draw_text(screen, font, f"Question {idx + 1}/{len(order)}   Score: {score}", (0, 0, 0), (W // 2, 18), True)
            draw_text(screen, big, "Which anime?", (0, 0, 0), (W // 2, 60), True)

            for i, r in enumerate(buttons):
                color = (255, 255, 255)
                if state == "feedback":
                    if choices[i] == q["answer"]:
                        color = (120, 220, 120)
                    elif i == picked:
                        color = (240, 120, 120)
                pygame.draw.rect(screen, color, r, border_radius=8)
                pygame.draw.rect(screen, (0, 0, 0), r, 3, border_radius=8)
                draw_text(screen, font, f"{i + 1}. {choices[i]}", (0, 0, 0), (r.x + 15, r.centery - 12))

            if state == "feedback":
                ok = choices[picked] == q["answer"]
                msg = "Correct!" if ok else f"Wrong! Answer: {q['answer']}"
                draw_text(screen, font, msg, (0, 120, 0) if ok else (180, 0, 0), (W // 2, 775), True)
                draw_text(screen, font, "Click / Space = next", (30, 30, 30), (W // 2, 805), True)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()