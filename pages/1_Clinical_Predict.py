import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# 设置页面标题
st.set_page_config(page_title="🫀冠心病风险预测系统", layout="wide")

# 添加自定义CSS样式
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, white, #a5d8ff) !important;
        color: black;
    }
    .stMarkdown, .stText, p, div, h1, h2, h3, h4, h5, h6, li, span {
        color: black !important;
        font-size: 18px !important;
    }
    /* 使用更强的选择器和!important标记 */
    h1, .stTitle h1, div.stTitle > h1, [data-testid="stTitle"] h1, .stMarkdown h1 {
        font-size: 60px !important;
        font-weight: bold !important;
        color: black !important;
        text-align: left !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 直接针对markdown生成的h1标签 */
    .element-container div.stMarkdown h1 {
        font-size: 60px !important;
        font-weight: bold !important;
    }
    /* 使用更强的选择器确保标题样式被应用 */
    .stTitle, .stTitle h1, div.stTitle > h1, [data-testid="stTitle"] h1 {
        color: black !important;
        font-size: 60px !important;  /* 进一步增大标题字体 */
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 20px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1) !important;
    }
    .stHeader {
        color: black !important;
        font-size: 28px !important;
    }
    .stSubheader {
        color: black !important;
        font-size: 22px !important;
    }
    .stButton button {
        font-size: 22px !important;
        margin-top: 10px !important;  /* 调整按钮位置 */
    }
    .stRadio label, .stCheckbox label, .stSelectbox label {
        font-size: 18px !important;
        color: black !important;
    }
    .stSlider label {
        font-size: 18px !important;
        color: black !important;
    }
    /* 下拉选框样式 - 更全面的选择器 */
    /* 选择框本身 */
    .stSelectbox > div > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div {
        background-color: white !important;
        color: black !important;
        font-size: 18px !important;
        font-weight: 500 !important;
    }
    
    /* 下拉菜单容器 */
    div[role="listbox"],
    ul[role="listbox"],
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[data-baseweb="select"] + div {
        background-color: white !important;
        color: black !important;
    }
    
    /* 下拉菜单选项 */
    div[role="option"],
    li[role="option"],
    div[data-testid="stSelectbox"] li,
    div[data-testid="stSelectbox"] ul li {
        background-color: white !important;
        color: black !important;
        font-size: 18px !important;
    }
    
    /* 下拉菜单选项悬停状态 */
    div[role="option"]:hover,
    li[role="option"]:hover,
    div[data-testid="stSelectbox"] li:hover,
    div[data-testid="stSelectbox"] ul li:hover {
        background-color: #f0f0f0 !important;
    }
    
    /* 确保所有弹出菜单都有白色背景 */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background-color: white !important;
    }
    
    /* 强制所有文本为黑色 */
    div[data-baseweb="select"] span,
    div[role="option"] span,
    li[role="option"] span,
    div[data-testid="stSelectbox"] span {
        color: black !important;
        font-size: 18px !important;
        font-weight: 500 !important;
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

# 加载模型
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "config", "best_model_pipeline.pkl")
@st.cache_resource
def load_model(model):
    return joblib.load(model)

model = load_model(model_path)

st.markdown("""<h1 style='font-size: 60px !important; font-weight: bold !important; text-align: left !important; color: black !important; margin: 0 !important; padding: 0 !important; display: block !important;'>🫀冠心病风险预测系统</h1>""", unsafe_allow_html=True)
st.write("请输入患者的特征信息，系统将预测未来10年内患有冠心病的风险。")

# 创建两列布局
col1, col2 = st.columns(2)

# 第一列的输入字段
with col1:
    st.subheader("基本信息")
    age = st.slider("年龄", 0, 90, 50)
    sex = st.radio("性别", ["男", "女"])
    sex_encoded = 1 if sex == "男" else 0
    
    # 添加教育程度选择
    education_options = {"小学及以下": 1.0, "初中": 2.0, "高中": 3.0, "大学及以上": 4.0}
    education = st.selectbox("教育程度", list(education_options.keys()))
    education_encoded = education_options[education]
    
    st.subheader("生活习惯")
    current_smoker = st.checkbox("是否吸烟")
    cigs_per_day = st.slider("每天吸烟数量", 0, 70, 0) if current_smoker else 0

