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
    # 安全取得畫布資料，避免未塗抹時崩潰
    image_data = None
    try:
      if canvas_result is not None:
        image_data = canvas_result.image_data
    except Exception:
      pass

    if image_data is not None:
      # 取得塗抹的 Mask
      mask = image_data[:, :, 3]
      _, mask_binary = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)

      if np.count_nonzero(mask_binary) > 0:
        # 影像修復
        img_np = np.array(bg_image)
        dst_np = cv2.inpaint(
            img_np, mask_binary, inpaintRadius=3, flags=cv2.INPAINT_TELEA
        )

        result_img = Image.fromarray(dst_np)
        st.image(result_img, caption="處理結果", use_container_width=True)
      else:
        st.warning("請先在圖片上用筆刷塗抹需要去除的浮水印區域！")
    else:
      st.warning("請先在圖片上進行塗抹，再點擊清除按鈕！")
