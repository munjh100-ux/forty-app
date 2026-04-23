import streamlit as st
import time
import matplotlib.pyplot as plt
import numpy as np

# --- 1. 환경 및 스타일 설정 ---
plt.rcParams['font.family'] = 'Malgun Gothic' # Windows 기준
plt.rcParams['axes.unicode_minus'] = False

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .persona-card {
        background: linear-gradient(135deg, #6C63FF 0%, #3F3D56 100%);
        padding: 40px; border-radius: 25px; color: white; text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15); margin-bottom: 25px;
    }
    .analysis-box {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 5px solid #6C63FF; margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .match-container { display: flex; gap: 15px; margin-top: 10px; }
    .match-card {
        flex: 1; background-color: white; padding: 20px; border-radius: 20px;
        border: 2px solid #eef0f5; text-align: center; transition: 0.3s;
    }
    .match-card:hover { border-color: #6C63FF; transform: translateY(-5px); }
    .strength-tag { color: #2E7D32; font-weight: bold; font-size: 0.9rem; }
    .weakness-tag { color: #D32F2F; font-weight: bold; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 코어 엔진 (V4.7) ---
class FortyEngineV47:
    def __init__(self):
        self.clusters_x = ["INF", "INT", "ENF", "ENT", "ISJ", "ISP", "ESJ", "ESP"]
        
        # 성격 군집 간 상보적 파트너 맵 (심리학적 반대 성향)
        self.match_logic = {
            "INF": "ENT", "ENT": "INF", "INT": "ENF", "ENF": "INT",
            "ISJ": "ESP", "ESP": "ISJ", "ISP": "ESJ", "ESJ": "ISP"
        }

        # 40가지 페르소나 데이터베이스
        # 구조: [극우/보수성향높음 -> 극좌/진보성향높음] 순서 5단계
        self.db = {
            "ENT": [
                {"title": "강철의 지배자", "s": "압도적인 리더십과 위기 돌파력", "w": "가끔 속도가 너무 빨라 팀원들이 숨차 함"},
                {"title": "냉철한 경영자", "s": "효율을 극대화하는 데이터 기반 결정", "w": "사람의 마음을 숫자로만 판단하려는 경향"},
                {"title": "실용적 전략가", "s": "이념보다 실리를 택하는 천재적 협상가", "w": "상황에 따라 입장이 바뀌는 유연함(이라 쓰고 변덕)"},
                {"title": "변화의 설계자", "s": "논리적 근거로 무장한 시스템 개혁가", "w": "비판이 너무 날카로워 스스로 지칠 때가 있음"},
                {"title": "급진적 기획자", "s": "기존 질서를 뒤엎는 파괴적 창조성", "w": "브레이크 없는 탱크처럼 전진해 주변을 놀래킴"}
            ],
            "INT": [
                {"title": "독고다이 참모", "s": "치밀한 리스크 관리와 심층 분석", "w": "혼자만의 동굴이 너무 깊어 소통 단절 주의"},
                {"title": "논리적 현실주의자", "s": "빈틈없는 팩트 체크와 객관적 판단", "w": "사소한 오류에도 예민해지는 완벽주의"},
                {"title": "심층 분석가", "s": "현상의 근원을 꿰뚫는 통찰력", "w": "생각이 너무 많아 새벽까지 잠 못 들기도 함"},
                {"title": "미래학자", "s": "10년 후를 내다보는 지성적 혜안", "w": "가끔 너무 미래에 살아 현실 감각이 부족함"},
                {"title": "시스템 파괴자", "s": "고정관념을 부수는 지적 도전 정신", "w": "논리가 너무 완벽해 대화 상대를 당황하게 함"}
            ],
            "INF": [
                {"title": "순혈의 수호자", "s": "고결한 신념과 공동체를 지키는 힘", "w": "새로운 변화를 받아들이는 데 시간이 걸림"},
                {"title": "고독한 애국자", "s": "품격 있는 자부심과 선비 같은 절개", "w": "원칙이 너무 엄격해 스스로를 피곤하게 함"},
                {"title": "사색적 중재자", "s": "갈등을 녹이는 따뜻한 공감과 포용", "w": "배려하느라 결정을 못 내리는 우유부단함"},
                {"title": "따뜻한 선구자", "s": "약자를 향한 무한 공감과 인도적 혁신", "w": "상상력이 풍부해 현실적 제약을 잊곤 함"},
                {"title": "유토피아 몽상가", "s": "순수한 선의로 가득 찬 이상의 결정체", "w": "세상의 쓴맛보다 단맛만 보고 싶은 낭만파"}
            ],
            "ENF": [
                {"title": "신념의 선동가", "s": "사람을 움직이는 뜨거운 호소력", "w": "열정이 너무 넘쳐 주변을 지치게 할 수 있음"},
                {"title": "열정적 홍보관", "s": "긍정 에너지의 화신, 분위기 메이커", "w": "혼자 있는 시간을 견디기 힘들어할 때가 있음"},
                {"title": "유연한 소통가", "s": "누구와도 친구가 되는 탁월한 사교성", "w": "모두에게 잘 보이려다 본인 색깔을 잃기도 함"},
                {"title": "공감의 개혁가", "s": "사람 중심의 가치를 실현하는 따뜻한 변화", "w": "남의 슬픔에 너무 깊게 이입해 감정 소모가 큼"},
                {"title": "인간중심 혁명가", "s": "억압에 맞서는 뜨거운 인류애와 용기", "w": "이상적인 모습에 대한 고집이 커서 실망도 빠름"}
            ],
            "ESJ": [
                {"title": "원칙의 집행관", "s": "완벽한 질서와 흐트러짐 없는 성실함", "w": "1분 1초의 오차도 용납 못 하는 엄격함"},
                {"title": "안정적 운영자", "s": "믿고 맡길 수 있는 든든한 체계 관리", "w": "검증되지 않은 방식에 대한 강한 거부감"},
                {"title": "합리적 조율사", "s": "공평무사한 판단과 중도의 균형감", "w": "너무 이성적이라 가슴보다 머리가 먼저 반응"},
                {"title": "포용적 행정가", "s": "따뜻한 돌봄과 체계적 행정의 조화", "w": "모두를 챙기려다 행정 절차가 복잡해짐"},
                {"title": "공동체 관리자", "s": "하나로 묶는 강력한 결속력과 책임감", "w": "개인보다 조직의 논리를 앞세우기도 함"}
            ],
            "ISJ": [
                {"title": "전통의 파수꾼", "s": "묵묵히 제자리를 지키는 인내와 전통", "w": "익숙한 길에서 벗어나는 것을 몹시 두려워함"},
                {"title": "성실한 보수주의자", "s": "빈틈없는 일 처리와 검증된 방식 신뢰", "w": "예상치 못한 변수가 생기면 당황하는 편"},
                {"title": "조용한 안정주의자", "s": "평온한 일상의 수호자, 깔끔한 매너", "w": "자기주장을 내세우기보다 참는 것이 습관화"},
                {"title": "다정한 봉사자", "s": "보이지 않는 곳에서의 섬세한 배려", "w": "거절을 못 해 혼자 일을 다 떠맡는 경향"},
                {"title": "평등의 파수꾼", "s": "규칙 속에서 공평함을 찾는 정의감", "w": "선을 넘는 사람을 보면 블랙리스트 작성함"}
            ],
            "ESP": [
                {"title": "거침없는 개척자", "s": "두려움 없는 도전과 야성적 행동력", "w": "일단 저지르고 수습은 미래의 나에게 토스"},
                {"title": "승부사", "s": "1등을 놓치지 않는 집념과 추진력", "w": "지는 것을 죽기보다 싫어하는 승부욕"},
                {"title": "쾌락적 실용주의자", "s": "즐거움을 찾는 감각과 유머러스함", "w": "지루하고 반복적인 업무를 견디기 힘들어함"},
                {"title": "자유로운 활동가", "s": "구속을 거부하는 유연함과 변화 향유", "w": "계획표대로 사는 것을 인생의 낭비라 여김"},
                {"title": "기존 질서 저항자", "s": "부당한 권위에 맞서는 당당한 표현", "w": "가끔 반대를 위한 반대를 하는 반항아적 면모"}
            ],
            "ISP": [
                {"title": "냉소적 기술자", "s": "감정에 휘둘리지 않는 완벽한 전문성", "w": "무덤덤한 표정 때문에 차갑다는 오해를 받음"},
                {"title": "실력 위주 분석가", "s": "화려한 말보다 결과로 증명하는 쿨함", "w": "낭만적인 대화도 효율적으로 끝내려 함"},
                {"title": "객관적 관찰자", "s": "한발 물러나 세상을 보는 여유로운 시선", "w": "세상 돌아가는 일에 가끔 너무 무심해 보임"},
                {"title": "유동적 비판가", "s": "허점을 찾아내는 날카롭고 정확한 통찰", "w": "상대방의 논리 오류를 너무 직설적으로 지적"},
                {"title": "파격적 창조자", "s": "고정관념을 뛰어넘는 독창적인 감각", "w": "본인 스타일이 확고해 대중성이 부족할 수 있음"}
            ]
        }

    def analyze(self, answers, response_times):
        mbti_raw = {'E': [], 'S': [], 'T': [], 'J': []}
        val_raw = []
        for q_id, score in answers.items():
            num = int(q_id.replace('q', ''))
            if num in [1, 9, 17, 25]: mbti_raw['E'].append(score)
            elif num == 33: mbti_raw['E'].append(7 - score)
            elif num in [3, 11, 19, 27, 35]: mbti_raw['S'].append(score)
            elif num in [5, 13, 21, 29, 37]: mbti_raw['T'].append(score)
            elif num in [7, 15, 23, 31, 39]: mbti_raw['J'].append(score)
            else: val_raw.append(score)

        get_avg = lambda s: sum(s)/len(s) if s else 3.5
        mbti = ("E" if get_avg(mbti_raw['E']) > 3.5 else "I") + \
               ("S" if get_avg(mbti_raw['S']) > 3.5 else "N") + \
               ("T" if get_avg(mbti_raw['T']) > 3.5 else "F") + \
               ("J" if get_avg(mbti_raw['J']) > 3.5 else "P")
        
        cluster = mbti[0] + mbti[1:3] if mbti[1] == 'N' else mbti[0] + mbti[1] + mbti[3]
        v_total = sum(val_raw)
        v_idx = 0 if v_total >= 100 else 1 if v_total >= 80 else 2 if v_total >= 61 else 3 if v_total >= 41 else 4
        
        res = self.db[cluster][v_idx]
        soulmate = self.db[cluster][v_idx]["title"]
        spark_partner = self.db[self.match_logic[cluster]][v_idx]["title"]

        return {
            "title": res["title"], "strength": res["s"], "weakness": res["w"],
            "mbti": mbti, "soulmate": soulmate, "spark": spark_partner,
            "x": self.clusters_x.index(cluster), "y": 4 - v_idx,
            "consistency": max(0, 100 - (np.mean([np.std(x) for x in mbti_raw.values()]) * 40)),
            "avg_time": np.mean(list(response_times.values()))
        }

# --- 3. 문항 데이터 (최종 통합) ---
QUESTIONS = [
    {"id": "q01", "text": "나는 처음 보는 사람들과 가벼운 대화를 나누는 것이 즐겁다."},
    {"id": "q02", "text": "기업에 대한 법인세 인상은 국가 경제 활력을 떨어뜨리는 행위이다."},
    {"id": "q03", "text": "나는 영화를 볼 때 숨겨진 상징보다는 눈에 보이는 연출에 더 집중한다."},
    {"id": "q04", "text": "전통적인 가족 제도와 가치는 우리 사회가 수호해야 할 소중한 유산이다."},
    {"id": "q05", "text": "친구의 고민을 들으면 공감보다는 구체적인 해결책을 먼저 고민하게 된다."},
    {"id": "q06", "text": "대북 정책은 대화보다는 강력한 억제와 압박을 기조로 삼아야 한다."},
    {"id": "q07", "text": "여행을 갈 때 분 단위의 계획이 없으면 불안함을 느끼곤 한다."},
    {"id": "q08", "text": "복지 확대보다는 기업 성장을 통한 일자리 창출이 가난 해결의 지름길이다."},
    {"id": "q09", "text": "지독하게 힘든 날일수록 혼자보다는 사람들을 만나 에너지를 얻고 싶다."},
    {"id": "q10", "text": "소수자 인권 정책은 사회적 합의가 충분히 이루어진 후에 시행해야 한다."},
    {"id": "q11", "text": "새로운 도구를 다룰 때 설명서를 정독하고 그대로 따르는 것을 선호한다."},
    {"id": "q12", "text": "외교에서 최우선은 국익이며, 때로는 동맹보다 자국 우선주의가 필요하다."},
    {"id": "q13", "text": "나는 공동체의 화합보다 명확한 성과와 효율성을 우선시한다."},
    {"id": "q14", "text": "부유층에 대한 상속세는 재산권 침해이므로 대폭 완화해야 한다."},
    {"id": "q15", "text": "나는 업무나 과제를 마감 직전에 처리하기보다 미리미리 끝내두는 편이다."},
    {"id": "q16", "text": "공동체의 안전을 위해서라면 개인의 자유는 어느 정도 제한될 수 있다."},
    {"id": "q17", "text": "나는 생각한 것을 머릿속으로 정리하기보다 말로 내뱉으며 정리하는 편이다."},
    {"id": "q18", "text": "국제적 명분보다는 우리나라의 경제적 실익을 위한 외교가 더 중요하다."},
    {"id": "q19", "text": "나는 구체적인 수치와 데이터가 뒷받침된 정보만을 신뢰한다."},
    {"id": "q20", "text": "최저임금은 국가 강제보다 시장의 자율적인 결정에 맡겨야 한다."},
    {"id": "q21", "text": "비판을 들었을 때 감정보다 논리적 타당성을 먼저 따진다."},
    {"id": "q22", "text": "역사 교육은 민족적 자부심과 정체성을 고취하는 데 주력해야 한다."},
    {"id": "q23", "text": "내 책상이나 방은 항상 정해진 규칙에 따라 질서정연하게 정리되어 있다."},
    {"id": "q24", "text": "평화를 유지하는 가장 확실한 방법은 강력한 군사력을 비축하는 것이다."},
    {"id": "q25", "text": "갑작스럽게 제안된 번개 모임이나 약속이 나를 설레게 한다."},
    {"id": "q26", "text": "공공 서비스(철도, 의료 등)는 경쟁력 강화를 위해 민영화될 필요가 있다."},
    {"id": "q27", "text": "사과라는 단어를 들으면 비유적인 의미보다 과일 사과가 먼저 떠오른다."},
    {"id": "q28", "text": "환경 보호도 중요하지만 국가 경제 성장을 늦추면서까지 강요해서는 안 된다."},
    {"id": "q29", "text": "'똑똑하다'는 칭찬이 '따뜻하다'는 말보다 나에게는 더 큰 기쁨을 준다."},
    {"id": "q30", "text": "난민 수용은 국가 안보와 갈등을 고려하여 엄격하게 제한해야 한다."},
    {"id": "q31", "text": "결정을 내려야 할 때 대안을 찾기보다 빠르게 결론을 맺는 쪽을 택한다."},
    {"id": "q32", "text": "안전망보다 열심히 일한 사람에게 큰 보상을 주는 사회가 건강하다고 믿는다."},
    {"id": "q33", "text": "나는 넓고 얕은 관계보다 좁고 깊은 관계에서 더 큰 편안함을 느낀다."},
    {"id": "q34", "text": "성과에 따른 차등 보상 시스템이 조직 발전을 이끄는 가장 공정한 방식이다."},
    {"id": "q35", "text": "상상력보다는 현실적인 대안을 제시하는 능력이 더 중요하다고 생각한다."},
    {"id": "q36", "text": "외교적 갈등 시 중립보다는 선명한 가치 동맹을 선택해야 한다."},
    {"id": "q37", "text": "원칙은 상황에 상관없이 예외 없이 적용되어야 한다고 믿는다."},
    {"id": "q38", "text": "주택 가격 안정을 위해서는 규제보다 공급 확대가 우선이다."},
    {"id": "q39", "text": "계획되지 않은 돌발 상황이 발생하면 즐거움보다 스트레스를 먼저 받는다."},
    {"id": "q40", "text": "표현의 자유는 중요하지만 유해 정보에 대해서는 국가적 검열이 필요하다."}
]

# --- 4. 메인 애플리케이션 ---
def main():
    st.set_page_config(page_title="Forty : Persona discovery", page_icon="🧩")

    if 'step' not in st.session_state: st.session_state.step = 'intro'
    if 'current_q' not in st.session_state: st.session_state.current_q = 0
    if 'answers' not in st.session_state: st.session_state.answers = {}
    if 'times' not in st.session_state: st.session_state.times = {}
    if 'q_start' not in st.session_state: st.session_state.q_start = 0

    if st.session_state.step == 'intro':
        st.title("Forty : Discover Your Persona")
        st.subheader("당신의 내면과 신념의 좌표를 찾아드립니다.")
        st.write("본 검사는 40개의 문항을 통해 당신의 성격 유형과 가치관을 분석합니다.")
        if st.button("진단 시작하기 ⚡", use_container_width=True):
            st.session_state.step = 'survey'
            st.session_state.q_start = time.time()
            st.rerun()

    elif st.session_state.step == 'survey':
        q_idx = st.session_state.current_q
        total_q = len(QUESTIONS)
        st.progress(q_idx / total_q)
        q = QUESTIONS[q_idx]
        st.markdown(f"#### Q{q_idx+1}. {q['text']}")
        ans = st.select_slider("응답:", options=[1,2,3,4,5,6], value=3,
                               format_func=lambda x: {1:"전혀 아님", 2:"아님", 3:"보통", 4:"약간", 5:"그렇다", 6:"매우 그렇다"}[x])

        if st.button("다음으로 ➡️", type="primary", use_container_width=True):
            st.session_state.times[q['id']] = time.time() - st.session_state.q_start
            st.session_state.answers[q['id']] = ans
            if q_idx + 1 < total_q:
                st.session_state.current_q += 1
                st.session_state.q_start = time.time()
                st.rerun()
            else:
                st.session_state.step = 'result'
                st.rerun()

    elif st.session_state.step == 'result':
        engine = FortyEngineV47()
        res = engine.analyze(st.session_state.answers, st.session_state.times)
        
        st.balloons()
        st.markdown(f"""<div class="persona-card">
            <p style="opacity:0.8; margin-bottom:5px;">당신을 정의하는 페르소나</p>
            <h1 style="font-size:2.8rem; margin:0;">"{res['title']}"</h1>
            <p style="margin-top:10px;">MBTI: {res['mbti']}</p>
        </div>""", unsafe_allow_html=True)
        
        st.subheader("🔍 심리학적 심층 리포트")
        st.markdown(f"""
        <div class="analysis-box">
            <p class="strength-tag">✨ 핵심 장점</p>
            <p style="margin:0;">{res['strength']}</p>
        </div>
        <div class="analysis-box" style="border-left-color: #D32F2F;">
            <p class="weakness-tag">🌀 주의할 점 (귀여운 약점)</p>
            <p style="margin:0;">{res['weakness']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("💖 환상의 파트너 매칭")
        st.markdown(f"""
        <div class="match-container">
            <div class="match-card">
                <p style="font-size:0.8rem; color:gray; margin-bottom:5px;">말하지 않아도 통하는</p>
                <p style="color:#6C63FF; font-weight:bold; margin-bottom:10px;">🍀 소울메이트</p>
                <h4 style="margin:0;">{res['soulmate']}</h4>
            </div>
            <div class="match-card">
                <p style="font-size:0.8rem; color:gray; margin-bottom:5px;">반대라서 더 끌리는</p>
                <p style="color:#FF4B4B; font-weight:bold; margin-bottom:10px;">🔥 스파크 파트너</p>
                <h4 style="margin:0;">{res['spark']}</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.write("### 📊 40 MATRIX 가치관 지도")
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(res['x'], res['y'], marker='*', markersize=15, color='#6C63FF')
        ax.set_xticks(range(8)); ax.set_xticklabels(["INF", "INT", "ENF", "ENT", "ISJ", "ISP", "ESJ", "ESP"])
        ax.set_yticks([]); st.pyplot(fig)

        st.write("### 🛡️ 데이터 신뢰도 지표")
        c1, c2, c3 = st.columns(3)
        c1.metric("일관성 점수", f"{res['consistency']:.1f}%")
        c2.metric("평균 속도", f"{res['avg_time']:.2f}s")
        c3.metric("진실성 추정", "높음" if res['avg_time'] > 1.5 else "낮음")

        if st.button("다시 검사하기 🔄", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()