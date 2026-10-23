import os
import cv2
import gradio as gr
import numpy as np
from PIL import Image


def remove_watermark(dict_input):
  if dict_input is None:
    return None

  # 1. 取得底圖
  bg_img = dict_input["background"].convert("RGB")
  img_np = np.array(bg_img)

  # 2. 取得塗抹圖層 (Mask)
  layers = dict_input.get("layers", [])
  if not layers or len(layers) == 0:
    return bg_img

  mask_layer = layers[0].convert("L")
  mask_np = np.array(mask_layer)

  # 3. 二值化遮罩
  _, mask_binary = cv2.threshold(mask_np, 10, 255, cv2.THRESH_BINARY)

  # 4. 執行無痕修復
  dst_np = cv2.inpaint(
      img_np, mask_binary, inpaintRadius=3, flags=cv2.INPAINT_TELEA
  )
  return Image.fromarray(dst_np)


with gr.Blocks(title="極速無痕去除浮水印") as demo:
  gr.Markdown("# 🛡️ 專業無損·去浮水印工具")
  gr.Markdown(
      "支援**圖片縮放、平移**。直接用筆刷塗抹浮水印，點擊按鈕即可瞬間清除！"
  )

  with gr.Row():
    with gr.Column(scale=2):
      editor = gr.ImageEditor(
          type="pil",
          label="上傳圖片並塗抹（支援縮放、移動、還原）",
          brush=gr.Brush(colors=["#FFFFFF"], default_size=20),
      )
      btn = gr.Button("✨ 點擊清除浮水印", variant="primary", scale=1)
    with gr.Column(scale=2):
      output = gr.Image(label="處理結果（可直接右鍵儲存圖片）")

  btn.click(remove_watermark, inputs=[editor], outputs=[output])

# 自動對應雲端伺服器連接埠，確保穩定運行
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
