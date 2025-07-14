import streamlit as st
import pandas as pd
import numpy as np
import requests
import networkx as nx
import plotly.graph_objects as go
from scipy.stats import mannwhitneyu
from community import community_louvain
from Bio import Entrez
import os
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体（Windows常见）
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题


Entrez.email = "225523@tongji.edu.cn"

def get_string_ppi(gene_list, species=9606, score=700):
    gene_str = "%0d".join(gene_list)
    url = "https://string-db.org/api/tsv/network"
    params = {
        "identifiers": gene_str,
        "species": species,
        "required_score": score,
        "caller_identity": "streamlit_app"
    }
    response = requests.post(url, data=params)
    if response.status_code != 200:
        st.error("STRING API 请求失败")
        return None
    data = [line.split("\t") for line in response.text.strip().split("\n")]
    df = pd.DataFrame(data[1:], columns=data[0])
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    return df.dropna(subset=['score'])

def plot_ppi_network(ppi_df, color_mode='community'):
    G = nx.from_pandas_edgelist(ppi_df, 'preferredName_A', 'preferredName_B', edge_attr='score')
    degrees = dict(G.degree())
    try:
        partition = community_louvain.best_partition(G, weight='score')
    except:
        partition = {node: 0 for node in G.nodes()}
    pos = nx.spring_layout(G, k=0.3, weight='score', seed=42)

    node_x, node_y, node_text, node_size, node_color, node_names = [], [], [], [], [], []
    max_degree = max(degrees.values()) if degrees else 1
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_names.append(node)
        deg = degrees[node]
        node_text.append(f"<b>{node}</b><br>Degree: {deg}")
        node_size.append(20 + 30 * (deg / max_degree))
        node_color.append(deg if color_mode == 'degree' else partition.get(node, 0))

    edge_x, edge_y = [], []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig = go.Figure(data=[
        go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=0.5, color='#888'), hoverinfo='none'),
        go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_names,
            textposition='top center',
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                showscale=True,
                colorscale='Rainbow' if color_mode == 'degree' else 'Viridis',
                color=node_color,
                size=node_size,
                colorbar=dict(title='节点度数' if color_mode == 'degree' else '社区分区'),
                line=dict(width=1, color='black')
            )
        )
    ], layout=go.Layout(
        title='<b>STRING PPI 网络</b>',
        showlegend=False, hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=800
    ))
    st.plotly_chart(fig)

def get_hub_genes(ppi_df, top_n=5):
    G = nx.from_pandas_edgelist(ppi_df, 'preferredName_A', 'preferredName_B', edge_attr='score')
    degrees = dict(G.degree())
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
    return sorted_degrees[:top_n]

def query_dgidb_interactions(gene_names):
    genes_str = ', '.join(f'"{g}"' for g in gene_names)
    query = f"""
    query {{
      genes(names: [{genes_str}]) {{
        edges {{
          node {{
            name
            interactions {{
              interactionTypes {{ type definition }}
              sources {{ sourceDbName }}
              drug {{ name }}
            }}
          }}
        }}
      }}
    }}
    """
    url = "https://dgidb.org/api/graphql"
    response = requests.post(url, json={'query': query})
    if response.status_code != 200 or 'errors' in response.json():
        return pd.DataFrame()

    data = response.json()['data']['genes']['edges']
    records = []
    for edge in data:
        gene = edge['node']['name']
        for inter in edge['node']['interactions']:
            records.append({
                'gene': gene,
                'drug': inter['drug']['name'] if inter['drug'] else None,
                'interaction_types': "; ".join(f"{i['type']}({i['definition']})" for i in inter['interactionTypes']),
                'sources': "; ".join(s['sourceDbName'] for s in inter['sources'])
            })
    return pd.DataFrame(records)

def search_pubmed(gene, disease="coronary heart disease", max_results=5):
    query = f"{gene}[Title/Abstract] AND {disease}[Title/Abstract]"
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    return record["IdList"]

def fetch_abstracts(id_list):
    if not id_list:
        return "No results found.\n"
    handle = Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="abstract", retmode="text")
    return handle.read()

