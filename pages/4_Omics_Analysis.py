import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import plotly.express as px
import os
from pages.omics.pathway_page import pathway_page
from pages.omics.cluster_page import cluster_page
from pages.omics.target_page import target_page
from pages.omics.mirna_page import mirna_page

# 页面配置
st.set_page_config(page_title="冠心病组学平台", layout="wide", page_icon="🫀")

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import plotly.express as px
import os
import scipy.stats as stats
import statsmodels.stats.multitest as smm
import matplotlib.pyplot as plt
import seaborn as sns
import base64

# 设置页面配置
st.set_page_config(page_title="冠心病组学平台", layout="wide", page_icon="🫀")


# 读取图片并转base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(BASE_DIR, "..", "image", "背景.jpg")

img_base64 = get_base64_of_bin_file(bg_path)

background_css = f"""
<style>
body {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

/* 加紫色滤板 */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(206, 147, 216, 0.15);  /* 深紫色 + 50% 透明 */
    backdrop-filter: blur(4px);           /* 模糊滤镜，可选 */
    z-index: -1;
}}

.stApp {{
    background-color: rgba(255, 255, 255, 0.01);
}}
</style>
"""


# 注入背景样式
st.markdown(background_css, unsafe_allow_html=True)


# 在您的CSS样式部分替换为以下代码：
st.markdown("""
<style>  
    /* 主标题样式 - 深紫色 */
    .main-title {
        color: #5E35B1;   
        text-align: center;
        padding: 15px;
        border-bottom: 2px solid #7E57C2;
        margin-bottom: 30px;
        font-size: 28px;
        font-weight: 700;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* 子标题样式 - 紫色 */
    .subheader {
        color: #7E57C2;
        border-left: 4px solid #9575CD;
        padding-left: 10px;
        margin-top: 25px;
        margin-bottom: 20px;
        font-size: 18px;
        font-weight: 600;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 卡片样式 - 淡紫色半透明背景 */

.card {
    background: rgba(237, 231, 246, 0.85);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s;
    height: 180px;  /* 固定高度 */
    font-size: 14px;
    color: #4A148C;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    text-align: left;
    border: 1px solid #D1C4E9;
    overflow-y: auto;  /* 如果内容超出，显示滚动条 */
}

    .card h3 {
        color: #5E35B1;  /* 紫色标题 */
        margin-bottom: 0px;
        font-size: 16px;
        font-weight: 600;
    }

    .card ul {
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .card ul li {
        position: relative;
        padding-left: 0px;       
        text-align: left;
        line-height: 1.4;
        color: #4527A0;  /* 深紫色列表项 */
    }
    
    /* 卡片悬停效果 */
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        background: rgba(243, 229, 245, 0.9);  /* 悬停时变为淡粉色 */
    }
    
 /* 按钮样式 */
div.stButton > button {
    width: fit-content !important;
    min-width: 120px;
    padding: 6px 16px !important;
    font-size: 14px !important;
    font-weight: bold;
    border-radius: 8px !important;
    background-color: #CE93D8 !important;
    color: white !important;
    box-shadow: 0 2px 5px rgba(206, 147, 216, 0.4);
    transition: background-color 0.3s ease;
}

/* 悬停时按钮颜色渐变 */
div.stButton > button:hover {
    background: linear-gradient(to right, #F48FB1, #BA68C8) !important;
    box-shadow: 0 4px 8px rgba(186, 104, 200, 0.4);
}
    
    /* PCA卡片样式 */
    .pca-card {
        background: rgba(255, 255, 255, 0.8);  /* 半透明白色 */
        border: 1px solid #D1C4E9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 分隔线样式 */
    .hr-with-text {
      display: flex;
      align-items: center;
      text-align: center;
      color: #7E57C2;  /* 紫色 */
      font-weight: 600;
      font-size: 18px;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      margin: 20px 0;
    }

    .hr-with-text::before,
    .hr-with-text::after {
      content: "";
      flex: 1;
      border-bottom: 1.5px solid #D1C4E9;  /* 浅紫色 */
      margin: 0 10px;
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

# 其余代码保持不变，确保 h1/h2 已用 div.main-title / div.subheader 包裹


# 页面状态管理
PAGES = {
    "主页": "main",
    "免疫通路分析": "pathway",
    "免疫亚型识别": "cluster",
    "靶点识别": "target",
    "miRNA-mRNA 网络": "mirna"
}

if "page" not in st.session_state:
    st.session_state.page = "main"

def set_page(page_key):
    st.session_state.page = page_key

def load_local_data(expr_path, group_path):
    expr_df = pd.read_csv(expr_path, index_col=0)
    group_df = pd.read_csv(group_path)
    return expr_df, group_df

def main_page():
    st.markdown('<div class="main-title"> 冠心病组学分析平台</div>', unsafe_allow_html=True)
        # 先放一个subheader样式的“背景”标题
    st.markdown('<div class="subheader">背景</div>', unsafe_allow_html=True)
    
    # 再放一段正文文字，可以加些样式，比如淡紫色背景、圆角和内边距
    st.markdown("""
    <div style="
        background: rgba(158, 123, 186, 0.1);
        border-radius: 10px;
        padding: 12px 20px;
        margin-bottom: 30px;
        font-size: 18px;
        color: black;
        line-height: 1.9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    ">
    本部分以冠心病患者的多组学数据为基础，系统开展了从差异表达、免疫通路活性、免疫亚型划分、分子靶点筛选到miRNA调控网络构建的多层次分析，构建了一个围绕“免疫调控在冠心病中的作用机制”的研究框架。
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="subheader">📂 数据集选择</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        data_path = os.path.join(BASE_DIR, "..", "data")
        st.markdown('<div class="card"><h3>内置数据集选择</h3><p>选择一个内置数据集进行分析：</p></div>', unsafe_allow_html=True)
        options = {
            "无（使用上传数据）": (None, None),
            "本地mRNA-seq数据集": (os.path.join(data_path,"GSE12288_gene_expr_scaled.csv"), os.path.join(data_path,"GSE12288_sample_group.csv")),
            "本地miRNA-seq数据集": (os.path.join(data_path,"GSE105449_miRNA_expr_scaled.csv"), os.path.join(data_path,"GSE105449_sample_group.csv"))
        }
        selected_dataset = st.selectbox("", list(options.keys()), index=1, key="local_dataset")
        if st.button("加载内置数据集", key="load_local"):
            expr_path, group_path = options[selected_dataset]
            if selected_dataset != "无（使用上传数据）":
                if os.path.exists(expr_path) and os.path.exists(group_path):
                    st.session_state['expr_path'] = expr_path
                    st.session_state['group_path'] = group_path
                    st.session_state['data_source'] = "builtin"
                    st.success(f"✅ 已选择内置数据集：{selected_dataset}")
                else:
                    st.error("❌ 内置数据文件缺失")
            else:
                st.info("请使用右侧上传数据功能")

    with col2:
        st.markdown('<div class="card"><h3>上传自定义数据</h3><p>上传你自己的表达矩阵和分组信息文件（CSV或TSV）：</p></div>', unsafe_allow_html=True)
        uploaded_expr = st.file_uploader("表达数据", type=["csv", "tsv"], key="expr_uploader")
        uploaded_group = st.file_uploader("分组信息", type=["csv", "tsv"], key="group_uploader")
        if uploaded_expr and uploaded_group and st.button("加载上传数据", key="load_upload"):
            st.session_state['uploaded_expr'] = uploaded_expr
            st.session_state['uploaded_group'] = uploaded_group
            st.session_state['data_source'] = "upload"
            st.success("✅ 上传数据准备加载")

    expr_df, group_df = None, None
    if 'data_source' in st.session_state:
        if st.session_state['data_source'] == "builtin":
            expr_df, group_df = load_local_data(st.session_state['expr_path'], st.session_state['group_path'])
        elif st.session_state['data_source'] == "upload":
            st.session_state['uploaded_expr'].seek(0)
            st.session_state['uploaded_group'].seek(0)
            expr_df = pd.read_csv(st.session_state['uploaded_expr'], sep="\t" if st.session_state['uploaded_expr'].name.endswith(".tsv") else ",", index_col=0)
            group_df = pd.read_csv(st.session_state['uploaded_group'], sep="\t" if st.session_state['uploaded_group'].name.endswith(".tsv") else ",")

    if expr_df is not None and group_df is not None:
        st.markdown('<div class="subheader">🔍 数据预览</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["表达数据", "分组信息"])
        with tab1:
            st.write("表达数据预览（前5行×前5列）：")
            st.dataframe(expr_df.iloc[:5, :5])
            expr_df = expr_df.T
            st.write("转置后数据（样本×基因）：")
            st.dataframe(expr_df.iloc[:5, :5])
        with tab2:
            st.write("分组信息预览：")
            st.dataframe(group_df.head())

        st.markdown('<div class="subheader">样本匹配</div>', unsafe_allow_html=True)
        samples_intersect = expr_df.index.intersection(group_df.iloc[:, 0])
        if len(samples_intersect) == 0:
            st.error("❌ 无交集样本ID")
            return
        expr_df = expr_df.loc[samples_intersect]
        group_df = group_df[group_df.iloc[:, 0].isin(samples_intersect)]
        st.success(f"✅ 匹配到 {len(samples_intersect)} 个样本")

        sample_col, group_col = group_df.columns[0], group_df.columns[1]
        st.markdown('<div class="subheader">PCA分析</div>', unsafe_allow_html=True)
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(expr_df)
        pca_df = pd.DataFrame(pca_result, columns=["PC1", "PC2"], index=expr_df.index)
        pca_df[group_col] = group_df.set_index(sample_col).loc[pca_df.index, group_col]

        col_pca1, col_pca2 = st.columns([1, 2])
        with col_pca1:
            st.markdown(f'''
            <div style="border: 1.5px dashed #CE93D8; border-radius: 10px; background-color: rgba(243, 229, 245, 0.9); padding: 15px; margin-bottom: 15px;">
                <div style="font-size:16px; font-weight:bold; color:#6A1B9A;">PCA 解释方差</div>
                <div style="display: flex; justify-content: space-between;">
                    <div style="text-align: center;"><b>PC1</b><br>{pca.explained_variance_ratio_[0]*100:.2f}%</div>
                    <div style="text-align: center;"><b>PC2</b><br>{pca.explained_variance_ratio_[1]*100:.2f}%</div>
                    <div style="text-align: center;"><b>累计</b><br>{sum(pca.explained_variance_ratio_[:2])*100:.2f}%</div>
                </div>
            </div>''', unsafe_allow_html=True)
            group_counts = pca_df[group_col].value_counts()
            color_map = ['#BA68C8', '#F48FB1', '#FFD54F', '#9575CD']  # 取决于分组数量
            fig2 = px.bar(
              x=group_counts.index,
              y=group_counts.values,
              color=group_counts.index,
              title="样本分组分布",
              color_discrete_sequence=color_map[:len(group_counts)])
            fig2.update_layout(height=320)

            st.plotly_chart(fig2, use_container_width=True)

        with col_pca2:
            fig = px.scatter(pca_df, x="PC1", y="PC2", color=group_col, title="PCA主成分分析",color_discrete_sequence=color_map[:len(pca_df[group_col].unique())])
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
<style>
.hr-with-text {
  display: flex;
  align-items: center;
  text-align: center;
  color:  #6A1B9A;
  font-weight: 600;
  font-size: 18px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  margin: 20px 0;
}

.hr-with-text::before,
.hr-with-text::after {
  content: "";
  flex: 1;
  border-bottom: 1.5px solid #BA68C8;
  margin: 0 10px;
}
</style>

<div class="hr-with-text">功能模块</div>
""", unsafe_allow_html=True)



    
    cols = st.columns([1, 1, 1, 1.1])  # 最后一个列宽是前面列的0.7倍

    module_info = [
        ("免疫通路分析", ["通路富集分析", "ssGSEA分析", "通路活性可视化"], "pathway_btn", "pathway"),
        ("免疫亚型识别", ["样本聚类分析", "免疫亚型识别", "亚型特征可视化"], "cluster_btn", "cluster"),
        ("靶点识别", ["Hub基因筛选", "潜在靶点预测", "药物-靶点互作"], "target_btn", "target"),
        ("miRNA-mRNA网络", ["调控网络构建", "关键miRNA识别", "互作关系可视化"], "mirna_btn", "mirna")
    ]
    for i, (title, features, btn_key, page_key) in enumerate(module_info):
        with cols[i]:
            st.markdown(f'<div class="card"><h3>{title}</h3><ul>' + ''.join([f"<li>{f}</li>" for f in features]) + '</ul></div>', unsafe_allow_html=True)
            if st.button("进入模块 →", key=btn_key):
                set_page(page_key)

# 路由调用
if st.session_state.page == "main":
    main_page()
elif st.session_state.page == "pathway":
    pathway_page(set_page)
# 后续模块视图留空，待集成 cluster_page、target_page、mirna_page
elif st.session_state.page == "cluster":
    cluster_page(set_page)
 
elif st.session_state.page == "target": 
    target_page(set_page)

elif st.session_state.page == "mirna":
    mirna_page(set_page)