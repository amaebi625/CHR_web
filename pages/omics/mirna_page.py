import streamlit as st
import pandas as pd
from scipy.stats import ttest_ind
import networkx as nx
import plotly.graph_objects as go
import os

# 中文显示设置
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False




def differential_expression(df, labels, group1='CHD', group2='Control'):
    group1_cols = [s for s, l in zip(df.columns, labels) if l == group1]
    group2_cols = [s for s, l in zip(df.columns, labels) if l == group2]
    results = []
    for gene in df.index:
        stat, p = ttest_ind(df.loc[gene, group1_cols], df.loc[gene, group2_cols], equal_var=False)
        logfc = df.loc[gene, group1_cols].mean() - df.loc[gene, group2_cols].mean()
        results.append([gene, logfc, p])
    df_out = pd.DataFrame(results, columns=["gene", "logFC", "pval"])
    df_out["adj_pval"] = df_out["pval"] * len(df_out)  # Bonferroni校正
    return df_out.sort_values("pval")


def load_miRTarBase_local(filepath="data/miRTarBase_MTI.csv"):
    mtb = pd.read_csv(filepath)
    mtb = mtb[mtb["Species (Target Gene)"] == "hsa"]
    return mtb[["miRNA", "Target Gene"]]


def build_network(de_mirna_sig, de_mrna_sig, mtb):
    demirnas = set(de_mirna_sig["gene"])
    deg_mrnas = set(de_mrna_sig["gene"])
    network_df = mtb[mtb["miRNA"].isin(demirnas) & mtb["Target Gene"].isin(deg_mrnas)]
    return network_df


def plot_network(network_df):
    G = nx.DiGraph()
    for _, row in network_df.iterrows():
        G.add_edge(row['miRNA'], row['Target Gene'])
    pos = nx.spring_layout(G, k=0.5, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines',
                            line=dict(width=1, color='#888'), hoverinfo='none')

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', text=node_text,
        textposition="top center", hoverinfo='text',
        marker=dict(color='skyblue', size=15, line_width=2, showscale=False)
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title="miRNA-mRNA 调控网络",
                        title_x=0.5, showlegend=False, hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    st.plotly_chart(fig, use_container_width=True)


