# test_capture_pipeline.py
# Teste de pipeline de captura: executa cada etapa, ignora erros, imprime valores de HP/Mana e resumo ao final.

import os
import time
import cv2
from src.utils.core import locate
from src.repositories.inventory.config import images as inv_images

results = []
def record(name, ok, msg=None):
    results.append((name, ok, msg))


def save_image(img, name: str):
    # Salva todas as imagens na pasta 'captures'
    folder = "captures"
    os.makedirs(folder, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"{name}_{ts}.png")
    cv2.imwrite(path, img)

# 1) Full screenshot
try:
    from src.utils.core import getScreenshot
    ss = getScreenshot()
    save_image(ss, "full_screenshot")
    record("full_screenshot", True)
except Exception as e:
    ss = None
    record("full_screenshot", False, str(e))

# 2) Game Window
try:
    from src.repositories.gameWindow.config import gameWindowSizes
    from src.repositories.gameWindow.core import getCoordinate, getImageByCoordinate
    coord = getCoordinate(ss, gameWindowSizes[1080])
    gw = getImageByCoordinate(ss, coord, gameWindowSizes[1080])
    save_image(gw, "gameWindow")
    record("gameWindow", True)
except Exception as e:
    record("gameWindow", False, str(e))

# 3) statsBar
try:
    from src.repositories.statsBar.locators import getStopIconPosition
    stop = getStopIconPosition(ss)
    if stop:
        sb = ss[stop[1]+1:stop[1]+12, stop[0]-117:stop[0]-11]
        save_image(sb, "statsBar")
    record("statsBar", True)
except Exception as e:
    record("statsBar", False, str(e))

# 4) statusBar (HP + Mana)
try:
    from src.repositories.statusBar.locators import getHpIconPosition, getManaIconPosition
    hp = getHpIconPosition(ss)
    mana = getManaIconPosition(ss)
    status_img = None
    if hp and mana:
        x1, y1, w1, h1 = hp
        x2, y2, w2, h2 = mana
        top = min(y1, y2)
        bottom = max(y1 + h1, y2 + h2)
        left = min(x1, x2)
        right = max(x1 + w1, x2 + w2)
        status_img = ss[top:bottom, left:right]
        save_image(status_img, "statusBar")
    record("statusBar", True)
except Exception as e:
    record("statusBar", False, str(e))

# 4.1) Captura das barras HP e Mana
try:
    if hp:
        bar_width = 110
        x, y, w, h = hp
        hp_bar = ss[y:y+h, x+w:x+w+bar_width]
        save_image(hp_bar, "hp_bar")
    if mana:
        bar_width = 110
        x, y, w, h = mana
        mana_bar = ss[y:y+h, x+w:x+w+bar_width]
        save_image(mana_bar, "mana_bar")
    record("statusBarsCapture", True)
except Exception as e:
    record("statusBarsCapture", False, str(e))

# 5) chat (mensagens e abas)
try:
    from src.repositories.chat.core import getChatMessagesContainerPosition, getTabs
    chat_bbox = getChatMessagesContainerPosition(ss)
    if chat_bbox:
        x, y, w, h = chat_bbox
        save_image(ss[y:y+h, x:x+w], "chat_messages")
    tabs = getTabs(ss)
    for tab_name, info in tabs.items():
        xt, yt, wt, ht = info['position']
        save_image(ss[yt:yt+ht, xt:xt+wt], f"chat_tab_{tab_name}")
    record("chat", True)
except Exception as e:
    record("chat", False, str(e))

# 6) actionBar
try:
    from src.repositories.actionBar.locators import getLeftArrowsPosition, getRightArrowsPosition
    left = getLeftArrowsPosition(ss)
    right = getRightArrowsPosition(ss)
    if left and right:
        xl, yl, wl, hl = left
        xr, yr, wr, hr = right
        top = min(yl, yr)
        bottom = max(yl+hl, yr+hr)
        left_x = xl
        right_x = xr + wr
        ab = ss[top:bottom, left_x:right_x]
        save_image(ab, "actionBar")
    record("actionBar", True)
except Exception as e:
    record("actionBar", False, str(e))

# 7) skills
try:
    from src.repositories.skills.locators import getSkillsIconPosition
    sk = getSkillsIconPosition(ss)
    if sk:
        xs, ys, ws, hs = sk
        save_image(ss[ys:ys+hs, xs:xs+ws], "skills")
    record("skills", True)
except Exception as e:
    record("skills", False, str(e))

# 8) battleList (usa extractor)
try:
    from src.repositories.battleList.extractors import getContent as getBattleListContent
    bl = getBattleListContent(ss)
    if bl is not None:
        save_image(bl, "battleList")
    record("battleList", True)
except Exception as e:
    record("battleList", False, str(e))

# 9) radar (usa extractor)
try:
    from src.repositories.radar.locators import getRadarToolsPosition
    from src.repositories.radar.extractors import getRadarImage
    tools_bbox = getRadarToolsPosition(ss)
    if tools_bbox:
        radar_img = getRadarImage(ss, tools_bbox)
        save_image(radar_img, "radar")
    record("radar", True)
except Exception as e:
    record("radar", False, str(e))

# 10) refill (trade window)
try:
    from src.repositories.refill.core import getTradeTopPosition, getTradeBottomPos
    top = getTradeTopPosition(ss)
    bottom = getTradeBottomPos(ss)
    if top and bottom:
        xt, yt, wt, ht = top
        _, yb, _, _ = bottom
        refill_img = ss[yt:yb, xt:xt+wt]
        save_image(refill_img, "refill")
    record("refill", True)
except Exception as e:
    record("refill", False, str(e))

# 11) inventory (slots grid crop)
try:
    bboxes = []
    for slot_img in inv_images['slots'].values():
        pos = locate(ss, slot_img)
        if pos:
            bboxes.append(pos)
    if bboxes:
        xs = [x for x,_,w,_ in bboxes] + [x+w for x,_,w,_ in bboxes]
        ys = [y for _,y,_,h in bboxes] + [y+h for _,y,_,h in bboxes]
        left, right = min(xs), max(xs)
        top, bottom = min(ys), max(ys)
        inv_img = ss[top:bottom, left:right]
        save_image(inv_img, "inventory")
    record("inventory", True)
except Exception as e:
    record("inventory", False, str(e))

# 12) status percentages (HP & Mana)
try:
    from src.repositories.statusBar.core import getHpPercentage, getManaPercentage
    hp_pct = getHpPercentage(ss)
    mana_pct = getManaPercentage(ss)
    print(f"Detected HP%: {hp_pct}")
    print(f"Detected Mana%: {mana_pct}")
    record("statusPercentages", True, f"HP%={hp_pct}, Mana%={mana_pct}")
except Exception as e:
    record("statusPercentages", False, str(e))

# resumo final
if __name__ == "__main__":
    print("\n=== Resumo das capturas ===")
    for name, ok, msg in results:
        status = "OK" if ok else f"FALHOU: {msg}"
        print(f"- {name}: {status}")
