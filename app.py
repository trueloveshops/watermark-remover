import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("🛡️ 絕對無損·精準去浮水印工具")
st.write(
    "**絕對不破壞原圖**：只有用筆刷「親手塗抹」的地方會被清除，其他所有未塗抹區域"
    " 100% 完好保留！"
)

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  w, h = bg_image.size

  stroke_width = st.slider("筆刷大小", 3, 40, 12)

  st.info("💡 操作提示：請直接在圖片上的浮水印位置用筆刷精準塗抹。")

  # 繪圖畫布
  canvas_result = st_canvas(
      fill_color="rgba(255, 0, 0, 0.4)",
      stroke_width=stroke_width,
      stroke_color="#FF0000",
      background_image=bg_image,
      update_streamlit=True,
      height=h,
      width=w,
      drawing_mode="freedraw",
      key="canvas_safe_v2",
  )

  if st.button("✨ 精準清除塗抹處（保證其他區域絕對不動）", type="primary"):
    if canvas_result is not None and canvas_result.image_data is not None:
      canvas_rgba = canvas_result.image_data
      canvas_rgb = canvas_rgba[:, :, :3].astype(np.int16)
      img_np = np.array(bg_image).astype(np.int16)

      # 嚴格像素比對：只有畫布上有被筆刷畫過（與原圖像素不同）的地方才會成為遮罩
      diff = np.sum(np.abs(canvas_rgb - img_np), axis=2)
      mask_binary = np.where(diff > 5, 255, 0).astype(np.uint8)

      if np.count_nonzero(mask_binary) > 0:
        img_np_uint8 = np.array(bg_image)
        # 影像修復（inpaintRadius 設小，確保修復邊緣極致精細）
        dst_np = cv2.inpaint(
            img_np_uint8,
            mask_binary,
            inpaintRadius=3,
            flags=cv2.INPAINT_TELEA,
        )

        result_img = Image.fromarray(dst_np)
        st.success("✨ 處理完成！已精準去除浮水印，未塗抹區域受到 100% 保護。")
        st.image(
            result_img, caption="處理後結果（原圖完好）", use_container_width=True
        )
      else:
        st.warning("⚠️ 請先在圖片上的浮水印位置用筆刷塗抹！")
    else:
      st.warning("⚠️ 請先進行塗抹後再點擊清除按鈕！")