immune_targets_chd = [
    'IL1B', 'IL6', 'IL10', 'TNF', 'TGFB1', 'IFNG',
    'CXCL8', 'CXCL10', 'CCL2', 'CCL5', 'CCR2', 'CCR5',
    'PDCD1', 'CD274', 'CTLA4', 'LAG3', 'TIGIT',
    'CD3D', 'CD4', 'CD8A', 'FOXP3', 'TBX21', 'GZMB',
    'STAT1', 'STAT3', 'TYK2', 'JAK1', 'JAK2', 'IRF7',
    'IL1R1', 'TLR2', 'TLR4', 'NLRP3',
    'CD28', 'ICOS', 'CD40', 'CD80', 'CD86',
    'CD68', 'CD163',
    'MMP9', 'S100A8', 'S100A9', 'NFKB1'
]

def target_page(set_page_callback):
    st.markdown("""
    <style>
    .main-title {
        font-size: 28px;
        color: #9b59b6;  /* 粉紫色 */
        font-weight: bold;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 20px;
        color: #ba96d3;  /* 柔和粉紫 */
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .btn-instruction {
        font-size: 16px;
        color: #8e44ad;  /* 深粉紫 */
        margin-bottom: 10px;
    }
    .pubmed-abstract {
        font-size: 14px;
        color: #555555;
        white-space: pre-wrap;
        background-color: #f4e6fc;  /* 淡紫背景 */
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
        font-family: "Microsoft YaHei", Arial, sans-serif;
    }
    /* Streamlit按钮美化 */
    div.stButton > button {
        font-size: 16px;
        background-color: #af7ac5;  /* 按钮紫色 */
        color: white;
        border-radius: 8px;
        padding: 8px 18px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">冠心病免疫靶点识别分析</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align:right; margin-bottom:20px;">', unsafe_allow_html=True)
    if st.button("🔙 返回首页"):
        set_page_callback("main")
    st.markdown('</div>', unsafe_allow_html=True)

    expr_df, clin_df = None, None

    # 根据全局session状态加载数据
    if 'data_source' in st.session_state:
        if st.session_state['data_source'] == "builtin":
            expr_path = st.session_state.get('expr_path', None)
            group_path = st.session_state.get('group_path', None)
            if expr_path and group_path:
                expr_df = pd.read_csv(expr_path, index_col=0)
                clin_df = pd.read_csv(group_path, index_col=0)
        elif st.session_state['data_source'] == "upload":
            uploaded_expr = st.session_state.get('uploaded_expr', None)
            uploaded_group = st.session_state.get('uploaded_group', None)
            if uploaded_expr and uploaded_group:
                uploaded_expr.seek(0)
                uploaded_group.seek(0)
                sep_expr = "\t" if uploaded_expr.name.endswith(".tsv") else ","
                sep_group = "\t" if uploaded_group.name.endswith(".tsv") else ","
                expr_df = pd.read_csv(uploaded_expr, sep=sep_expr, index_col=0)
                clin_df = pd.read_csv(uploaded_group, sep=sep_group, index_col=0)
    else:
        st.warning("请先在首页加载或上传表达矩阵和临床分组数据")

    if expr_df is not None and clin_df is not None:
        st.success(f"表达矩阵形状：{expr_df.shape}，临床分组形状：{clin_df.shape}")

        if st.button("① PPI 网络绘制和 Hub 基因识别", key="btn_ppi_hub"):
            gene_map = dict(zip(expr_df.index.str.upper(), expr_df.index))
            targets_found = [gene_map[g.upper()] for g in immune_targets_chd if g.upper() in gene_map]
            if not targets_found:
                st.warning("表达矩阵中未找到靶点基因")
            else:
                expr_sub = expr_df.loc[targets_found].T
                common_samples = expr_sub.index.intersection(clin_df.index)
                expr_sub = expr_sub.loc[common_samples]
                clin_sub = clin_df.loc[common_samples]

                # 差异分析
                pvals = {}
                for gene in expr_sub.columns:
                    group1_data = expr_sub[clin_sub['group'] == 'CHD'][gene]
                    group0_data = expr_sub[clin_sub['group'] == 'Control'][gene]
                    if len(group1_data) == 0 or len(group0_data) == 0:
                        pvals[gene] = np.nan
                    else:
                        pvals[gene] = mannwhitneyu(group1_data, group0_data).pvalue

                pval_series = pd.Series(pvals).sort_values()
                top_targets = pval_series.head(20).index.tolist()
                st.session_state['top_targets'] = top_targets

                # 构建和绘制 PPI 网络
                ppi_df = get_string_ppi(top_targets)
                if ppi_df is not None and not ppi_df.empty:
                    st.session_state['ppi_df'] = ppi_df
                    plot_ppi_network(ppi_df, color_mode='degree')


                    # 提取 Hub 基因
                    hub_genes = get_hub_genes(ppi_df, top_n=5)
                    hub_names = [g[0] for g in hub_genes]
                    st.session_state['hub_genes'] = hub_names
                    st.success(f"Hub 基因: {', '.join(hub_names)}")
                else:
                    st.warning("未能获取PPI数据或数据为空")

                st.markdown('<div class="subheader">Hub基因分析</div>', unsafe_allow_html=True)
                st.markdown("""
<style>
  .hub-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    margin-bottom: 20px;
    font-family: "Microsoft YaHei", Arial, sans-serif;
    font-size: 13px; 
  }
  .hub-table th, .hub-table td {
    border: 1px solid #ddd;
    padding: 10px;
    vertical-align: top;
  }
  .hub-table th {
    background-color: #af7ac5;  /* 紫色表头 */
    color: white;
    font-weight: bold;
    text-align: left;
  }
  .hub-table tr:nth-child(even) {
    background-color: #f9f5fb;
  }
