=======
![picture](https://i.pinimg.com/736x/73/70/c9/7370c9221f25c698bd813de20e8308d8.jpg)

# https://www.instagram.com/reel/DRMTCRBiMDz/?igsh=Z2pnMDM2YmF6c21t
# https://www.instagram.com/reel/DQbTFvBiA9h/?igsh=NXk5ZXhvMTdxdDI5
# 提案一：參數化變形體系與數據視覺化 (Parametric Deformation System and Data Visualization)
此提案著重於運用 compas.geometry 的幾何物件、座標系和轉換矩陣來創造動態的 3D 形體，並使用顏色和大小映射進行數據視覺化。
核心技術與概念：
1. 幾何物件基礎 (Geometry Foundation): 創建基礎點 (cg.Point)、向量 (cg.Vector)、框架 (cg.Frame) 或基礎形狀（例如 cg.Box 或 cg.Sphere）。
2. 變形矩陣應用 (Transformation Application): 使用 cg.Rotation（旋轉）和 cg.Translation（平移） 組合多個 4×4 轉換矩陣 (cg.Transformation) 來對點或整個結構進行複雜的定位和方向調整。
3. 迭代與數據映射 (Iteration and Data Mapping):
    ◦ 利用迴圈結構創建大量的幾何物件（例如，像我們之前討論的三維泡泡圖一樣，創建 5x5x5 的 Sphere 陣列）。
    ◦ 將點或球體的位置座標（X, Y, Z）或其他計算結果映射到其顏色 (compas.colors.Color) 或大小（Sphere 的半徑）上，實現數據的視覺化效果。
可能成果：
• 創建一個「晶格塔」或「參數化群體」：一個由數百個經過不同旋轉、平移和縮放（cg.Scale） 變形的幾何單元組成的複雜 3D 模型。

12/02
![picture](https://i.pinimg.com/736x/b8/87/88/b88788350b14edb632ae944a03616ef0.jpg)