# 第二列的输入字段
with col2:
    st.subheader("医学指标")
    bp_meds = st.checkbox("是否服用降压药")
    prevalent_stroke = st.checkbox("是否有过中风")
    prevalent_hyp = st.checkbox("是否有高血压")
    diabetes = st.checkbox("是否有糖尿病")
    tot_chol = st.slider("总胆固醇 (mg/dL)", 100, 600, 200)
    sys_bp = st.slider("收缩压 (mmHg)", 80, 300, 120)
    dia_bp = st.slider("舒张压 (mmHg)", 40, 150, 80)
    bmi = st.slider("体重指数 (BMI)", 15.0, 50.0, 25.0)
    heart_rate = st.slider("心率 (次/分钟)", 40, 150, 75)
    glucose = st.slider("血糖 (mg/dL)", 40, 400, 80)

# 预测按钮
if st.button("开始预测", type="primary"):
    # 创建输入数据框
    # 修改输入数据框部分（大约在第56行附近）
    input_data = pd.DataFrame({
    'age': [age],
    'education': [education_encoded],
    'sex': ['M' if sex == "男" else 'F'],  # 使用与训练数据相同的编码
    'is_smoking': ['YES' if current_smoker else 'NO'],  # 使用与训练数据相同的编码
    'cigsPerDay': [cigs_per_day],
    'BPMeds': [1 if bp_meds else 0],
    'prevalentStroke': [1 if prevalent_stroke else 0],
    'prevalentHyp': [1 if prevalent_hyp else 0],
    'diabetes': [1 if diabetes else 0],
    'totChol': [tot_chol],
    'sysBP': [sys_bp],
    'diaBP': [dia_bp],
    'BMI': [bmi],
    'heartRate': [heart_rate],
    'glucose': [glucose]
})
    
    # 进行预测
    prediction_proba = model.predict_proba(input_data)[0, 1]
    prediction = model.predict(input_data)[0]
    
    # 显示结果
    st.header("预测结果")
    
    # 创建进度条显示风险概率
    st.write(f"患冠心病风险概率: {prediction_proba:.2%}")
    st.progress(prediction_proba)
    
    # 根据不同风险级别显示不同颜色的结果
    if prediction == 1:
        st.error("⚠️ 高风险: 该患者未来10年内患冠心病的风险较高。")
        if current_smoker:
            st.write("建议: 请尽快咨询医生，并考虑改变您的生活方式，如控制饮食、增加运动、戒烟限酒等。")
        else:
            st.write("建议: 请咨询医生，平时多注意运动，规律饮食。")

    else:
        st.success("✅ 低风险: 该患者未来10年内患冠心病的风险较低。")
        st.write("建议: 继续保持健康的生活方式，同时也要养成定期体检的好习惯哦。")
    
    # 显示影响因素
    st.subheader("主要风险因素分析")
    
    risk_factors = []
    if age > 55: risk_factors.append("年龄偏高")
    if current_smoker: risk_factors.append("吸烟")
    if tot_chol > 240: risk_factors.append("高胆固醇")
    if sys_bp > 140 or dia_bp > 90: risk_factors.append("高血压")
    if bmi > 30: risk_factors.append("肥胖")
    if diabetes: risk_factors.append("糖尿病")
    if prevalent_stroke: risk_factors.append("既往中风史")
    
    if risk_factors:
        st.write("您的主要风险因素包括: " + ", ".join(risk_factors))
    else:
        st.write("未检测到明显风险因素。")

# 添加页脚
st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
st.caption("注意：本系统仅供参考，不能替代专业医生的诊断。如有健康问题，请咨询专业医疗人员。")