</style>

<table class="hub-table">
  <thead>
    <tr>
      <th>Hub基因</th>
      <th>功能</th>
      <th>意义</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>TNF（Tumor Necrosis Factor）</b></td>
      <td>炎症因子，激活NF-κB通路，调控细胞凋亡、炎症和免疫反应。</td>
      <td>TNF在动脉粥样硬化斑块形成及稳定性中起关键作用，其高连接度提示其为炎症驱动型冠心病的重要调控因子，是经典的抗炎靶点（如抗TNF药物用于风湿免疫疾病）。</td>
    </tr>
    <tr>
      <td><b>CD8A</b></td>
      <td>细胞毒性T细胞（CTL）标志分子，参与识别并杀伤病毒感染细胞和肿瘤细胞。</td>
      <td>CD8A的上调可能提示细胞毒性T细胞活性增强，在冠心病慢性炎症背景下，这种免疫活化可能加剧内皮损伤。</td>
    </tr>
    <tr>
      <td><b>IL6（Interleukin 6）</b></td>
      <td>经典促炎因子，参与急性期反应、B细胞分化和T细胞极化。</td>
      <td>IL6在动脉粥样硬化、心肌损伤和炎性反应中广泛表达，是潜在的炎症生物标志物和治疗靶点（如IL6抑制剂Tocilizumab被研究用于心血管疾病）。</td>
    </tr>
  </tbody>
</table>
""", unsafe_allow_html=True)

        
        # 药物推荐与PubMed摘要按钮
        if st.button("② 药物推荐与PubMed摘要", key="btn_drug_pubmed"):
            if 'hub_genes' in st.session_state and 'top_targets' in st.session_state:
                hub_names = st.session_state['hub_genes']
                top_targets = st.session_state['top_targets']
                dgidb = query_dgidb_interactions(top_targets)
                dgidb_filtered = dgidb[dgidb['gene'].isin(hub_names)]

                st.markdown('<div class="subheader"> 药物发现（Hub基因）</div>', unsafe_allow_html=True)
                st.dataframe(dgidb_filtered)
                #st.markdown('<div class="btn-instruction">药物备注...</div>', unsafe_allow_html=True)
                # 保存CSV
                os.makedirs("data", exist_ok=True)
                dgidb_filtered.to_csv("data/recommended_immune_targets.csv", index=False)

                st.markdown('<div class="subheader"> PubMed 文献摘要（Top5示例）</div>', unsafe_allow_html=True)
                os.makedirs("data", exist_ok=True)
                with open("data/pubmed_abstracts.txt", "w", encoding="utf-8") as f:
                    for gene in top_targets:
                        ids = search_pubmed(gene)
                        abstracts = fetch_abstracts(ids)
                        entry = f"=== Gene: {gene} ===\n{abstracts}\n\n"
                        f.write(entry)
                        if gene in top_targets[:5]:
                            with st.expander(f" {gene} 相关文献摘要"):
                                st.markdown(f'<div class="pubmed-abstract">{entry}</div>', unsafe_allow_html=True)
                st.success("所有摘要已保存至 data/pubmed_abstracts.txt")
            else:
                st.warning("请先完成差异表达分析和PPI网络绘制")
    

    else:
        st.info("等待上传或加载表达矩阵和临床分组数据")



