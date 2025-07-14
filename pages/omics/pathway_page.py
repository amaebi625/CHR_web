import streamlit as st
import pandas as pd
import gseapy as gp
from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 注入自定义CSS
# 注入自定义CSS
st.markdown("""
<style>
    .main-title {
        color: #6A1B9A;
        font-size: 24px;
        font-weight: 700;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        padding: 12px 0;
        border-bottom: 2px solid #BA68C8;
        margin-bottom: 25px;
    }

    .subheader {
        color: #7E57C2;
        font-size: 18px;
        font-weight: 600;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        border-left: 4px solid #BA68C8;
        padding-left: 10px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .card-title {
        color: #7E57C2;
        font-size: 16px;
        font-weight: 600;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 12px;
    }

    .card {
        background: #F3E5F5;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        color: #4A148C;
        text-align: left;
        border: 1px solid #D1C4E9;
    }

    .stButton > button {
        background-color: #CE93D8 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 700;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        cursor: pointer;
        width: 100%;
        font-size: 14px !important;
        transition: background-color 0.3s ease;
        box-shadow: 0 2px 5px rgba(206, 147, 216, 0.4);
    }

    .stButton > button:hover {
        background-color: #AB47BC !important;
        box-shadow: 0 4px 8px rgba(186, 104, 200, 0.4);
    }

    div.stFileUploader {
        max-width: 480px !important;
        margin-left: auto;
        margin-right: auto;
        border: 2px dashed #BA68C8 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background-color: #F8EAF6 !important;
    }

    .custom-dashed-container {
        border: 2px dashed #BA68C8;
        border-radius: 10px;
        background-color: #F8EAF6;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 分割线紫色 */
    hr.custom-divider {
        border: none;
        border-top: 2px solid #BA68C8;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)

def analyze_and_visualize(ssgsea_clinical_df, title_prefix=""):
    ssgsea_scores = ssgsea_clinical_df.drop(columns=['group_label'])

    def diff_test(pathway):
        group0 = ssgsea_clinical_df[ssgsea_clinical_df['group_label'] == 0][pathway].dropna()
        group1 = ssgsea_clinical_df[ssgsea_clinical_df['group_label'] == 1][pathway].dropna()
        stat, p = mannwhitneyu(group0, group1, alternative='two-sided')
        return p

    pvals = {pw: diff_test(pw) for pw in ssgsea_scores.columns}
    pvals_series = pd.Series(pvals).sort_values()
    sig_pathways = pvals_series[pvals_series < 0.05]

    st.info(f"显著差异通路数量: {len(sig_pathways)}")
    if len(sig_pathways) == 0:
        st.warning("未检测到显著差异通路。")
        return

    top3 = sig_pathways.index[:3]

    # Top3箱线图
    st.markdown('<div class="subheader">Top 3 显著通路箱线图</div>', unsafe_allow_html=True)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    for i, pw in enumerate(top3):
        sns.boxplot(
            x='group_label', y=pw, data=ssgsea_clinical_df,
            palette=['#1f77b4', '#ff7f0e'], ax=axes[i]
        )
        axes[i].set_title(pw, fontsize=14, fontweight='bold')
        axes[i].set_xticklabels(['对照组', '冠心病'])
        axes[i].set_ylabel('ssGSEA得分' if i == 0 else '')
    st.pyplot(fig)

    # 热图
    st.markdown('<div class="subheader">显著通路组均值热图</div>', unsafe_allow_html=True)
    group_means = ssgsea_clinical_df.groupby('group_label')[sig_pathways.index].mean().T
    heatmap_fig = go.Figure(go.Heatmap(
        z=group_means.values,
        x=['对照组', '冠心病'],
        y=group_means.index,
        colorscale='RdBu_r',
        colorbar=dict(title='均值得分')
    ))
    heatmap_fig.update_layout(margin=dict(l=100, r=20, t=50, b=50), height=450,
                              title=title_prefix + "显著通路组均值热图")
    st.plotly_chart(heatmap_fig, use_container_width=True)

    # 火山图
    st.markdown('<div class="subheader">免疫通路差异火山图</div>', unsafe_allow_html=True)
    volcano_df = pd.DataFrame({
        'pathway': pvals_series.index,
        'log_p': -np.log10(pvals_series),
        'effect_size': ssgsea_scores.mean(axis=0).reindex(pvals_series.index)
    })
    volcano_fig = go.Figure()
    volcano_fig.add_trace(go.Scatter(
        x=volcano_df['effect_size'],
        y=volcano_df['log_p'],
        mode='markers',
        marker=dict(color=volcano_df['log_p'], colorscale='Viridis', size=8, opacity=0.7),
        text=volcano_df['pathway'], hoverinfo='text+x+y'
    ))
    volcano_fig.update_layout(
        title=title_prefix + '免疫通路差异火山图',
        xaxis_title='效应大小', yaxis_title='-log10(p)',
        height=450, margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(volcano_fig, use_container_width=True)


def show_ssgsea_table(ssgsea_clinical_df):
    st.markdown('<div class="subheader">ssGSEA 临床分组数据预览</div>', unsafe_allow_html=True)
    st.dataframe(ssgsea_clinical_df)


def pathway_page(set_page_callback):
    st.markdown('<div style="text-align:right; margin-bottom:20px;">', unsafe_allow_html=True)
    if st.button("🔙 返回首页"):
        set_page_callback("main")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-title">冠心病免疫通路差异分析（ssGSEA）</div>', unsafe_allow_html=True)

    st.markdown('<div class="subheader">免疫通路分析的意义</div>', unsafe_allow_html=True)
    # 段落文字描述
    st.markdown("""
通过 ssGSEA（single-sample Gene Set Enrichment Analysis）方法，对每个样本中免疫相关通路的富集得分进行定量评估，
从而全面刻画冠心病（CHD）患者免疫系统的活跃状态及其在关键通路（如炎症反应、抗原呈递等）上的功能差异。
随后，利用统计检验方法对CHD组与对照组的免疫通路得分进行差异分析，以识别在疾病状态下显著上调或下调的通路。
这一流程不仅揭示了CHD相关的免疫特征变化，还帮助我们发掘具有潜在临床诊断和治疗价值的免疫通路，
为进一步的靶点筛选和个体化免疫干预提供了理论依据。
""")
    
    # —— ssGSEA分析模块 —— #
    st.markdown('<div class="subheader"> 从表达矩阵运行 ssGSEA 分析</div>', unsafe_allow_html=True)
    expr_dir = clin_dir = gmt_dir = "data/"

    def list_files(dir_path, ext): return [f for f in os.listdir(dir_path) if f.endswith(ext)]

    expr_files = list_files(expr_dir, ".csv")
    clin_files = list_files(clin_dir, ".csv")
    gmt_files = list_files(gmt_dir, ".gmt")

    with st.container():
        st.markdown('<div class="custom-dashed-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            selected_expr = st.selectbox("表达矩阵文件", [""] + expr_files, key="expr_selectbox")
        with col2:
            selected_clin = st.selectbox("临床分组文件", [""] + clin_files, key="clin_selectbox")
        st.markdown('</div>', unsafe_allow_html=True)

    expression_data = clinical_df = None
    if selected_expr:
        expression_data = pd.read_csv(os.path.join(expr_dir, selected_expr), index_col=0)
        st.write(f"✅ 已加载表达矩阵：{selected_expr}")
    if selected_clin:
        clinical_df = pd.read_csv(os.path.join(clin_dir, selected_clin), index_col=0)
        st.write(f"✅ 已加载临床分组：{selected_clin}")

    selected_gmt = st.selectbox("选择 GMT 通路基因集文件", [""] + gmt_files)
    gmt_path = os.path.join(gmt_dir, selected_gmt) if selected_gmt else None

    if st.button("运行 ssGSEA 分析"):
        if expression_data is None or clinical_df is None or gmt_path is None:
            st.error("⚠ 请确保已选择表达矩阵、临床分组和GMT文件")
        else:
            with st.spinner("ssGSEA 分析中..."):
                ssgsea_results = gp.ssgsea(
                    data=expression_data,
                    gene_sets=gmt_path,
                    sample_norm_method='rank',
                    outdir=None,
                    no_plot=True,
                    processes=4
                )
                df_long = ssgsea_results.res2d
                ssgsea_scores = df_long.pivot(index="Name", columns="Term", values="NES")
                ssgsea_scores = ssgsea_scores.apply(pd.to_numeric, errors='coerce')

            st.success("✅ ssGSEA 计算完成")
            

            # 添加 group_label 映射（CHD=1, Control=0）
            clinical_df['group_label'] = clinical_df['group'].map({'CHD': 1, 'Control': 0})
            ssgsea_clinical_df = pd.concat([ssgsea_scores, clinical_df['group_label']], axis=1)

            # 展示与分析
            show_ssgsea_table(ssgsea_clinical_df)
            analyze_and_visualize(ssgsea_clinical_df, title_prefix="（计算）")

            # 保存结果
            output_path = os.path.join("data", "ssgsea_clinical_result.csv")
            ssgsea_clinical_df.to_csv(output_path)
            st.success(f"✅ 已保存 ssGSEA 结果至本地文件：{output_path}")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # —— 加载已有 ssGSEA 文件 —— #
    st.markdown('<div class="subheader"> 加载本地已有 ssGSEA 分析结果</div>', unsafe_allow_html=True)
    ssgsea_files = [f for f in os.listdir("data/") if f.endswith(".csv")]
    selected_ssgsea_file = st.selectbox("选择 ssGSEA 得分文件（含 group_label）", [""] + ssgsea_files)

    if selected_ssgsea_file:
        ssgsea_path = os.path.join("data", selected_ssgsea_file)
        try:
            ssgsea_clinical_df = pd.read_csv(ssgsea_path, index_col=0)
            st.success(f"✅ 已加载 ssGSEA 文件：{selected_ssgsea_file}")
            show_ssgsea_table(ssgsea_clinical_df)
            analyze_and_visualize(ssgsea_clinical_df, title_prefix="（本地）")
        except Exception as e:
            st.error(f"❌ 读取失败，请检查文件格式：{e}")