def mirna_page(set_page_callback):
    st.markdown('<div style="text-align:right; margin-bottom:20px;">', unsafe_allow_html=True)
    if st.button("🔙 返回首页"):
        set_page_callback("main")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-title">miRNA-mRNA 调控网络分析</div>', unsafe_allow_html=True)

    st.markdown("""
        <style>
        .custom-title {
            font-size: 18px;
            color: #7E57C2;
            font-weight: 600;
            margin-top: 10px;
            margin-bottom: 5px;
        }
        .stRadio > div {
            flex-direction: row;
        }
        .btn-instruction {
            font-size: 16px;
            color: #7E57C2;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 数据来源选择
    st.markdown('<div class="custom-title">选择数据来源：</div>', unsafe_allow_html=True)
    data_mode = st.radio("", ["使用本地数据", "上传自定义数据"], horizontal=True)

    mirna_df = mirna_meta = mrna_df = mrna_meta = None

    if data_mode == "使用本地数据":
        st.info("从内置本地数据集中选择：")

        mirna_datasets = {
            "无": (None, None),
            "本地miRNA-seq数据集": ("data/GSE105449_miRNA_expr_scaled.csv", "data/GSE105449_sample_group.csv")
        }

        mrna_datasets = {
            "无": (None, None),
            "本地mRNA-seq数据集": ("data/GSE12288_gene_expr_scaled.csv", "data/GSE12288_sample_group.csv")
        }

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="custom-title">选择 miRNA 数据集：</div>', unsafe_allow_html=True)
            mirna_choice = st.selectbox("", list(mirna_datasets.keys()))
        with col2:
            st.markdown('<div class="custom-title">选择 mRNA 数据集：</div>', unsafe_allow_html=True)
            mrna_choice = st.selectbox("", list(mrna_datasets.keys()))

        mirna_expr_path, mirna_meta_path = mirna_datasets[mirna_choice]
        mrna_expr_path, mrna_meta_path = mrna_datasets[mrna_choice]

        if mirna_expr_path and mrna_expr_path:
            mirna_df = pd.read_csv(mirna_expr_path, index_col=0)
            mirna_meta = pd.read_csv(mirna_meta_path)
            mrna_df = pd.read_csv(mrna_expr_path, index_col=0)
            mrna_meta = pd.read_csv(mrna_meta_path)

    else:
        st.info("上传自定义表达数据和分组信息：")
        col1, col2 = st.columns(2)
        with col1:
            mirna_expr_file = st.file_uploader("上传 miRNA表达矩阵", type=["csv"], key="mirna_expr")
            mirna_meta_file = st.file_uploader("上传 miRNA分组信息", type=["csv"], key="mirna_meta")
        with col2:
            mrna_expr_file = st.file_uploader("上传 mRNA表达矩阵", type=["csv"], key="mrna_expr")
            mrna_meta_file = st.file_uploader("上传 mRNA分组信息", type=["csv"], key="mrna_meta")

        if all([mirna_expr_file, mirna_meta_file, mrna_expr_file, mrna_meta_file]):
            mirna_df = pd.read_csv(mirna_expr_file, index_col=0)
            mirna_meta = pd.read_csv(mirna_meta_file)
            mrna_df = pd.read_csv(mrna_expr_file, index_col=0)
            mrna_meta = pd.read_csv(mrna_meta_file)

    # 数据预处理和网络构建按钮
    if all([mirna_df is not None, mirna_meta is not None, mrna_df is not None, mrna_meta is not None]):
        mirna_df.columns = mirna_df.columns.str.strip().str.upper()
        mrna_df.columns = mrna_df.columns.str.strip().str.upper()
        mirna_meta["geo_accession"] = mirna_meta["geo_accession"].str.strip().str.upper()
        mrna_meta["geo_accession"] = mrna_meta["geo_accession"].str.strip().str.upper()

        mirna_meta = mirna_meta[mirna_meta["geo_accession"].isin(mirna_df.columns)]
        mrna_meta = mrna_meta[mrna_meta["geo_accession"].isin(mrna_df.columns)]

        mirna_meta = mirna_meta.set_index("geo_accession").loc[mirna_df.columns]
        mrna_meta = mrna_meta.set_index("geo_accession").loc[mrna_df.columns]

        mirna_labels = mirna_meta["group"].tolist()
        mrna_labels = mrna_meta["group"].tolist()

        st.write("miRNA组别分布：", pd.Series(mirna_labels).value_counts().to_dict())
        st.write("mRNA组别分布：", pd.Series(mrna_labels).value_counts().to_dict())

        if st.button("构建并绘制调控网络"):
            with st.spinner("进行差异分析并构建网络..."):
                de_mirna = differential_expression(mirna_df, mirna_labels)
                de_mrna = differential_expression(mrna_df, mrna_labels)

                N = 10
                de_mirna_sig = pd.concat([de_mirna.sort_values("logFC", ascending=False).head(N),
                                          de_mirna.sort_values("logFC", ascending=True).head(N)])
                de_mrna_sig = pd.concat([de_mrna.sort_values("logFC", ascending=False).head(N),
                                         de_mrna.sort_values("logFC", ascending=True).head(N)])

                mtb = load_miRTarBase_local()
                network_df = build_network(de_mirna_sig, de_mrna_sig, mtb)

            st.write(f"调控网络边数：{len(network_df)}")
            st.dataframe(network_df)

            st.markdown('<div class="subheader">miRNA-mRNA调控网络图</div>', unsafe_allow_html=True)

            plot_network(network_df)

            st.markdown('<div class="subheader">调控网络解读</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="btn-instruction" style="color:#7E57C2; font-size:16px; margin-top:10px;">
    <ol style="padding-left: 20px; line-height: 1.8;">
        <li><b>中心节点 hsa-miR-1305 与 hsa-miR-543</b><br>
            这两个 miRNA 与多个 mRNA 发生调控关系，是网络中的高连接度节点（degree hub），说明它们可能是关键的转录后调控因子。<br>
            hsa-miR-1305、hsa-miR-543 参与调控的 mRNA 涉及免疫、炎症、代谢等过程，在冠心病发病机制中可能具有广泛的调控作用。
        </li>
        <li><b>被调控的关键 mRNA</b><br>
            如 CEBPA（与炎症细胞分化、脂代谢密切相关）被 hsa-miR-139-3p 调控；<br>
            PAPOLA、TMED10、ZNF518A 等可能与RNA修饰、囊泡运输、转录因子活性相关；<br>
            多数下游基因为差异表达的 mRNA，表明 miRNA 调控可能直接影响炎症信号通路、细胞激活等功能。
        </li>
        <li><b>网络连通性说明调控轴可能形成协同效应</b><br>
            多个 miRNA 可调控同一个 mRNA（如 PAPOLA 被 hsa-miR-28-3p 与 hsa-miR-1305 调控）；<br>
            多个 mRNA 也可受到同一 miRNA 调控（如 hsa-miR-1305 → ITPK1、PAPOLA、NCAPH）；<br>
            表明 miRNA 网络在调控过程中具有冗余性和复杂的反馈调节机制。
        </li>
    </ol>
</div>
""", unsafe_allow_html=True)

    else:
        st.warning("请确保完整加载表达数据与分组信息。")



