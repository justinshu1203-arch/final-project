import compas
import compas.geometry as cg
# 為了視覺化結果，可能還需要 compas_viewer
# from compas_viewer import Viewer

def create_conceptual_bookshelf(book_dimensions):
    """
    輸入數個書本的長寬高，生成排列好的長方體幾何物件 (作為書架上的書)。

    Args:
        book_dimensions (list of tuples/lists): 每個元素是 (長L, 寬W, 高H)。
                                               在這裡，我們假設 長=X軸尺寸, 寬=Y軸尺寸, 高=Z軸尺寸。

    Returns:
        list: 包含所有已定位書本的 cg.Box 物件列表。
    """
    bookshelf_geometries = []
    current_x_position = 0.0  # 用於追蹤下一本書沿 X 軸擺放的起始位置

    # 迭代處理每一本書的尺寸
    for L, W, H in book_dimensions:
        # 1. 創建一個 Box 物件 (表示單本書)
        # 注意：compas.geometry.Box 的簽名為 (xsize, ysize, zsize, frame=...)
        book_box = cg.Box(L, W, H, frame=cg.Frame.worldXY())

        # 2. 計算位移向量 (Translation Vector)
        tx = current_x_position + L / 2
        ty = W / 2
        tz = H / 2

        translation_vector = [tx, ty, tz]

        # 創建位移變換 (Translation) 物件
        T = cg.Translation.from_vector(translation_vector)

        # 3. 應用變換
        book_box.transform(T)

        # 4. 儲存結果
        bookshelf_geometries.append(book_box)

        # 5. 更新下一個書本的起始位置
        current_x_position += L # 下一本書從當前書本的結束位置開始

    return bookshelf_geometries

# --- 使用範例 ---
# 假設我們有三本書的尺寸 (長度 L, 寬度 W, 高度 H)
# 單位可以是米或任何一致的單位
input_book_sizes = [
    (0.3, 0.2, 0.25), # 書本 1 (長 0.3, 寬 0.2, 高 0.25)
    (0.4, 0.2, 0.3),  # 書本 2
    (0.25, 0.2, 0.2),
    (0.35, 0.2, 0.28)
]

bookshelf = create_conceptual_bookshelf(input_book_sizes)

print("概念性書架空間生成完成：")
for i, book in enumerate(bookshelf):
    L, W, H = input_book_sizes[i]
    # Box 的 frame.point 是其中心點
    print(f"Book {i+1} (L={L}, W={W}, H={H}) 的中心點位置: {book.frame.point}")

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