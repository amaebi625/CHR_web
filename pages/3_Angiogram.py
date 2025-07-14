import streamlit as st
from PIL import Image
import torch
import torchvision.transforms as T
import pandas as pd
import base64
import os
import sys
from pathlib import Path
# 导入utils模块
from utils.inference_single import run_inference_on_image
import streamlit.components.v1 as components

# 获取当前文件所在目录（pages目录）
current_dir = Path(__file__).parent
# 获取项目根目录（pages的父目录）
root_dir = current_dir.parent
# 将根目录添加到Python路径
model_path = os.path.join(root_dir, "config", "faster_rcnn.pth")


def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def get_base64_background(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_image = get_base64_background("data/images/bk.png")

# 页面配置
st.set_page_config(page_title="看懂我的冠脉造影", layout="wide", page_icon="👀")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>
.left-title {
    text-align: right;
    padding-right: 20px;
}
.right-title {
    text-align: left;
    padding-left: 20px;
} 
* 🌕 侧边栏背景色（浅米黄） */
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
/* 优化悬浮系统 */
.hover-wrapper {
    position: relative;
    display: flex;
    justify-content: flex-end;  /* 左栏右对齐 */
    margin-bottom: 1.5rem;
}
.hover-title {
    color: #5a4dbb;
    font-weight: 600;
    font-size: 1.15rem;  /* 保持字体大小不变 */
    cursor: pointer;
    padding: 0.1rem 1rem;  /* 增加内边距使块变大 */
    border-radius: 18px;
    display: inline-block;
    transition: all 0.25s ease;
    background: linear-gradient(to right, #c5c3da, #d5e2f9);
    box-shadow: 0 2px 5px rgba(90, 77, 187, 0.1);
    line-height: 3.5;  /* 调整行高 */
    min-width: 120px;  /* 可选：设置最小宽度 */
}
.hover-title:hover {
    background: linear-gradient(to right, #d5e2f9, #c5c3da);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(90, 77, 187, 0.15);
}
.hover-card {
    display: none;
    position: absolute;
    z-index: 1000;
    width: 600px;
    border: 1px solid #d1d0e6;
    border-radius: 12px;
    padding: 1.5rem;
    background: linear-gradient(to bottom, #ffffff, #f8f8fd);
    box-shadow: 0 6px 25px rgba(90, 77, 187, 0.2);
    left: 0 !important;  /* 左栏卡片从右弹出 */
    right: auto !important;
    top: calc(100% + 5px);
    backdrop-filter: blur(2px);
}
.hover-wrapper:hover .hover-card {
    display: block;
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.hover-card p {
    color: #3f3683;
    line-height: 1.6;
    font-weight: bold;
}
.hover-card b {
    color: black;
}
.hover-card ul {
    padding-left: 1.8rem;
    margin: 0.4rem 0;
}
.hover-card li {
    margin-bottom: 0.1rem;
    color: #555;
}
.hover-card h5 {
    margin-bottom: 0.1rem;
    color: #3f3683;
}
@media (max-width: 768px) {
    .hover-card {
        width: 85vw;
        right: 0;
        left: auto;
        padding: 1rem;
    }
}

.right-hover-wrapper {
    position: relative;
    display: flex;
    left: 20px !important;  /* 右栏卡片从左弹出 */
    right: auto !important;
    justify-content: flex-end; /* 右对齐 */
    margin-bottom: 1.5rem;
}

/* 右栏悬浮卡片 */
.right-hover-card {
    display: none;
    position: absolute;
    z-index: 1000;
    width: 600px;
    border: 1px solid #d1d0e6;
    border-radius: 12px;
    padding: 1.5rem;
    background: linear-gradient(to bottom, #ffffff, #f8f8fd);
    box-shadow: 0 6px 25px rgba(90, 77, 187, 0.2);
    right: 0px !important;  /* 右栏卡片从左弹出 */
    left: auto !important;
    top: calc(100% + 5px);
    backdrop-filter: blur(2px);
}
            
.right-hover-wrapper:hover .right-hover-card {
    display: block;
    animation: fadeIn 0.3s ease-out;
}

.right-hover-wrapper {
    position: relative;
    display: flex;
    justify-content: flex-start;  /* 右栏左对齐 */
    margin-bottom: 1.5rem;
}         

.right-hover-card h5 {
    margin-bottom: 0.1rem;
    color: #3f3683;
}
            
/* 移动端适配 */
@media (max-width: 768px) {
    .right-hover-card {
        width: 85vw;
        left: 0; /* 移动端恢复左对齐 */
        right: auto;
    }
}
            
/* 3D模型容器居中 */
.model-container {
    display: flex;
    justify-content: center;
    height: 100%;
}
            
/* 保持原有时间线样式 */
.timeline {
    position: relative;
    max-width: 950px;
    margin: 0 auto;
}
.timeline::after {
    content: '';
    position: absolute;
    width: 4px;
    background: linear-gradient(to bottom, #d5d2f0, #a59feb);
    top: 0;
    bottom: 0;
    left: 35px;
    margin-left: -2px;
    border-radius: 2px;
}
.container {
    display: flex;
    background: linear-gradient(to right, #f5f4fd, #f0effa);
    border-radius: 12px;
    padding: 1rem;
    padding-left: 60px;
    margin: 15px 0;
    box-shadow: 0 3px 10px rgba(90, 77, 187, 0.1);
    position: relative;
    border: 1px solid #dcdaf4;
}
.container::before {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    left: 25px;
    top: 20px;
    background: white;
    border: 4px solid #7a6fdf;
    border-radius: 50%;
    z-index: 1;
}
.text-col h5 {
    margin-top: 0;
    color: #3f3683;
    font-weight: 600;
    font-size: 1.1rem;
}
.text-col ul {
    padding-left: 2rem;
    margin-top: 0.5rem;
}
.text-col ul li {
    margin-bottom: 0.5rem;
    line-height: 1.2;
    color: #4a4a6a;
}

.title-section {
    margin-bottom: 2rem;
    text-align: center;
}
.subtitle {
    color: #666;
    font-size: 1.1rem;
    max-width: 800px;
    margin: 0 auto;
    line-height: 1.6;
    position: relative;
}
.subtitle::before, .subtitle::after {
    content: "◆";
    color: #a59feb;
    font-size: 0.8rem;
    margin: 0 0.8rem;
    position: relative;
    top: -3px;
}
            
.divider-container {
    margin: 1.5rem 0;
    position: relative;
}
.wave-divider {
    height: 5px;
    background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" fill="%235a4dbb" opacity=".25"/></svg>');
    background-size: cover;
    width: 100%;
}
.diamond-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    background: white;
    padding: 0 1rem;
}
.diamond {
    width: 10px;
    height: 10px;
    background: #5a4dbb;
    transform: rotate(45deg);
    margin: 0 5px;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
    <div class="title-section">
        <h1>👀 看懂我的冠脉造影</h1>
        <p class="subtitle">
            通过AI图像识别与医学科普，帮助您全面了解冠状动脉造影的检查流程与临床意义
        </p>
        <div class="divider-container">
            <div class="wave-divider"></div>
            <div class="diamond-center">
                <div class="diamond"></div>
                <div class="diamond"></div>
                <div class="diamond"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)  # 加空行

# 获取所有需要的图片base64编码
img_base64_1 = get_image_base64("data/images/image5.png")
img_base64_2 = get_image_base64("data/images/image6.png")
img_base64_4 = get_image_base64("data/images/image7.png")
img_base64_5 = get_image_base64("data/images/image8.png")

col_left, col_center,col_right = st.columns([0.8, 0.9, 0.8]) 

# ============= 左栏：三个悬浮卡片 =============
with col_left:
    # 卡片1：什么是冠状动脉造影
    st.markdown("""
    <div class="left-title">
        <h3 style='font-size: 24px; font-weight: bold;'>📌 什么是冠状动脉造影</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hover-wrapper">
        <div class="hover-title">What Is Coronary Angiography? 🖱️</div>
        <div class="hover-card">
            <div style="display: flex;">
                <div style="flex: 3; padding-right: 1rem;">
                    <p style='font-weight: bold;'>
                    冠状动脉造影（Coronary Angiography）是一种用于检查心脏供血血管（冠状动脉）状态的影像学检查方法，属于有创性心导管术的一部分。
                    </p>
                    <ul style='margin-top: 10px;'>
                        <li>借助X线与对比剂显影技术，可 <b>直观显示冠状动脉的走形与病变</b></li>
                        <li>判断血管是否存在 <b>斑块沉积、狭窄或闭塞情况</b></li>
                        <li>造影图像称为 <b>冠脉造影图（Angiogram）</b>，是评估冠心病严重程度的 <b>金标准</b></li>
                        <li>在进行如 <b>支架植入</b> 等介入治疗前，几乎所有患者都需接受该检查</li>
                    </ul>
                </div>
                <div style="flex: 1;">
                    <img src="{img_base64_1}" style="width: 100%; border-radius: 8px; margin-top: 40px;">
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 卡片2：为什么需要冠状动脉造影
    st.markdown("""
    <div class="left-title">
        <h3 style='font-size: 24px; font-weight: bold;'>💡 为什么需要冠状动脉造影</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hover-wrapper">
        <div class="hover-title">Why Is Coronary Angiography Needed? 🖱️</div>
        <div class="hover-card">
            <div style="display: flex;">
                <div style="flex: 3; padding-right: 1rem;">
                    <p style='font-weight: bold;'>该检查通常用于以下几种情况：</p>
                    <ul>
                        <li><b>明确心肌梗死后的血管状况</b>，为进一步治疗（如支架植入）提供依据</li>
                        <li><b>判断心绞痛的严重程度及其血流受限部位</b></li>
                        <li><b>为介入手术或搭桥手术等治疗做准备</b></li>
                        <li><b>心功能不明原因下降时的进一步结构功能评估</b></li>
                    </ul>
                        相较于其他非侵入性检查手段（如CT、核医学、超声心动图等），该项检查可提供更
                        <b>直接、量化且高精度</b> 的信息，有助于制定个体化治疗方案。
                </div>
                <div style="flex: 1;">
                    <img src="{img_base64_2}" style="width: 100%; border-radius: 8px; margin-top: 40px;">
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    # 卡片3：造影过程是怎样的
    st.markdown("""
    <div class="left-title">
        <h3 style='font-size: 24px; font-weight: bold;'>🩺 造影过程是怎样的</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="hover-wrapper">
        <div class="hover-title">How Is Coronary Angiography Performed? 🖱️</div>
        <div class="hover-card">
            <div class="timeline">
                <div class="container">
                    <div class="text-col">
                        <h5>🔹📝 1. 术前准备</h5>
                        <ul>
                            <li>接受 <b>心电图</b>、<b>血液检查</b>，确认 <b>造影剂过敏史</b>。</li>
                            <li>签署 <b>知情同意书</b>，了解流程与潜在风险。</li>
                            <li>停用 <b>抗凝药</b> 或调整 <b>糖尿病用药</b>。</li>
                            <li>女性需告知 <b>末次月经时间</b>，以排除妊娠。</li>
                            <li>检查前 <b>禁食 4–6 小时</b>，备好 <b>穿刺区域与静脉通道</b>。</li>
                        </ul>
                    </div>
                </div>
                <div class="container">
                    <div class="text-col">
                        <h5>🔹🏥 2. 检查过程</h5>
                        <ul>
                            <li>于 <b>导管室</b>进行，使用 <b>局麻</b> 或 <b>轻度镇静</b>。</li>
                            <li>实时监测 <b>心电图</b>、<b>血压</b> 与 <b>血氧</b>。</li>
                            <li>经 <b>桡动脉/股动脉</b> 插管至 <b>冠状动脉</b>。</li>
                            <li>注入 <b>造影剂</b> 后拍片，判断 <b>血管狭窄</b>。</li>
                            <li>可能感到 <b>轻微发热</b>，需配合 <b>屏气或咳嗽</b>。</li>
                            <li>可合并 <b>心腔导管检查</b>，评估 <b>心功能</b>。</li>
                        </ul>
                    </div>
                </div>
                <div class="container">
                    <div class="text-col">
                        <h5>🔹🛌 3. 检查结束</h5>
                        <ul>
                            <li>拔除导管后 <b>压迫止血</b>，或使用 <b>血管闭合装置</b>。</li>
                            <li><b>卧床休息数小时</b>，避免活动穿刺部位。</li>
                            <li>如 <b>腹股沟穿刺</b>，咳嗽时需 <b>按压穿刺点</b> 防止出血。</li>
                            <li>护理人员定期检查 <b>生命体征</b> 与 <b>穿刺部位</b>。</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============= 右栏：三个悬浮卡片 =============
with col_right:
    # 卡片6：可能的风险与并发症
    st.markdown("""
    <div class="right-title">
        <h3 style='font-size: 24px; font-weight: bold;'>⚠️ 可能的风险与并发症</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="right-hover-wrapper">
        <div class="hover-title">Risks and Potential Complications 🖱️</div>
        <div class="right-hover-card">
            <h5 style="margin: 0.1rem 0 0.1rem 0;">✅ 轻微并发症</h5>
            <ul style="margin-left: 1.0rem; padding-left: 1rem;">
                <li>对造影剂产生轻度<b>过敏反应</b>（如皮疹、恶心等）</li>
                <li>穿刺点轻微<b>疼痛、瘀斑或出血</b></li>
            </ul>
            <h5 style="margin-top: 1.0rem;">❗ 严重并发症（总发生率 &lt; 1%）</h5>
            <ul style="margin-left: 1.0rem; padding-left: 1rem;">
                <li ><b>死亡：约0.1%</b></li>
                <li><b>心肌梗死（MI）</b></li>
                <li><b>中风：0.1–0.6%</b></li>
                <li><b>心腔穿孔、大动脉夹层、严重出血</b></li>
                <li><b>心律失常、低血压、造影剂相关肾损伤</b></li>
                <li><b>罕见情况：</b> 空气栓塞 / 导丝器械<b>滞留断裂</b> / 支架<b>移位卡顿</b></li>
            </ul>
            <p style="margin-top: 1.0rem;">💬 <b>尽管存在风险，但冠状动脉造影在明确诊断、指导治疗方面具有不可替代的价值，获益通常远大于风险。</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    

    # 卡片4：造影图像结果解读
    st.markdown("""
    <div class="right-title">
        <h3 style='font-size: 24px; font-weight: bold;'>📊 造影图像结果解读</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="right-hover-wrapper">
        <div class="hover-title">Interpretation of Angiographic Images 🖱️</div>
        <div class="right-hover-card">
            <p style="color: #3f3683; font-weight: bold;">
                完成冠状动脉造影后，医生将获得一系列动态或静态的X线图像（<i>Coronary Angiograms</i>），用于评估冠状动脉是否存在狭窄、闭塞或形态异常。
            </p>
            <ul style="padding-left: 1.8rem; color: #555;">
                <li><b>狭窄位置</b>：如前降支、回旋支、右冠状动脉等</li>
                <li><b>狭窄程度</b>：按比例评估为轻度、中度或重度</li>
                <li><b>病变形态</b>：节段性、串珠样、钙化或伴血栓形成</li>
                <li><b>是否闭塞</b>：完全阻断血流</li>
                <li><b>血流灌注分级</b>：如 TIMI 分级系统</li>
            </ul>
            <b>
                医生会结合图像表现、心电图、症状与心功能，判断是否需进一步实施经皮冠状动脉介入治疗（PCI）或其他干预手段。
            </b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 卡片5：术后恢复注意事项
    st.markdown("""
    <div class="right-title">
        <h3 style='font-size: 24px; font-weight: bold;'>🛌 术后恢复注意事项</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="right-hover-wrapper">
        <div class="hover-title">Post-Procedure Recovery and Precautions 🖱️</div>
        <div class="right-hover-card">
            <ul style="padding-left: 1.5rem;">
                <li>多数患者可在<b>造影当日或次日出院</b>。</li>
                <li>穿刺点用<b>敷料覆盖</b>，需保持干燥与清洁，若湿润应<b>及时更换</b>。术后 <b>1–2天内可恢复淋浴</b>。</li>
                <li><b>术后一周</b>避免剧烈运动、搬重物。穿刺部位轻微<b>淤青</b>常见，约<b>2–3周内自然吸收</b>。</li>
                <li>若有<b>发热、红肿、疼痛或渗液增多</b>，需尽快就医排除感染。</li>
                <li>医生通常会在出院前说明检查结果，若仍有疑问，可于<b>复诊时向医生或家属咨询</b>。</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ✅ 中间栏：3D模型
with col_center:
    #st.markdown("<div class='card-title'>🫀 冠脉3D模型</div>", unsafe_allow_html=True)
    components.html(
        """
        <div class="sketchfab-embed-wrapper" style="width: 100%; height:500px;">
            <iframe 
                title="Coronary Arteries: Blood Supply to Ventricles" 
                frameborder="0" 
                allowfullscreen 
                mozallowfullscreen="true" 
                webkitallowfullscreen="true" 
                allow="autoplay; fullscreen; xr-spatial-tracking" 
                width="100%" height="100%"
                src="https://sketchfab.com/models/60e1da3fbef542c6bcf61cdac312ce4f/embed?autospin=1&autostart=1&transparent=1&ui_infos=0&ui_watermark_link=0&ui_watermark=0&ui_settings=0&ui_vr=0">
            </iframe>
        </div>
        """,
        height=500,
    )
    st.markdown("<div style='text-align: center; margin-top: 1px;'>旋转、缩放模型以查看冠状动脉结构</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)  # 加空行
st.markdown("""
        <div class="wave-divider"></div>
            <div class="diamond-center">
                <div class="diamond"></div>
                <div class="diamond"></div>
                <div class="diamond"></div>
            </div>
            """, unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)  # 加两个空行

colleft, space, colright = st.columns([0.9, 0.1, 0.8]) 

with colleft:
    st.markdown("""
        <h5>📽️ <b>下面为一段关于冠状动脉造影的视频，用于进一步了解检查流程。</b></h5>
        <iframe src="https://players.brightcove.net/79855382001/EkC1XU82e_default/index.html?videoId=2766459450001"
        allowfullscreen
        width="80%"
        height= 330
        style="border-radius: 10px; border: none; margin: 0.5rem auto; display: block;">
        </iframe>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="padding: 1.5rem; background: #dfe5f8 ; border-radius: 12px; border: 1px solid #e0def7;margin-top: 2rem;">
            <h5>🖼️ <b>典型病例展示</b></h5>
            <!-- 病例1 -->
            <div style="margin-bottom: 2rem;">
                <h6 style="color: #3f3683; margin-bottom: 0.5rem;"><b>病例一：</b>83岁女性，急性心肌梗死</h6>
                <img src="{img_base64_4}" style="display: block; width: 65%; border-radius: 10px; margin: 0 auto; box-shadow: 0 3px 12px rgba(90, 77, 187, 0.15);"/>
                <p style="font-size: 0.9rem; color: #666; text-align: center; margin-top: 0.8rem;">
                    左前降支近端部分闭塞（黄色箭头）→ 支架植入后血运重建
                </p>
                <details>
                    <summary style="cursor: pointer; font-weight: 600; color: #3f3683; background: linear-gradient(to right, #f0effa, #e6e5f7); padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; margin-top: 0.8rem;">
                        🔎 展开病例详情
                    </summary>
                    <div style="margin-top: 1rem; padding: 0.8rem; background-color: rgba(255,255,255,0.7); border-radius: 8px;">
                        <b>基本信息：</b>83岁女性，突发胸痛入院<br>
                        <b>造影结果：</b>LAD近端次全闭塞，支架植入后TIMI 3级血流<br>
                        <b>术后用药：</b>肝素/阿司匹林/氯吡格雷/比索洛尔/瑞舒伐他汀
                    </div>
                </details>
                <p style="margin-top: 1rem;">
                    <a href="https://academic.oup.com/ehjcr/article/8/4/ytae193/7645953?login=true" target="_blank" 
                    style="text-decoration: none; color: #3f3683; font-weight: 600; display: inline-flex; align-items: center;">
                        <span style="margin-right: 0.5rem;">📄</span> <b>查看原始文献 →</b>
                    </a>
                </p>
            </div>
            <hr style="border-top: 1px solid #dcdaf4; margin: 1.5rem 0;"/>
            <!-- 病例2 -->
            <div>
                <h6 style="color: #3f3683; margin-bottom: 0.5rem;"><b>病例二：</b>63岁男性，急性心肌梗死</h6>
                <img src="{img_base64_5}" style="width: 100%; border-radius: 10px; box-shadow: 0 3px 12px rgba(90, 77, 187, 0.15);"/>
                <p style="font-size: 0.9rem; color: #666; text-align: center; margin-top: 0.8rem;">
                    右冠状动脉中段重度狭窄 → 术后9个月CTA显示血栓完全缓解
                </p>
                <details>
                    <summary style="cursor: pointer; font-weight: 600; color: #3f3683; background: linear-gradient(to right, #f0effa, #e6e5f7); padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; margin-top: 0.8rem;">
                        🔎 展开病例详情
                    </summary>
                    <div style="margin-top: 1rem; padding: 0.8rem; background-color: rgba(255,255,255,0.7); border-radius: 8px;">
                        <b>基本信息：</b>63岁男性，胸痛就诊<br>
                        <b>造影结果：</b>
                        <ul style="padding-left: 1.5rem;">
                            <li>右冠状动脉中段重度血栓性狭窄</li>
                            <li>后降支完全血栓性闭塞</li>
                        </ul>
                        <b>治疗：</b>IVUS引导下PCI术，9个月后CTA复查
                    </div>
                </details>
                <p style="margin-top: 1rem;">
                    <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC7917400/" target="_blank" 
                    style="text-decoration: none; color: #3f3683; font-weight: 600; display: inline-flex; align-items: center;">
                        <span style="margin-right: 0.5rem;">📄</span> <b>查看原始文献 →</b>
                    </a>
                </p>
            </div>
            """,unsafe_allow_html=True)
    
    st.divider()

    # 常见问题模块
    st.markdown("""
        <h5 style="margin-top: 0;">❓ 常见问题解答</h5>
    """, unsafe_allow_html=True)

    #st.markdown("<br>", unsafe_allow_html=True)  # 加一个空行
    # 页链接按钮
    st.page_link("pages/questions.py", label="点击查看完整问题列表。如：", icon="📖")

    # 示例问题提示
    st.markdown("""
    <ul style="margin-top: 0.1rem; padding-left: 1.2rem;">
        <li>检查前需要空腹吗？</li>
        <li>糖尿病患者能做造影吗？</li>
        <li>使用AI图像分析功能是否有隐私风险？</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with colright:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h5>🤖 <b>AI辅助分析模型</b></h5>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background: #eff0f8 ; border-radius: 15px; margin-bottom: 1rem;">
        <p>为帮助临床解读过程，我们开发并集成了一款基于深度学习的血管狭窄自动检测模型。</p>
        <ul>
            <li>可对上传的冠脉造影图像进行<b>自动识别</b></li>
            <li>用<b>红框标记</b>疑似狭窄区域，作为<b>辅助参考</b></li>
            <li>不替代专业诊断，但可以：
                <ul>
                    <li>✅ 快速突出图像中的可疑部位</li>
                    <li>✅ 提升用户对图像的理解</li>
                    <li>✅ 批量处理，适用于教学与筛查</li>
                </ul>
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 页面主体布局
    uploaded_file = st.file_uploader("📤 上传您的冠脉造影图像(bmp格式）", type=["bmp"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

        st.markdown("##### ✅ 图像上传成功")
        
        with st.expander("📷 查看原始图像", expanded=True):
            st.image(image, caption="原始冠脉造影图像", width=300)

        with st.spinner("🧠 正在识别狭窄区域，请稍候..."):
            try:
                result_img, total, kept, scores = run_inference_on_image(image, model_path=model_path)

                # Step 2: 显示标注图像（替代原图）
                st.success("识别完成 ✅")
                st.image(result_img, caption="检测结果图", width=300)

                # Step 3: 检测统计
                st.markdown("##### 📊 检测简报")
                st.markdown(f"- **模型初步识别的狭窄区域总数**：{total}")
                st.markdown(f"- **过滤后保留（置信度 > 0.7）的狭窄区域**：{kept}")
                if scores:
                    # 构建 DataFrame
                    df_scores = pd.DataFrame({
                    "区域编号": [f"区域 {i+1}" for i in range(len(scores))],
                    "置信度": [round(s, 2) for s in scores]
                })  
                    st.dataframe(df_scores, hide_index=True)
                else:
                    st.warning("未发现置信度大于 0.7 的狭窄区域。")

            except Exception as e:
                st.error(f"检测失败：{e}")

        # 拓展讲解区域
        with st.expander("📚 如何理解识别出的区域？"):
            st.markdown("""
            在系统展示的图像中，模型会自动识别可能存在血管狭窄的区域，并用不同颜色的数字编号框进行标注。这些框的含义如下：

🔴 红色框：置信度高于 90%，模型认为高度疑似存在狭窄病灶；

🟠 橙色框：置信度在 70%–90% 之间，提示可能存在异常区域，建议进一步关注；

🪟 编号说明：每个框的数字（如 1, 2, 3）与下方表格中的“编号”一一对应，可查看对应的置信度得分。

⚠️ **请注意**：
本系统仅基于人工智能图像分析，不构成医疗诊断。检测结果可能受图像质量、角度、拍摄时机等因素影响。
                        
👉 强烈建议您结合其他临床检查结果，由专业心血管影像医生或介入医师做最终判断和解释。
            """, unsafe_allow_html=True)

    else:
        st.markdown(
            """
            <div style='
                padding: 10px;
                background-color: #dae0f6;
                color: #3f3683;
                border-left: 5px solid #c4cadd;
                border-radius: 10px;
                font-weight: bold;
            '>
                请上传您的图像开始分析。
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)  # 结束AI模型卡片


# 页面尾部提示
st.markdown("---")
st.markdown("<center><sub>📌 本页面内容仅用于医学科普和辅助理解，不作为任何诊断依据</sub></center>", unsafe_allow_html=True)