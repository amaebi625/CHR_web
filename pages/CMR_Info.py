# cmr_info.py

# pages/cmr_info.py
import os
import streamlit as st
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
bg_path = os.path.join(BASE_DIR, "..", "image", "cmr_bg.png")
set_background(bg_path)
st.markdown("""
<style>
/* 设置正文段落文字字体大小和加粗 */
div[data-testid="stMarkdownContainer"] p {
    font-size: 1.05rem;
    font-weight: 700;
    color: #3B2B4F;
    line-height: 1.25;
}
/* 全局 Markdown 段落与列表项文字颜色（冒号后文字） */
.markdown-text-container p,
.markdown-text-container li {
    color: rgba(70, 45, 105, 0.95) !important;  /* 深紫色，接近黑字 */
    font-weight: 700;
}
/* 设置 blockquote 的样式（> 引用部分） */
div[data-testid="stMarkdownContainer"] blockquote {
    font-size: 1.05rem;
    color: #4C3F5A;
    background: rgba(240,240,250,0.4);
    padding: 1rem 1rem;
    border-left: 4px solid #AAA3D0;
    border-radius: 5px;
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
# 页面配置
st.set_page_config(page_title="CMR 科普指南", page_icon="📖", layout="wide")
st.markdown("""
<style>
.main-title {
        color: #e63946;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 板块1：什么是 CMR（心脏磁共振成像）
# ==============================
st.markdown("<h1 class='main-title'>🫀 心脏磁共振成像（CMR）科普</h1>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 什么是 CMR？")
st.markdown("""
心血管磁共振成像（Cardiac Magnetic Resonance，CMR）是一项基于 MRI 的**高精度、无电离辐射的心脏成像技术**，被誉为心脏功能与结构评估的“金标准”。

- **非侵入性 + 高分辨率**：无需导管、不依赖 X 射线，能够清晰显示心肌轮廓、心腔、血流等细节；
- **功能 + 组织评估**：通过 cine 动态序列测量射血分数（EF）、血容量；晚期增强（LGE）、T1/T2 mapping 可识别心肌炎、纤维化、瘢痕等病理变化；
- **多种序列组合**：包括亮-黑血序列、灌注序列、4D-flow 等，可评估解剖、灌注、运动与应变状态；
- **广泛临床应用**：用于扩张型/肥厚型心肌病、冠心病、先天性心脏病、心肌炎等疾病的早期检测与疗效评估。

> **CMR的功能和优势：**  
> • CMR 可测量心脏射血分数、血流动力学和组织特性；  
> • Cine 序列提供每个心动周期的动态图像；  
> • LGE 用于检测心肌瘢痕，T1/T2 mapping 用于诊断炎症或纤维化；  
> • 无电离辐射，适合重复检测。

""")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "..", "image", "cmr.jpg")
st.image(
    IMG_PATH, 
    caption="心脏 CMR 横断面解剖图示，左心室 (LV)、右心室 (RV)、心房等结构清晰可见",
     width=600
)
# ==============================
# 板块2：医学分区与功能科普
# ==============================
st.markdown("---")
st.markdown("## 医学分区与功能科普")
st.markdown("""
冠心病的本质是冠状动脉粥样硬化所导致的**心肌供血不足**，其典型后果包括：

- 心肌缺血（Ischemia）；
- 心肌梗死（Myocardial Infarction, MI）；
- 心肌重构与收缩功能障碍；
- 心力衰竭（Heart Failure）等。

冠心病的心肌供血不足将引发一系列心肌结构与功能的变化，而这些变化在影像上有着最直观的表现，且往往集中在特定的解剖区域，需要精准的识别与分割。

| 区域 | 解剖位置 | 监测功能 |
|------|----------|-----------|
| **左心室（LV）** | 主动脉流出腔 | 反映心脏泵血功能 |
| **右心室（RV）** | 连通肺循环 | 评估肺动脉高压、右心功能衰减 |
| **心肌壁（MYO）** | 包裹心腔的心肌层 | 监测墙厚、纤维化、炎症等心肌结构变化 |

CMR是目前评估冠心病心肌损伤的金标准影像手段之一，其结构分割是完成所有**下游定量**分析的前置任务：

| 下游分析指标 | 依赖区域 | 医学意义 |
| --------------------------- | -------- | ------------------------ |
| 舒张末体积/收缩末体积(EDV/ESV)    | LV  | 反映心腔容量变化                 |
| 每搏输出量(SV)                   | LV  | 每次收缩泵出的血量，SV = EDV - ESV |
| 射血分数(EF)                    | LV  | 心脏泵血能力核心指标，EF = SV / EDV |
| 右心室舒张末/收缩末体积(RVEDV/RVESV) | RV  | 评估肺循环容量变化                |
| 右心室射血分数(RVEF)               | RV  | 右心泵血功能评估指标               |
| 心肌质量                        | MYO | 用于判断心肌肥厚、心室重构            |
| 心肌壁厚与运动分析                   | MYO | 用于识别心肌梗死区域、分析运动同步性       |


""")

# ==============================
# 板块3：数据与模型架构
# ==============================
st.markdown("---")
st.markdown("## 数据来源与模型架构")
st.markdown("""
### 📚 数据来源
本系统基于 ACDC（Automated Cardiac Diagnosis Challenge）公开数据集构建并训练，数据共包括 150 例 Cine CMR 检查样本（100 例训练 + 50 例测试），覆盖五种主要临床类型：
- 正常心脏（Normal）；
- 心肌梗死（Myocardial Infarction）；
- 扩张型心肌病（Dilated Cardiomyopathy）；
- 肥厚型心肌病（Hypertrophic Cardiomyopathy）；
- 右心室异常（Abnormal Right Ventricle）。

### 🔧 模型结构设计

本模型在标准 U‑Net 架构基础上建立了一种轻量化的 Encoder–Decoder 网络，兼顾表达能力与训练效率，特别适用于 2D CMR 图像的语义分割任务。整体模型架构如下：

| 模块       | 操作构成                     | 通道数变化     | 输出尺寸（示例） |
|------------|------------------------------|----------------|------------------|
| 输入层     | 单通道 CMR 图像              | 1              | 256×256          |
| 编码器 1   | Conv2D×2 + BN + ReLU + MaxPool | 32 → 64        | 128×128          |
| 编码器 2   | Conv2D×2 + BN + ReLU + MaxPool | 64 → 128       | 64×64            |
| 编码器 3   | Conv2D×2 + BN + ReLU + MaxPool | 128 → 256      | 32×32            |
| 瓶颈层     | Conv2D + BN + ReLU           | 256 → 512      | 16×16            |
| 解码器 1   | UpSampling + skip + Conv2D×2 | 512 → 256      | 32×32            |
| 解码器 2   | UpSampling + skip + Conv2D×2 | 256 → 128      | 64×64            |
| 解码器 3   | UpSampling + skip + Conv2D×2 | 128 → 64       | 128×128          |
| 输出层     | Conv2D + Softmax             | 64 → 4         | 256×256×4        |

此网络通过多尺度信息融合与空间分辨率恢复机制，在保持较小模型规模的同时，有效提升了分割精度与模型推理效率。

""")


# ==============================
# 板块4：模型性能（Dice 指标表现）
# ==============================
st.markdown("---")
st.markdown("## 多维度模型性能展示")
st.markdown("""
模型在 ACDC 训练集上完成训练后，针对独立测试集进行了性能评估。主要分割指标表现如下所示：

| 指标名称 (Metric) | 数值 (Value) | 评价说明 |
|------------------|---------------|-----------|
| **Dice 系数 (Dice Coefficient)** | 0.9247 | ✅ 预测区域与真实区域高度一致 |
| **Jaccard 指数 (IoU)** | 0.8610 | ✅ 预测掩码与真实掩码有较强空间重叠性 |
| **Precision (查准率)** | 0.9473 | ✅ 误报率低，预测结果可靠性强 |
| **Recall (查全率)** | 0.9390 | ✅ 漏检率低，模型具备良好敏感性 |
| **Accuracy (总体像素准确率)** | 0.9954 | ✅ 整体分类效果极佳 |

结果表明，本模型在控制计算复杂度的同时，性能能够在CMR分割任务中达到高精度水平，具有实用价值。
""")

# ==============================
# 返回按钮
# ==============================
st.markdown("""
<div style="text-align:center; margin:40px 0;">
  <a href="/cmr" target="_self">
    <button style="
      background:#0072C6;
      color:white;
      padding:14px 36px;
      font-size:16px;
      border:none;
      border-radius:8px;
      cursor:pointer;
      box-shadow:0 3px 10px rgba(0,0,0,0.2);
    ">🔙 返回分割页面</button>
  </a>
</div>
""", unsafe_allow_html=True)
