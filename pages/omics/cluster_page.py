import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.stats import kruskal
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import os

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体（Windows常见）
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 添加标题样式
st.markdown("""
    <style>
    .custom-purple-title {
        font-size: 18px;
        color: #D291BC;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)


def cluster_page(set_page_callback):
    st.markdown('<div style="text-align:right; margin-bottom:20px;">', unsafe_allow_html=True)
    if st.button("🔙 返回首页"):
        set_page_callback("main")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-title">冠心病免疫亚型识别分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">免疫亚型聚类</div>', unsafe_allow_html=True)
    def load_ssgsea_files():
        try:
            files = [f for f in os.listdir("data") if f.startswith("ssgsea_clinical") and f.endswith(".csv")]
            return files
        except Exception:
            return []

    available_files = load_ssgsea_files()
    if not available_files:
        st.error("❌ 当前 data/ 目录中没有 ssGSEA 结果文件，请先在通路分析页生成。")
        st.stop()

    st.markdown('<div class="custom-purple-title">请选择ssGSEA通路分析生成的合并文件：</div>', unsafe_allow_html=True)
    selected_file = st.selectbox("", [""] + available_files, index=1)
    
    if not selected_file:
        st.info("请先选择文件")
        return

    ssgsea_clinical_df = pd.read_csv(os.path.join("data", selected_file), index_col=0)
    st.success(f"✅ 已加载文件：{selected_file}")

    run_btn = st.button("运行聚类分析")
    if not run_btn:
        st.info("点击上方按钮运行聚类分析")
        return

    features = ssgsea_clinical_df.drop(columns=['group_label'])

    # 1. 聚类数优化
    k_range = range(2, 10)
    inertias, sil_scores = [], []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42)
        labels = km.fit_predict(features)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(features, labels))

    st.markdown('<div class="subheader">肘部法则 & 轮廓系数</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)  # 增加间距

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(k_range, inertias, marker='o')
    ax[0].set_title('肘部法则 - SSE')
    ax[0].set_xlabel('聚类数')
    ax[0].set_ylabel('总平方误差')

    ax[1].plot(k_range, sil_scores, marker='s', color='green')
    ax[1].set_title('轮廓系数')
    ax[1].set_xlabel('聚类数')
    ax[1].set_ylabel('Silhouette Score')

    st.pyplot(fig)

    best_k = k_range[np.argmax(sil_scores)]
    st.success(f"推荐聚类数为 k = {best_k}（基于轮廓系数最大值）")

    # 2. 聚类并添加标签
    ssgsea_clinical_df['immune_cluster'] = KMeans(n_clusters=best_k, random_state=42).fit_predict(features)

    # 3. 聚类分布可视化
    st.markdown('<div class="subheader">聚类结果分布</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    fig2, ax2 = plt.subplots()
    sns.countplot(x='immune_cluster', data=ssgsea_clinical_df, palette='Set2', ax=ax2)
    ax2.set_title("不同免疫亚型样本数量")
    ax2.set_xlabel("免疫亚型")
    ax2.set_ylabel("样本数")
    st.pyplot(fig2)

    # 4. 聚类间通路差异分析（Kruskal-Wallis）
    st.markdown('<div class="subheader">聚类间通路差异分析 (Kruskal-Wallis)</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    features2 = ssgsea_clinical_df.drop(columns=['group_label', 'immune_cluster'])
    pvals = {}
    for pw in features2.columns:
        groups = [group[pw].dropna() for _, group in ssgsea_clinical_df.groupby('immune_cluster')]
        stat, pval = kruskal(*groups)
        pvals[pw] = pval

    pvals_df = pd.Series(pvals, name='p-value').sort_values()
    top3_pathways = pvals_df.head(3).index.tolist()

    fig3, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    for i, pw in enumerate(top3_pathways):
        sns.boxplot(x='immune_cluster', y=pw, data=ssgsea_clinical_df, ax=axes[i])
        axes[i].set_title(f"{pw}\nK-W p={pvals[pw]:.3e}")
        axes[i].set_xlabel('免疫亚型')
        axes[i].set_ylabel('ssGSEA得分' if i == 0 else '')
    st.pyplot(fig3)

    # 5. 通路活性热图
    st.markdown('<div class="subheader">通路活性热图 (Top变异通路)</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    cluster_means = ssgsea_clinical_df.groupby("immune_cluster").mean()
    top_var_pathways = cluster_means.var().sort_values(ascending=False).index[:30]

    fig4, ax4 = plt.subplots(figsize=(10, 8))
    sns.heatmap(cluster_means[top_var_pathways], cmap="coolwarm", center=0, ax=ax4)
    ax4.set_title("各亚型Top通路活性热图")
    ax4.set_xlabel("通路")
    ax4.set_ylabel("免疫亚型")
    st.pyplot(fig4)
    st.markdown('''
<p style="color:#7E57C2; font-size:16px; line-height:1.9;">
免疫亚型分类清晰分离了两类通路活跃模式，体现出CHD患者在免疫水平上的异质性。<br>
· Cluster 0 可视为“免疫高活性亚型”，更可能涉及慢性炎症、免疫持续激活；<br>
· Cluster 1 则表现为“免疫低活性亚型”，可能处于疾病不同阶段或存在免疫抑制现象；<br>
后续可以进一步将这两类亚型与临床特征（如 hs-CRP、斑块稳定性、预后）进行关联分析，以挖掘更多机制或指导临床分类治疗。
</p>
''', unsafe_allow_html=True)



    # 6. PCA二维可视化
    st.markdown('<div class="subheader">PCA二维可视化</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    feature_cols = [col for col in ssgsea_clinical_df.columns if col not in ['immune_cluster', 'group_label']]
    features = ssgsea_clinical_df[feature_cols]
    immune_map = {i: chr(65+i) for i in ssgsea_clinical_df['immune_cluster'].unique()}
    cluster_palette = ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00']
    cluster_colors = {c: cluster_palette[i % len(cluster_palette)] for i, c in enumerate(sorted(immune_map.values()))}

    pca_2d = PCA(n_components=2)
    pca_2d_result = pca_2d.fit_transform(features)
    pca_2d_df = pd.DataFrame(pca_2d_result, columns=['PC1', 'PC2'], index=features.index)
    pca_2d_df['Immune Cluster'] = ssgsea_clinical_df['immune_cluster'].map(immune_map)
    pca_2d_df['Clinical Group'] = ssgsea_clinical_df['group_label'].map({0: 'Control', 1: 'CAD'})

    fig_2d = go.Figure()
    for cluster in sorted(pca_2d_df['Immune Cluster'].unique()):
        for group in sorted(pca_2d_df['Clinical Group'].unique()):
            df_sub = pca_2d_df[(pca_2d_df['Immune Cluster'] == cluster) & (pca_2d_df['Clinical Group'] == group)]
            fig_2d.add_trace(go.Scatter(
                x=df_sub['PC1'],
                y=df_sub['PC2'],
                mode='markers',
                name=f'{cluster} - {group}',
                marker=dict(
                    size=8,
                    opacity=0.8,
                    symbol='circle' if group == 'Control' else 'diamond',
                    color=cluster_colors[cluster]
                )
            ))
    fig_2d.update_layout(
        title="PCA 2D免疫亚型可视化",
        xaxis_title='PC1',
        yaxis_title='PC2',
        width=800,
        height=600
    )
    st.plotly_chart(fig_2d)

    # 7. PCA三维可视化
    st.markdown('<div class="subheader">PCA三维免疫亚型可视化</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    ssgsea_clinical_df['Immune Cluster'] = ssgsea_clinical_df['immune_cluster'].map(immune_map)
    ssgsea_clinical_df['Clinical Group'] = ssgsea_clinical_df['group_label'].map({0: 'Control', 1: 'CAD'})

    pca_3d = PCA(n_components=3)
    pca_3d_result = pca_3d.fit_transform(features)
    pca_3d_df = pd.DataFrame(pca_3d_result, columns=['PC1', 'PC2', 'PC3'], index=features.index)
    pca_3d_df['Immune Cluster'] = ssgsea_clinical_df['Immune Cluster']
    pca_3d_df['Clinical Group'] = ssgsea_clinical_df['Clinical Group']

    group_symbols = {'Control': 'circle', 'CAD': 'diamond'}

    fig3d = go.Figure()
    for cluster in sorted(pca_3d_df['Immune Cluster'].unique()):
        for group in sorted(pca_3d_df['Clinical Group'].unique()):
            df_sub = pca_3d_df[(pca_3d_df['Immune Cluster'] == cluster) & (pca_3d_df['Clinical Group'] == group)]
            fig3d.add_trace(go.Scatter3d(
                x=df_sub['PC1'], y=df_sub['PC2'], z=df_sub['PC3'],
                mode='markers',
                name=f'{cluster} - {group}',
                marker=dict(
                    color=cluster_colors[cluster],
                    size=4,
                    opacity=0.8,
                    symbol=group_symbols[group]
                )
            ))
    fig3d.update_layout(
        title="PCA 3D免疫亚型可视化",
        scene=dict(xaxis_title='PC1', yaxis_title='PC2', zaxis_title='PC3'),
        width=900, height=700
    )
    st.plotly_chart(fig3d)

    # 8. 保存数据
    ssgsea_clinical_df.to_csv("data/ssgsea_with_cluster.csv")
    st.success("✅ 已保存带有免疫亚型的信息至 data/ssgsea_with_cluster.csv")
