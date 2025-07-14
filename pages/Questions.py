import streamlit as st
import base64
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 页面配置
st.set_page_config(
    page_title="冠状动脉造影FAQ",
    layout="wide",
    page_icon="❓"
)

def get_base64_background(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
bg_path = os.path.join(BASE_DIR, "..", "data", "images", "bk.png")
bg_image = get_base64_background(bg_path)

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

# 自定义CSS样式
st.markdown("""
<style>
.faq-container {
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.faq-item {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border-left: 4px solid #2b7de9;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
}
.faq-item:hover {
    background: #e6f0ff;
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.faq-item:hover::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: #e6f0ff;
}
.faq-item h5 {
    color: #1d3557;
    margin-top: 0;
    margin-bottom: 0.2rem;
    display: flex;
    align-items: center;
}
.faq-item h5::before {
    content: "❓";
    margin-right: 10px;
    font-size: 1.2rem;
}
.faq-item p {
    color: #2d3748;
    margin-bottom: 0;
    line-height: 1.5;
}
@media (max-width: 768px) {
    .faq-item {
        padding: 1rem;
    }
}
.section-title {
    text-align: center;
    margin-bottom: 1rem;
    color: #1d3557;
    position: relative;
    padding-bottom: 1px;
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

# 页面标题
st.title("💬冠状动脉造影Q＆A")
st.markdown('<div class="section-title"></div>', unsafe_allow_html=True)

# FAQ数据
faq_data = [
    {
        "question": "检查前需要空腹吗？",
        "answer": "是的，一般在冠状动脉造影前需要空腹4至6小时，以减少术中误吸风险。这段时间内不应进食，也要避免饮水，除非医生有特别指示。"
    },
    {
        "question": "糖尿病患者能做造影吗？",
        "answer": "可以，但需要特殊准备。如你正在使用二甲双胍（Metformin）等口服降糖药，通常需要提前停药1-2天，避免术后肾功能损害。胰岛素患者可能需调整剂量。医生会根据你的具体情况做出安排。"
    },
    {
        "question": "检查后多久能恢复工作？",
        "answer": "大多数人在检查后1至3天内即可恢复轻度工作，如果伤口愈合良好、无不适症状。若你的工作需要剧烈活动或搬重物，建议根据医生建议延长休息时间至一周左右。"
    },
    {
        "question": "什么是'血管狭窄'？一定需要治疗吗？",
        "answer": "血管狭窄是指冠状动脉被斑块（脂质、钙等）堵塞变窄，导致心肌供血不足。并非所有狭窄都需要手术或支架治疗，是否需要进一步干预要结合症状、狭窄程度和心脏功能评估等综合判断。"
    },
    {
        "question": "上传图像后模型能直接告诉我有没有问题吗？",
        "answer": "AI模型会自动标出疑似狭窄区域，但不能给出'正常'或'异常'的明确诊断结论。图像的最终解释仍需要专业医生评估。AI模型的目的在于协助你理解图像，不替代医生。"
    },
    {
        "question": "使用AI图像分析功能是否有隐私风险？",
        "answer": "我们不会保存任何上传的图像或相关信息。所有图像处理都在本地或安全环境中完成，符合数据隐私保护要求，请放心使用。"
    }
]

# 创建双列并渲染FAQ
left_col, spacer, right_col = st.columns([1, 0.05, 1])

for idx, faq in enumerate(faq_data):
    col = left_col if idx % 2 == 0 else right_col
    with col:
        st.markdown(
            f"""
            <div class="faq-item">
                <h5>Q{idx+1}: {faq['question']}</h5>
                <p>{faq['answer']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# 附加信息
st.markdown("---")
st.info("""
**重要提示**：以上信息仅供参考，不能替代专业医疗建议。冠状动脉造影的具体准备和恢复要求可能因医院、患者状况不同而有所差异。
请务必遵循您的主治医生的具体指导。
""")

# 联系信息
with st.expander("📞 需要更多帮助？", expanded=False):
    st.markdown("""
    <div style="background-color: #e6f0ff; padding: 1rem; border-radius: 10px;">
        <h6 style="color: #1d3557; margin-top: 0;">同济大学生命科学与技术学院</h6>
        <p>📧 联系邮箱: <a href="mailto:2252775@tongji.edu.cn">2252775@tongji.edu.cn</a></p>
        <p>🕒 当前状态: 生物信息学专业本科生，欢迎咨询交流</p>
        <p>📍 所在地: 上海市杨浦区四平路街道1239号同济大学</p>
    </div>
    """, unsafe_allow_html=True)