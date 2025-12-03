import compas
import compas.geometry as cg
import argparse
import random
# 為了視覺化結果，可能還需要 compas_viewer
from compas_viewer import Viewer

def create_conceptual_bookshelf(book_dimensions, gap=0.02, random_gaps=True, gap_min=0.01, gap_max=0.05):
    """
    輸入數個書本的長寬高，生成排列好的長方體幾何物件 (作為書架上的書)。

    Args:
        book_dimensions (list of tuples/lists): 每個元素是 (長L, 寬W, 高H)。
        gap (float): 固定間隙（當 random_gaps=False 時使用）。
        random_gaps (bool): 若 True 則每本書之間的間隙以隨機值取代。
        gap_min, gap_max (float): 隨機間隙的範圍（包含端點）。

    Returns:
        tuple: (list_of_boxes, list_of_gaps)
               list_of_boxes 為已定位的 cg.Box 物件列表。
               list_of_gaps 為每本書之後使用的間隙值 (最後一本之後的間隙為 None)。
    """
    bookshelf_geometries = []
    gaps = []
    current_x_position = 0.0  # 用於追蹤下一本書沿 X 軸擺放的起始位置

    n = len(book_dimensions)
    for i, (L, W, H) in enumerate(book_dimensions):
        book_box = cg.Box(L, W, H, frame=cg.Frame.worldXY())

        tx = current_x_position + L / 2
        ty = W / 2
        tz = H / 2
        translation_vector = [tx, ty, tz]
        T = cg.Translation.from_vector(translation_vector)
        book_box.transform(T)

        bookshelf_geometries.append(book_box)

        # 如果不是最後一本，決定並記錄本次使用的間隙，然後更新位置
        if i < n - 1:
            if random_gaps:
                # 保證 gap_min <= gap_max
                lo, hi = (gap_min, gap_max) if gap_min <= gap_max else (gap_max, gap_min)
                current_gap = random.uniform(lo, hi)
            else:
                current_gap = gap
            gaps.append(current_gap)
            current_x_position += L + current_gap
        else:
            gaps.append(None)  # 最後一本之後沒有間隙

    return bookshelf_geometries, gaps

# --- 使用範例 ---
# 假設我們有三本書的尺寸 (長度 L, 寬度 W, 高度 H)
# 單位可以是米或任何一致的單位
input_book_sizes = [
    (0.2, 0.3, 0.25), # 書本 1 (長 0.3, 寬 0.2, 高 0.25)
    (0.2, 0.4, 0.3),  # 書本 2
    (0.2, 0.25, 0.2),
    (0.2, 0.35, 0.28)
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成概念性書架並可自訂書本間隙 (gap)")
    parser.add_argument("--gap", type=float, default=0.02, help="固定間隙 (預設 0.02)")
    parser.add_argument("--random-gaps", action="store_true", help="若啟用則每個間隙為隨機值")
    parser.add_argument("--gap-min", type=float, default=0.01, help="隨機間隙最小值 (預設 0.01)")
    parser.add_argument("--gap-max", type=float, default=0.05, help="隨機間隙最大值 (預設 0.05)")
    args = parser.parse_args()

    if args.random_gaps:
        bookshelf, gaps = create_conceptual_bookshelf(input_book_sizes,
                                                      random_gaps=True,
                                                      gap_min=args.gap_min,
                                                      gap_max=args.gap_max)
    else:
        bookshelf, gaps = create_conceptual_bookshelf(input_book_sizes, gap=args.gap)

    print(f"概念性書架空間生成完成（random_gaps={args.random_gaps}）:")
    for i, book in enumerate(bookshelf):
        L, W, H = input_book_sizes[i]
        # Box 的 frame.point 是其中心點
        print(f"Book {i+1} (L={L}, W={W}, H={H}) 的中心點位置: {book.frame.point}  — gap after: {gaps[i]}")

    # 視覺化 (需要安裝 compas_viewer)
    try:
        from compas_viewer import Viewer
    except Exception as e:
        print("compas_viewer not available:", e)
    else:
        viewer = Viewer()
        # add each box individually (Viewer.scene.add() expects single items)
        for book in bookshelf:
            viewer.scene.add(book)
        viewer.show()