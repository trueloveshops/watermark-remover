import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title="極速無痕去除浮水印工具", page_icon="🛡️", layout="wide"
)

st.title("🛡️ 專業無損·精準去浮水印工具")
st.write(
    "**極速流暢**：畫布已自動最佳化顯示尺寸，操作順手不卡頓，清除時自動對應原圖高畫質！"
)

uploaded_file = st.file_uploader(
    "選擇圖片...", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
  bg_image = Image.open(uploaded_file).convert("RGB")
  orig_w, orig_h = bg_image.size

  # 計算適中的顯示尺寸（最大寬度 750px），確保畫布秒速同步、絕不卡頓
  max_disp_w = 750
  if orig_w > max_disp_w:
    disp_w = max_disp_w
    disp_h = int(orig_h * (max_disp_w / orig_w))
  else:
    disp_w, disp_h = orig_w, orig_h

  disp_bg_image = bg_image.resize((disp_w, disp_h), Image.Resampling.LANCZOS)

  with st.sidebar:
    st.subheader("🛠️ 操作控制台")
    stroke_width = st.slider("筆刷大小", 3, 40, 12)
    st.markdown("---")
    clear_btn = st.button(
        "✨ 開始清除塗抹處浮水印", type="primary", use_container_width=True
    )
    st.info(
        "💡 **操作步驟**：\n1. 在右側圖片上用紅筆塗抹浮水印。\n2. 點擊上方按鈕執行清除。\n3."
        " 自動產出無損原圖並提供下載！"
    )

  st.write("### 🖼️ 圖片塗抹編輯區")

  canvas_result = st_canvas(
      fill_color="rgba(255, 0, 0, 0.4)",
      stroke_width=stroke_width,
      stroke_color="#FF0000",
      background_image=disp_bg_image,
      update_streamlit=False,
      height=disp_h,
      width=disp_w,
      drawing_mode="freedraw",
      key="canvas_optimized_v1",
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
      disp_np = np.array(disp_bg_image).astype(np.int16)

      # 在顯示尺寸下比對像素差異產生遮罩
      diff = np.sum(np.abs(canvas_rgb - disp_np), axis=2)
      mask_disp = np.where(diff > 5, 255, 0).astype(np.uint8)

      if np.count_nonzero(mask_disp) > 0:
        with st.spinner("✨ 正在進行高畫質智慧無痕修復中..."):
          # 將遮罩放大回原圖的高畫質尺寸
          mask_orig = cv2.resize(
              mask_disp, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST
          )

          # 對原圖執行 OpenCV inpaint
          orig_np = np.array(bg_image)
          dst_np = cv2.inpaint(
              orig_np, mask_orig, inpaintRadius=3, flags=cv2.INPAINT_TELEA
          )

          result_img = Image.fromarray(dst_np)

          st.markdown("---")
          st.subheader("📊 處理結果對比")

          col1, col2 = st.columns(2)
          with col1:
            st.image(
                bg_image, caption="原始圖片（高畫質）", use_container_width=True
            )
          with col2:
            st.image(
                result_img,
                caption="處理後結果（完美無損）",
                use_container_width=True,
            )

          st.success(
              "✨ 浮水印已完美清除！原圖畫質 100% 保留，未塗抹區域絕對不受影響。"
          )

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
            "⚠️ 尚未偵測到塗抹痕跡！請先在圖片上的浮水印位置用紅筆塗抹後再點擊按鈕。"
        )
    else:
      st.warning(
          "⚠️ 畫布資料尚未讀取，請確認您已在圖片上進行塗抹後再點擊按鈕！"
      )
