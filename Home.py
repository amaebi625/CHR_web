import streamlit as st
import pandas as pd
import math
from pathlib import Path
import altair as alt

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='🫀"冠心"呵护',
    layout='centered'
     # This is an emoji shortcode. Could be a URL too.
)

# 添加自定义CSS样式
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #a5d8ff , white) !important;
        color: black;
    }
    .stButton {
        background-color: #4287f5;
        color: white;
    }
    .card {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .intro-text {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    .highlight {
        font-weight: bold;
        color: #1E88E5;
    }
    .stat-highlight {
        font-weight: bold;
        color: #e53935;
    }
    .chart-container {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    .section-header {
        margin-top: 30px;
        margin-bottom: 15px;
        color: #333;
        border-bottom: 2px solid #a5d8ff;
        padding-bottom: 5px;
    }
    /* 修改所有Streamlit控件标签的颜色 */
    .stSlider label, .stMultiselect label, div[data-testid="stMultiSelect"] label, div[data-baseweb="select"] label, .st-bq, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj {
        color: black !important;
        font-weight: 500 !important;
    }
    
    /* 增大左侧边栏文字大小 */
    [data-testid="stSidebar"] .css-pkbazv, [data-testid="stSidebar"] .css-uc76bn,
    [data-testid="stSidebar"] a, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li, [data-testid="stSidebar"] ul,
    [data-testid="stSidebar"] .css-eczf16, [data-testid="stSidebar"] .css-jcn9zf {
        font-size: 26px !important; /* 字体大小从18px增加到26px */
        font-weight: 500 !important;
        color: white!important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
    }
    
    /* 增强边栏项目的悬停效果 */
    [data-testid="stSidebar"] a:hover, [data-testid="stSidebar"] li:hover {
        background-color: rgba(255,255,255,0.2) !important;
        border-radius: 5px !important;
        color: #ffffff !important;
    }

    /* 1. 让页面内容最大宽度变宽 */
    main .block-container {
        max-width: 1200px !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* 2. 可选：让标题更大、更居中 */
    h1 {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
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

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_chd_mortality_data():
    """获取冠心病死亡率数据。

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # 读取CSV文件
    DATA_FILENAME = Path(__file__).parent/'data/chd_mortality_data.csv'
    raw_chd_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 2002
    MAX_YEAR = 2021

    # 将年份列转换为行
    chd_df = raw_chd_df.melt(
        ['Region Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'Mortality',
    )

    # 将年份从字符串转换为整数
    chd_df['Year'] = pd.to_numeric(chd_df['Year'])

    return chd_df

chd_df = get_chd_mortality_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
st.markdown("""
<style>
.hero-container {
    max-width: 960px;
    margin: 0 auto 2rem auto;
    padding: 2.2rem 2rem 2.2rem 2rem;
    background: rgba(255, 255, 255, 0.28);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    backdrop-filter: blur(10px);
    text-align: center;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
    color: #3c1d50;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: #4B4453;
    font-weight: 500;
    line-height: 1.6;
}
</style>

<div class="hero-container">
    <h1 class="hero-title">🫀 “冠心”呵护 · 智慧诊疗平台</h1>
    <p class="hero-subtitle">聚焦冠心病预防、评估与治疗，为每一颗心脏提供数据驱动的精准守护。</p>
</div>
""", unsafe_allow_html=True)




# 添加引言卡片
st.markdown("""
<style>
.intro-container {
    max-width: 880px;
    margin: 0 auto;
    padding: 1rem 2rem 2.5rem 2rem;
    color: #2F2D34;
    font-size: 1.05rem;
    line-height: 1.8;
}

.intro-container b {
    color: #7D3C98; /* 深紫色强调 */
}

.intro-container ul {
    padding-left: 1.5rem;
    margin-top: 0.8rem;
    margin-bottom: 1.5rem;
}

.intro-container li {
    margin-bottom: 0.5rem;
}
</style>

<div class="intro-container">

<p>每一次心跳，都是生命的声音。</p>

<p>
近年来，心血管疾病已连续多年位居我国居民死亡原因首位，其中 <b>冠心病</b> 所占比例超过 <b style="color:#d3342d;">40%</b>，每年约有 <b style="color:#d3342d;">330万人</b> 因此失去生命，形势十分严峻。
</p>

<p>
面对不断增长的疾病负担，我们创建了 <b>“冠心呵护”</b> 诊疗平台，致力于让心血管健康管理更早期、更智能、更个性化。
</p>

<p>在这里，您可以：</p>

<ul>
  <li>通过 <b>风险自评问卷</b> 初步了解自身心血管健康状况</li>
  <li>借助 <b>CMR 智能影像分析</b> 预测结构异常与功能减退</li>
  <li>整合 <b>前沿组学</b> 数据，探索个体化心脏病风险因子</li>
  <li>借助 <b>知识图谱</b> 全面了解病因、路径与治疗手段</li>
</ul>

<p>
我们相信，技术应服务于精准预防与早期干预。<br>
“冠心呵护”，以数据为眼，智能为脑，守护每一颗跳动的心。
</p>

</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 添加数据分析过渡文字
st.markdown('<h3 class="section-header">冠心病死亡率数据趋势分析</h3>', unsafe_allow_html=True)
st.markdown('<p>以下图表展示了中国城市与乡村冠心病死亡率的历史变化趋势，帮助我们更好地理解冠心病的流行病学特征。</p>', unsafe_allow_html=True)

# 数据筛选控件
col1, col2 = st.columns([2, 1])

with col1:
    min_value = chd_df['Year'].min()
    max_value = chd_df['Year'].max()

    from_year, to_year = st.slider(
        '您想查看哪些年份的数据？',
        min_value=min_value,
        max_value=max_value,
        value=[min_value, max_value])

with col2:
    regions = chd_df['Region Code'].unique()

    if not len(regions):
        st.warning("至少选择一个地区")

    selected_regions = st.multiselect(
        '您想查看哪些地区的数据？',
        regions,
        ['URBAN', 'RURAL'])

# Filter the data
filtered_chd_df = chd_df[
    (chd_df['Region Code'].isin(selected_regions))
    & (chd_df['Year'] <= to_year)
    & (from_year <= chd_df['Year'])
]

# 绘制图表
if not filtered_chd_df.empty:
    # 创建自定义颜色映射
    color_scale = alt.Scale(
        domain=['URBAN', 'RURAL'],
        range=['#FF5252', '#2196F3']  # 红色和蓝色，对比度更高
    )
    
    # 创建图表
    chart = alt.Chart(filtered_chd_df).mark_line(point=True).encode(
        x=alt.X('Year:Q', title='年份'),
        y=alt.Y('Mortality:Q', title='死亡率'),
        color=alt.Color('Region Code:N', scale=color_scale, legend=alt.Legend(
            title='地区',
            labelFontSize=12,
            titleFontSize=14
        )),
        tooltip=['Year:Q', 'Mortality:Q', 'Region Code:N']
    ).properties(
        width='container',
        height=400
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        strokeWidth=0
    )
    
    # 显示图表
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("没有符合条件的数据可显示")
st.markdown('</div>', unsafe_allow_html=True)
