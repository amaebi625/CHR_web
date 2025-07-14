import streamlit as st
import numpy as np
import torch
from PIL import Image
import cv2
import os
import io
import h5py
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import base64

def set_background(image_path):
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background: 
            linear-gradient(rgba(250, 245, 255, 0.4), rgba(250, 245, 255, 0.4)),
            url("data:image/png;base64,{data}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(BASE_DIR, "..", "image", "heart.png")
set_background(bg_path)
# 添加到页面顶部（在 set_page_config 之后，页面其他元素之前）

# --------------------
# 页面设置
# --------------------
st.set_page_config(page_title="CMR图像分割系统", page_icon="🫀", layout="centered")
st.markdown("""
<style>
/* 1. 让页面内容最大宽度变宽 */
main .block-container {
    max-width: 1200px !important;
    padding-left: 2rem;
    padding-right: 2rem;
}
/* 全局字体设定 */
html, body, [class*="css"] {
    color: #4A6C8C;
    font-family: 'Segoe UI', sans-serif;
}


/* 内部上传框本体 */
div[data-testid="stFileUploader"] section {
    background-color: rgba(235, 215, 255, 0.05);
    border: 1.5px dashed rgba(100, 50, 140, 0.6);
    border-radius: 12px;
    padding: 1rem;
}

/* 上传按钮 “Browse files” */
div[data-testid="stFileUploader"] button {
    background-color: rgba(225, 215, 250, 0.65);
    border: 1px solid rgba(120, 90, 160, 1);
    box-shadow: 0 4px 12px rgba(120, 90, 160, 0.15);
    border-radius: 8px;
    color: #3F3C5C;
}

/* 输入栏（用于当前选项展示） */
div[data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1.5px dashed rgba(100, 50, 140, 0.6) !important; /* 深紫色边框 */
    border-radius: 8px !important;
}

/* 下拉项菜单 */
ul[role="listbox"] {
    background-color: rgba(255, 255, 255, 0) !important;
    border: 1px solid rgba(180, 160, 220, 0.3);
    backdrop-filter: blur(5px);
}

/* 下拉选项文字 */
ul[role="listbox"] li {
    color: #3F3C5C !important;
}
.main-title {
        color: #3F3C5C;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
.sub-title {
    color: #e63946;
    font-size: 1.2rem;
    text-align: center;
    margin-bottom: 2rem;
}
/* 🌕 侧边栏背景色（浅米黄） */
    section[data-testid="stSidebar"] {
        background-color: #fff9e5 !important;
        width: 300px !important; 
    }
    /* 增大左侧边栏文字大小 */
    [data-testid="stSidebar"] .css-pkbazv, [data-testid="stSidebar"] .css-uc76bn,
    [data-testid="stSidebar"] a, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li, [data-testid="stSidebar"] ul,
    [data-testid="stSidebar"] .css-eczf16, [data-testid="stSidebar"] .css-jcn9zf {
        font-size: 26px !important; /* 字体大小从18px增加到26px */
        font-weight: 500 !important;
        color: #99c8f0!important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
    }
    
    /* 增强边栏项目的悬停效果 */
    [data-testid="stSidebar"] a:hover, [data-testid="stSidebar"] li:hover {
        background-color: rgba(255,255,255,0.2) !important;
        border-radius: 5px !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🫀 CMR图像自动分割系统</h1>", unsafe_allow_html=True)
st.markdown("<h6 class='sub-title'>上传 CMR 图像，自动获取左心室（LV）、心肌（MYO）、右心室（RV）分割结果</h6>", unsafe_allow_html=True)
st.markdown("---")

if 'show_result' not in st.session_state:
    st.session_state['show_result'] = False
if 'pred_mask' not in st.session_state:
    st.session_state['pred_mask'] = None
if 'image_np' not in st.session_state:
    st.session_state['image_np'] = None

# --------------------
# 上传图像 + 参数设置（横向布局）
# --------------------
with st.container():
    col1, col2 = st.columns([1.5, 1.2])  # 左宽右窄，更自然

    with col1:
        st.markdown("### 📤 上传图像（.h5 格式）")
        uploaded_file = st.file_uploader("请上传一张二维灰度 Cine MRI 图像（.h5 格式）", type=["h5"])
    with col2:
        st.markdown("### ⚙️ 分割参数设置")
        model_choice = st.selectbox("选择分割模型", ["UNet"])
        st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)
# --------------------
# 模型加载（带缓存）: Keras 版本
# --------------------
def load_model(model_path):
    return tf.keras.models.load_model(model_path)

# --------------------
# 读取单张 h5 图像（支持2D/3D）
# --------------------
def load_h5_data(file_obj, is_training=False, target_size=(256, 256), normalize=True):
    images = []

    if isinstance(file_obj, str):
        f = h5py.File(file_obj, 'r')
    else:
        f = h5py.File(file_obj, 'r')  # Streamlit UploadedFile or BytesIO

    with f:
        image = f['image'][:]

        if image.ndim == 3:
            for idx in range(image.shape[0]):
                slice_img = image[idx][..., np.newaxis]
                slice_img = tf.image.resize(slice_img, target_size, method='bilinear').numpy()
                if normalize:
                    slice_img /= np.max(slice_img) + 1e-8
                images.append(slice_img)
            return images, None

        elif image.ndim == 2:
            image = image[..., np.newaxis]
            image = tf.image.resize(image, target_size, method='bilinear').numpy()
            if normalize:
                image /= np.max(image) + 1e-8
            return image, None
        else:
            raise ValueError(f"Unsupported image shape: {image.shape}")

# --------------------
# 模型推理
# --------------------
def run_inference(image_np, model_path):
    if image_np.ndim != 3:
        raise ValueError("Input image must be a single (H, W, 1) array.")

    input_tensor = np.expand_dims(image_np, axis=0)
    model = load_model(model_path)

    pred_logits = model.predict(input_tensor)
    pred_softmax = tf.nn.softmax(pred_logits, axis=-1).numpy()[0]
    pred_mask = np.argmax(pred_softmax, axis=-1)

    return pred_softmax, pred_mask

# --------------------
# 可视化三图合一：原图、掩码、叠加图
# --------------------
def visualize_three(image_np, mask, save_path=None, use_streamlit=True):
    """
    显示并可选择保存三联图（原图/掩码/叠加）
    参数:
        image_np: (H, W, 1) numpy array
        mask:     (H, W)   numpy array
        save_path: 若指定，将保存为 PNG
        use_streamlit: 若为 True，使用 st.pyplot 显示
    """
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))

    axs[0].imshow(image_np[:, :, 0], cmap="gray")
    axs[0].set_title("Original")
    axs[0].axis("off")

    axs[1].imshow(mask, cmap="jet", vmin=0, vmax=np.max(mask))
    axs[1].set_title("Predicted Mask")
    axs[1].axis("off")

    axs[2].imshow(image_np[:, :, 0], cmap="gray")
    axs[2].imshow(mask, cmap="jet", alpha=0.5, vmin=0, vmax=np.max(mask))
    axs[2].set_title("Overlay")
    axs[2].axis("off")

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.show()

# --------------------
# 伪彩色掩码保存函数
# --------------------
def save_mask_as_colormap(mask):
    color_mask = (plt.cm.jet(mask / max(1, mask.max()))[:, :, :3] * 255).astype(np.uint8)
    out_buf = io.BytesIO()
    Image.fromarray(color_mask).save(out_buf, format="PNG")
    out_buf.seek(0)
    return out_buf
# --------------------
# 图像预览与模型推理
# --------------------
if uploaded_file:
    try:
        image_np, _ = load_h5_data(uploaded_file)
        center_col = st.columns([1, 2, 1])[1]
        with center_col:
            st.image(image_np[:, :, 0], caption="🖼️ 上传图像预览", width=300, clamp=True)

        if st.button("🧠 执行自动分割", use_container_width=True):
            with st.spinner("模型正在处理图像，请稍候..."):
                image_np = image_np / np.max(image_np)
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(BASE_DIR, "..", "config", "duck_net_model.h5")

                _, pred_mask = run_inference(image_np, model_path)

                # 状态缓存
                st.session_state['show_result'] = True
                st.session_state['pred_mask'] = pred_mask
                st.session_state['image_np'] = image_np

    except Exception as e:
        st.error(f"❌ 图像处理失败：{e}")

# --------------------
# 结果展示 + 下载按钮
# --------------------
if st.session_state['show_result']:
    pred_mask = st.session_state['pred_mask']
    image_np = st.session_state['image_np']

    st.markdown("### 🧾 分割结果展示")
    st.markdown("**颜色 ↔ 解剖结构对照表（Jet伪彩色映射）：**", unsafe_allow_html=True)

    color_legend_html = """
    <style>
    .color-circle {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 8px;
        border: 1px solid #666;
    }
    </style>

    <ul style="list-style: none; padding-left: 0;">
    <li><span class="color-circle" style="background-color: #000080;"></span> 背景（Background）</li>
    <li><span class="color-circle" style="background-color: #00FFFF;"></span> 右心室（RV）</li>
    <li><span class="color-circle" style="background-color: #FFFF00;"></span> 心肌层（MYO）</li>
    <li><span class="color-circle" style="background-color: #B22222;"></span> 左心室（LV）</li>
    </ul>
    """
    st.markdown(color_legend_html, unsafe_allow_html=True)

    visualize_three(image_np, pred_mask)

    st.markdown("### 📥 下载分割结果")

    normed_mask = pred_mask.astype(np.float32)
    normed_mask /= (np.max(normed_mask) + 1e-8)
    color_mask = (cm.jet(normed_mask)[:, :, :3] * 255).astype(np.uint8)

    out_buf = io.BytesIO()
    Image.fromarray(color_mask).save(out_buf, format="PNG")
    out_buf.seek(0)

    dl_col = st.columns([1, 2, 1])[1]
    with dl_col:
        st.download_button(
            label="⬇️ 下载伪彩色掩码",
            data=out_buf.getvalue(),
            file_name="分割结果.png",
            mime="image/png",
            use_container_width=True
        )

# --------------------
# 页面跳转按钮（了解CMR）
# --------------------
st.markdown(
    """
    <div style='display: flex; justify-content: center; margin-top: 30px;'>
        <a href="/CMR_Info" target="_self">
            <button style="
                background-color: #0072C6;
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 18px;
                border-radius: 10px;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            ">
                📖 点击了解 CMR 与冠心病评估原理
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------
# 底部信息
# --------------------
st.markdown("---")
with st.expander("ℹ️ 关于本系统", expanded=False):
    st.markdown("""
    - **任务目标**：自动分割 Cine MRI 图像中的左心室（LV）、心肌层（MYO）与右心室（RV）区域  
    - **模型架构**：基于 ACDC 数据集训练的 U‑Net 系列结构  
    - **开发团队**：同济大学生物信息学团队（F组）  
    """)
