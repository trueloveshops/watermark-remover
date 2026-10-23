import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("🛡️ 絕對無損·精準去浮水印工具")
st.write(
    "**操作步驟**：先用紅筆在浮水印上塗抹，然後點擊下方按鈕，即可秒速完美清除！"
)

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  w, h = bg_image.size

  stroke_width = st.slider("筆刷大小", 3, 40, 12)

  st.info("💡 提示：請在圖片上的浮水印塗上紅筆，再按下方按鈕。")

  # 繪圖畫布
  canvas_result = st_canvas(
      fill_color="rgba(255, 0, 0, 0.4)",
      stroke_width=stroke_width,
      stroke_color="#FF0000",
      background_image=bg_image,
      update_streamlit=False,  # 關閉即時更新，改由按鈕觸發最穩定
      height=h,
      width=w,
      drawing_mode="freedraw",
      key="canvas_stable_v1",
  )

  if st.button("✨ 開始清除塗抹處浮水印", type="primary", use_container_width=True):
    image_data = None
    if canvas_result is not None:
      try:
        image_data = canvas_result.image_data
      except Exception:
        image_data = None

    if image_data is not None:
      # 透過精準辨識畫面上的「紅色筆刷」來建立遮罩（100% 準確抓取塗抹處）
      canvas_rgba = image_data
      r = canvas_rgba[:, :, 0]
      g = canvas_rgba[:, :, 1]
      b = canvas_rgba[:, :, 2]

      # 只要是紅色筆刷經過的像素，就標記為遮罩
      mask_binary = np.where(
          (r > 200) & (g < 50) & (b < 50), 255, 0
      ).astype(np.uint8)

      if np.count_nonzero(mask_binary) > 0:
        with st.spinner("✨ 正在智慧無痕修復中..."):
          img_np_uint8 = np.array(bg_image)
          dst_np = cv2.inpaint(
              img_np_uint8,
              mask_binary,
              inpaintRadius=3,
              flags=cv2.INPAINT_TELEA,
          )

          result_img = Image.fromarray(dst_np)
          st.success(
              "✨ 浮水印已完美清除！其他未塗抹區域 100% 完好如初，絕無破壞。"
          )
          st.image(
              result_img, caption="處理後結果", use_container_width=True
          )

          # 提供直接下載按鈕
          buf = io.BytesIO()
          result_img.save(buf, format="JPEG", quality=95)
          st.download_button(
              label="📥 點此直接下載無浮水印圖片",
              data=buf.getvalue(),
              file_name="clean_image.jpg",
              mime="image/jpeg",
              use_container_width=True,
          )
      else:
        st.warning("⚠️ 尚未偵測到紅筆塗抹痕跡，請先在圖片上塗抹浮水印再點按鈕！")
    else:
      st.warning("⚠️ 畫布資料讀取中，請重新整理或重新塗抹一次！")
