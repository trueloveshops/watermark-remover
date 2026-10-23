import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("🛡️ 極速無痕去除浮水印工具")
st.write("上傳圖片後，使用筆刷塗抹浮水印區域，點擊「開始清除」即可！")

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  w, h = bg_image.size

  # 設定塗抹畫布
  stroke_width = st.slider("筆刷大小", 5, 50, 20)

  canvas_result = st_canvas(
      fill_color="rgba(255, 165, 0, 0.3)",
      stroke_width=stroke_width,
      stroke_color="#FFFFFF",
      background_image=bg_image,
      update_streamlit=True,
      height=h,
      width=w,
      drawing_mode="freedraw",
      key="canvas",
  )

  if st.button("✨ 開始清除塗抹處浮水印", type="primary"):
    if canvas_result.image_data is not None:
      # 讀取塗抹的 Mask
      mask = canvas_result.image_data[:, :, 3]
      _, mask_binary = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)

      # 影像修復
      img_np = np.array(bg_image)
      dst_np = cv2.inpaint(
          img_np, mask_binary, inpaintRadius=3, flags=cv2.INPAINT_TELEA
      )

      result_img = Image.fromarray(dst_np)
      st.image(result_img, caption="處理結果", use_column_width=True)
