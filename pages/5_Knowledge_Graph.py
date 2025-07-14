import streamlit as st
import streamlit.components.v1 as components
from PIL import Image  # 用于图标优化
import os
import base64
def set_background(image_path):
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background: 
            linear-gradient(rgba(230, 230, 230, 0.3), rgba(230, 230, 230, 0.3)),
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
# 页面配置
st.set_page_config(
    page_title="冠心病知识图谱",
    page_icon=":heart:",
    layout="wide"
)

# ---- 样式优化 ----
st.markdown("""
<style>
    .main-title {
        color: #e63946;
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
    .info-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-title {
        color: #1d3557;
        border-bottom: 2px solid #a8dadc;
        padding-bottom: 0.3rem;
        margin-top: 2rem;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #a8dadc 0%, #457b9d 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        width: 30%;
        min-width: 200px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .graph-container {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        background-color: white;
    }
    @media (max-width: 768px) {
        .stat-card {
            width: 100%;
        }
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

# ---- 页面内容 ----
# 标题区
st.markdown('<h1 class="main-title">冠心病（CAD）治疗PubMed知识图谱2.0</h1>', unsafe_allow_html=True)
st.markdown('<h6 class="sub-title">PubMed Knowledge Graph 2.0 (PKG 2.0)</h6>', unsafe_allow_html=True)

# 简介卡片
with st.container():
    st.markdown("""
    <div class="info-card">
        <h3 style="color: #1d3557;">📚 知识图谱简介</h3>
        <p style="color: #1d3557;">PubMed知识图谱2.0(PKG 2.0)是一种整合了学术论文、专利和临床试验三种生物医学界常见文献的图谱。这类图谱将文献中的不同实体提取出来后根据不同的关系将这些文献之内或之间的实体进行连接，从而清晰地展现这些文献内容的联系。</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<h3 class="section-title">📊 数据来源统计</h3>', unsafe_allow_html=True)
st.markdown("""
<div class="stats-container">
    <div class="stat-card">
        <h4>学术论文</h4>
        <p style="font-size: 2rem; margin: 0.5rem 0;">15篇</p>
        <small>最新研究成果</small>
    </div>
    <div class="stat-card">
        <h4>专利文献</h4>
        <p style="font-size: 2rem; margin: 0.5rem 0;">15篇</p>
        <small>技术创新</small>
    </div>
    <div class="stat-card">
        <h4>临床试验</h4>
        <p style="font-size: 2rem; margin: 0.5rem 0;">26篇</p>
        <small>临床验证</small>
    </div>
</div>
""", unsafe_allow_html=True)

# 知识图谱展示区
st.markdown('<h3 class="section-title">🌐 知识图谱可视化</h3>', unsafe_allow_html=True)

# 交互控制区
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h4>🔧 图谱控制</h4>
        <p>使用说明：</p>
        <ul>
            <li>鼠标悬停查看节点详情</li>
            <li>拖动节点重新布局</li>
            <li>滚轮缩放视图</li>
        </ul>
        <p><small>提示：大型图谱加载可能需要几秒钟</small></p>
    </div>
    """, unsafe_allow_html=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
graph_path = os.path.join(BASE_DIR, "..", "data", "full_knowledge_graph(1).html")
with col2:
    # 嵌入HTML知识图谱
    with st.spinner('正在加载知识图谱...'):
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                components.html(
                    f.read(),
                    height=800,
                    scrolling=True
                )
        except FileNotFoundError:
            st.error("未找到知识图谱文件，请确保 full_knowledge_graph(1).html 存在于当前目录")
            st.image(
                "https://via.placeholder.com/800x500?text=Knowledge+Graph+Placeholder",
                caption="知识图谱预览占位图",
                use_container_width=True  # ✅ 使用新参数替代 use_column_width
            )

# 底部说明
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; margin-top: 2rem;">
    <p>© 2025 医学信息实习 | 数据更新日期: 2025-7-13</p>
    <p><small>注意：本图谱仅用于科研用途，临床决策请参考权威指南</small></p>
</div>
""", unsafe_allow_html=True)