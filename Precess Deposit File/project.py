
import compas.geometry as cg
# 為了視覺化結果，可能還需要 compas_viewer
from compas_viewer import Viewer

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
        # cg.Box 是從一個 Frame 和尺寸 (xsize, ysize, zsize) 創建的
        # 我們先在世界座標系 (Frame.worldXY()) 創建一個以原點為中心的 Box。
        # 注意：cg.Box(xsize, ysize, zsize, frame) 創建的 Box，其尺寸是 (xsize, ysize, zsize)，Frame 定義了 Box 的中心位置和方向。
        
        # 由於 Box 構造函數需要知道尺寸和中心 Frame，
        # 這裡的 L, W, H 即為 xsize, ysize, zsize
        book_box = cg.Box(L, W, H, cg.Frame.worldXY())

        # 2. 計算位移向量 (Translation Vector)
        # 我們將書本沿著 X 軸排列。
        # 為了讓書本的左邊緣從 current_x_position 開始，我們需要將 Box 的中心 (x, y, z) 位移：
        # X 位移: current_x_position + L / 2
        # Y 位移: W / 2 (讓書本底部對齊 Y=0)
        # Z 位移: H / 2 (讓書本底部對齊 Z=0)
        
        tx = current_x_position + L / 2
        ty = W / 2
        tz = H / 2
        
        translation_vector = [tx, ty, tz]
        
        # 創建位移變換 (Translation) 物件
        T = cg.Translation.from_vector(translation_vector)
        
        # 3. 應用變換
        # 變換 (Transformation) 可以應用於幾何物件，使用 .transform() 方法
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
    (0.25, 0.2, 0.2)  # 書本 3
]

bookshelf = create_conceptual_bookshelf(input_book_sizes)

print("概念性書架空間生成完成：")
for i, book in enumerate(bookshelf):
    # Box 的 frame.point 是其中心點
    print(f"Book {i+1} (L={input_book_sizes[i]}, W={input_book_sizes[i]}, H={input_book_sizes[i]}) 的中心點位置: {book.frame.point}")

# 視覺化 (需要安裝 compas_viewer)
viewer = Viewer()
viewer.scene.add(bookshelf)
viewer.show()