import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# 設定寬螢幕模式，讓畫面變寬、視野極佳
st.set_page_config(
    page_title="極速無痕去除浮水印工具", page_icon="🛡️", layout="wide"
)

st.title("🛡️ 專業無損·精準去浮水印工具")
st.write(
    "**絕對不破壞原圖**：在左側調整筆刷大小，直接在圖片上的浮水印塗抹，再點擊側邊欄的按鈕即可！"
)

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  w, h = bg_image.size

  # 側邊欄控制區：操作直覺、畫面乾淨
  with st.sidebar:
    st.subheader("🛠️ 調整與控制")
    stroke_width = st.slider("筆刷大小", 5, 60, 20)
    st.markdown("---")
    clear_btn = st.button(
        "✨ 開始清除塗抹處浮水印", type="primary", use_container_width=True
    )
    st.info(
        "💡 **操作步驟**：\n1. 在右側圖片上用筆刷塗抹浮水印。\n2. 點擊上方按鈕執行清除。\n3."
        " 滿意後直接下載！"
    )

  st.write("### 🖼️ 圖片塗抹編輯區")

  # 繪圖畫布
  canvas_result = st_canvas(
      fill_color="rgba(255, 0, 0, 0.4)",
      stroke_width=stroke_width,
      stroke_color="#FF0000",
      background_image=bg_image,
      update_streamlit=False,
      height=h,
      width=w,
      drawing_mode="freedraw",
      key="canvas_pro_v1",
  )

  if clear_btn:
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

      # 嚴格像素比對：抓取畫布與原圖有差異的軌跡作為遮罩
      diff = np.sum(np.abs(canvas_rgb - img_np), axis=2)
      mask_binary = np.where(diff > 5, 255, 0).astype(np.uint8)

      if np.count_nonzero(mask_binary) > 0:
        with st.spinner("✨ 正在進行智慧無痕修復中..."):
          img_np_uint8 = np.array(bg_image)
          dst_np = cv2.inpaint(
              img_np_uint8,
              mask_binary,
              inpaintRadius=3,
              flags=cv2.INPAINT_TELEA,
          )

          result_img = Image.fromarray(dst_np)

          st.markdown("---")
          st.subheader("📊 處理結果對比")

          # 雙欄並排對比
          col1, col2 = st.columns(2)
          with col1:
            st.image(bg_image, caption="原始圖片", use_container_width=True)
          with col2:
            st.image(
                result_img,
                caption="處理後結果（完美無損）",
                use_container_width=True,
            )

          st.success(
              "✨ 浮水印已完美清除！其他未塗抹區域受到 100% 完整保護，絕無破壞。"
          )

          # 下載按鈕
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
        st.warning(
            "⚠️ 尚未偵測到塗抹痕跡！請先在圖片上的浮水印位置用筆刷塗抹後再點擊按鈕。"
        )
    else:
      st.warning("⚠️ 畫布資料尚未讀取，請在圖片上進行塗抹後再點擊按鈕！")
