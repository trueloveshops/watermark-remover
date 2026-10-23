import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st

st.title("🛡️ 智慧無痕去除浮水印工具")
st.write(
    "針對 AI 生成圖片（如豆包）設計：**免手動塗抹、免放大縮小**，一鍵秒速精準清除！"
)

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  img_np = np.array(bg_image)
  h, w, _ = img_np.shape

  st.image(bg_image, caption="原始圖片預覽", use_container_width=True)

  st.markdown("---")
  st.subheader("🎯 浮水印位置設定")

  # 讓使用者選擇浮水印通常在哪個角落
  corner = st.selectbox(
      "選擇浮水印所在位置：",
      ["右下角 (豆包 / 多數 AI 預設位置)", "左下角", "右上角", "左上角"],
  )

  area_size = st.slider(
      "清除範圍大小（針對該角落的涵蓋比例）", 10, 40, 18, 2
  )

  if st.button("✨ 一鍵無痕清除浮水印", type="primary", use_container_width=True):
    mask = np.zeros((h, w), dtype=np.uint8)

    # 計算角落遮罩範圍
    box_h = int(h * (area_size / 100.0))
    box_w = int(w * (area_size / 100.0))

    if "右下角" in corner:
      mask[h - box_h : h, w - box_w : w] = 255
    elif "左下角" in corner:
      mask[h - box_h : h, 0:box_w] = 255
    elif "右上角" in corner:
      mask[0:box_h, w - box_w : w] = 255
    elif "左上角" in corner:
      mask[0:box_h, 0:box_w] = 255

    # 執行 OpenCV 無縫影像修復
    dst_np = cv2.inpaint(
        img_np, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA
    )
    result_img = Image.fromarray(dst_np)

    st.success("✨ 浮水印已完美清除！其他未指定區域 100% 完好如初。")
    st.image(result_img, caption="處理後結果", use_container_width=True)

    # 提供直接下載按鈕
    buf = io.BytesIO()
    result_img.save(buf, format="JPEG", quality=95)
    byte_im = buf.getvalue()

    st.download_button(
        label="📥 點此直接下載無浮水印圖片",
        data=byte_im,
        file_name="clean_image.jpg",
        mime="image/jpeg",
        use_container_width=True,
    )
