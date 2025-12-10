# 純內建版市場生成器（不需要安裝任何套件！）
import random
import json
import os
from math import sqrt

# 資料設定（同之前）
stall_types = ['蔬菜','蔬菜','蔬菜','蔬菜','蔬菜',
               '肉','肉','肉',
               '魚','魚',
               '熟食','熟食','熟食','熟食',
               '乾貨','乾貨','乾貨','乾貨','乾貨','乾貨']

sizes = {(3,3):5, (4,3):3, (4,4):2, (3,2):4, (2,2):6}  # 對應上面數量
grid_w, grid_h = 20, 20
drains = [(5,19), (15,19)]
entries = [(0,0), (19,19)]

# 簡單鄰接分數（魚跟熟食互相討厭）
def adj_score(t1, t2):
    if {'魚','熟食'} == {t1,t2}: return -50
    if t1 == t2: return +10
    if {t1,t2} in [{'魚','肉'},{'蔬菜','乾貨'}]: return +15
    return -5

# 放置攤位
def try_place(stalls):
    grid = [[0]*grid_w for _ in range(grid_h)]
    placed = []
    counts = dict(stalls)  # 使用傳入的副本來追蹤剩餘數量
    for i, typ in enumerate(stall_types):
        # 取得下一個尚有數量的尺寸 (w,h)
        try:
            size = next(k for k, v in counts.items() if v > 0)
        except StopIteration:
            return None
        w, h = size
        counts[size] -= 1

        for _ in range(1000):
            x = random.randint(0, grid_w - w)
            y = random.randint(0, grid_h - h)
            if all(grid[y+dy][x+dx] == 0 for dx in range(w) for dy in range(h)):
                for dx in range(w):
                    for dy in range(h):
                        grid[y+dy][x+dx] = i+1
                placed.append({"id": i, "type": typ, "x": x, "y": y, "w": w, "h": h})
                break
        else:
            return None
    return placed, grid

# 計算簡單評分
def score(placed):
    s = 0
    for p in placed:
        cx = p["x"] + p["w"]/2
        cy = p["y"] + p["h"]/2
        # 排水分
        if p["type"] in ["魚","肉"]:
            d = min(sqrt((cx-dx)**2 + (cy-dy)**2) for dx,dy in drains)
            s += d
        # 氣味分
        for q in placed:
            if p["id"] != q["id"]:
                dx = (p["x"]+p["w"]/2) - (q["x"]+q["w"]/2)
                dy = (p["y"]+p["h"]/2) - (q["y"]+q["h"]/2)
                dist = max(sqrt(dx*dx + dy*dy), 1)
                s -= adj_score(p["type"], q["type"]) / dist
    return s

# 產生 30 個
os.makedirs("極簡版結果", exist_ok=True)
best = []
for i in range(30):
    while True:
        result = try_place(dict(sizes))
        if result:
            placed, grid = result
            sc = score(placed)
            best.append((sc, placed, grid))
            print(f"第{i+1:2d}個完成，分數 {sc:.1f}")
            break

best.sort()
for idx, (sc, placed, grid) in enumerate(best[:10]):  # 取前10名
    with open(f"極簡版結果/第{idx+1}_名_分數{sc:.0f}.csv", "w", encoding="utf-8") as f:
        f.write("id,類型,x,y,寬,高\n")
        for p in placed:
            f.write(f"{p['id']},{p['type']},{p['x']},{p['y']},{p['w']},{p['h']}\n")
    
    # 產生超簡單文字圖
    with open(f"極簡版結果/第{idx+1}_名_分數{sc:.0f}.txt", "w", encoding="utf-8") as f:
        legend = "蔬=蔬菜 肉=肉 魚=魚 熟=熟食 乾=乾貨\n"
        f.write(legend + "\n")
        txt = "\n".join("".join("蔬" if c and stall_types[c-1]=="蔬菜" else
                               "肉" if c and stall_types[c-1]=="肉" else
                               "魚" if c and stall_types[c-1]=="魚" else
                               "熟" if c and stall_types[c-1]=="熟食" else
                               "乾" if c and stall_types[c-1]=="乾貨" else "．"
                               for c in row) for row in grid)
        f.write(txt)

print("全部完成！請到「極簡版結果」資料夾看前10名（CSV + 文字平面圖）")