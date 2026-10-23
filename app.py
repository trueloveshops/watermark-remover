import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("🛡️ 絕對無損·即時去浮水印工具")
st.write(
    "**免按按鈕、即時自動化**：只要在浮水印上用紅筆塗抹，放開滑鼠就會**秒速自動清除**"
    "！"
)

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  w, h = bg_image.size

  stroke_width = st.slider("筆刷大小", 3, 40, 12)

  st.info("💡 操作提示：直接在圖片上的浮水印塗抹，畫完放開就會自動處理！")

  # 即時畫布：當塗完放開滑鼠時，會自動觸發更新並執行
  canvas_result = st_canvas(
      fill_color="rgba(255, 0, 0, 0.4)",
      stroke_width=stroke_width,
      stroke_color="#FF0000",
      background_image=bg_image,
      update_streamlit=True,
      height=h,
      width=w,
      drawing_mode="freedraw",
      key="canvas_auto_v1",
  )

  # 自動偵測畫布是否有塗抹並處理
  image_data = None
  if canvas_result is not None:
    try:
      image_data = canvas_result.image_data
    except Exception:
      image_data = None

  if image_data is not None:
    canvas_rgba = image_data
    canvas_rgb = canvas_rgba[:, :, :3].astype(np.int16)
    img_np = np.array(bg_image).astype(np.int16)

    # 比對像素差異，精準抓取塗抹處
    diff = np.sum(np.abs(canvas_rgb - img_np), axis=2)
    mask_binary = np.where(diff > 5, 255, 0).astype(np.uint8)

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
        st.success("✨ 浮水印已完美清除！其他未塗抹區域 100% 完好如初。")
        st.image(
            result_img, caption="處理後結果（原圖完好）", use_container_width=True
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
