import streamlit as st
from openai import OpenAI
import pyperclip

st.set_page_config(page_title="E-mail Writer Chatbot", page_icon="📧")

st.title("📧 E-mail Writer Chatbot")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 이메일 스타일 옵션
EMAIL_STYLES = {
    "비즈니스 격식": "정중하고 전문적인 비즈니스 이메일 형식으로 작성합니다.",
    "비즈니스 캐주얼": "친근하면서도 전문적인 비즈니스 이메일 형식으로 작성합니다.",
    "학술": "학술적이고 공식적인 형식으로 작성합니다.",
    "친근함": "친근하고 개인적인 톤으로 작성합니다."
}

# GPT 모델 설정
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# 대화 내역 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# 이메일 제목/본문 초기화
if "email_subject" not in st.session_state:
    st.session_state.email_subject = ""
if "email_body" not in st.session_state:
    st.session_state.email_body = ""

# 사용자 이름 초기화
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# 사이드바 설정
with st.sidebar:
    st.header("설정")

    # 사용자 이름 입력
    user_name = st.text_input("사용자 이름", value=st.session_state.user_name)
    st.session_state.user_name = user_name

    # 이메일 스타일 선택택
    selected_style = st.selectbox(
        "이메일 스타일 선택",
        options=list(EMAIL_STYLES.keys()),
        index=0
    )
    
    
    st.markdown("---")
    st.caption("이 앱은 OpenAI API를 사용하여 이메일 초안을 생성합니다.")

# 사용법
with st.expander("💡 이 페이지 사용법", expanded=False):
    st.markdown("""
    ## 이메일 작성 도우미 사용법
    
    이 도구는 AI를 활용하여 다양한 상황에 맞는 이메일을 작성해 드립니다.
    
    1. **사이드바 설정**
       - **사용자 이름**: 이메일 발신자 이름을 입력하세요.
       - **이메일 스타일**: 원하는 이메일 톤(비즈니스 격식, 캐주얼, 학술, 친근함)을 선택하세요.
    
    2. **상황 설명 입력**
       - 아래 입력창에 이메일을 작성해야 하는 상황을 구체적으로 설명해주세요.
       - 예시: "거래처에 새해 인사와 함께 신규 계약건에 대해 이메일을 보내야 합니다."
       - 받는 사람, 목적, 포함할 내용 등 구체적으로 작성할수록 더 적절한 이메일이 생성됩니다.
    
    3. **AI 응답 확인**
       - AI가 상황에 맞는 이메일 제목과 본문을 생성합니다.
       - 생성된 이메일을 검토하고 필요에 따라 수정하여 사용하세요.
    
    4. **추가 정보 제공**
       - 생성된 이메일이 만족스럽지 않으면, 더 구체적인 정보를 추가로 제공해보세요.
    """)

# 기존 대화 표시
st.subheader("상황 설명")
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 예시 입력이 있으면 채팅 입력창에 표시
chat_input_placeholder = "상황을 설명해주세요. \n(예: 거래처에 새해 인사와 함께 신규 계약건에 대해 이메일을 보내야 합니다.)"
if "example_input" in st.session_state:
    prompt = st.chat_input(chat_input_placeholder, value=st.session_state.example_input)
    del st.session_state.example_input
else:
    prompt = st.chat_input(chat_input_placeholder)

if prompt:
    # 시스템 메시지 설정 (최초 입력시에만)
    if len(st.session_state.messages) == 0:
        system_message = f"""당신은 이메일 작성을 도와주는 전문가입니다. 
사용자가 제공하는 상황에 맞는 적절한 이메일을 작성해주세요.
이메일은 항상 다음 형식으로 작성해주세요:

---

## 제목
[이메일 제목]

## 본문
안녕하세요, [이메일 받는 이]. 
{st.session_state.user_name}입니다.

[이메일 본문]

감사합니다.

{st.session_state.user_name} 올림

---

이메일 어조: {selected_style}
이메일 어조 설명: {EMAIL_STYLES[selected_style]}

필요한 정보가 부족하면 사용자에게 추가 정보를 요청하세요.
항상 문법적으로 정확하고 상황에 적합한 이메일을 작성하세요."""
        
        st.session_state.messages.append({"role": "system", "content": system_message})
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 응답 생성 및 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        
        response = st.write_stream(stream)
        
        # 이메일 제목과 본문 추출
        if "## 제목" in response and "## 본문" in response:
            try:
                subject_start = response.find("## 제목") + 6
                subject_end = response.find("## 본문")
                body_start = response.find("## 본문") + 6
                
                st.session_state.email_subject = response[subject_start:subject_end].strip()
                st.session_state.email_body = response[body_start:].strip()
            except:
                st.session_state.email_subject = "제목 추출 실패"
                st.session_state.email_body = response
    
    # 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 이메일 결과 표시
    if st.session_state.email_subject and st.session_state.email_body:
        st.markdown("---")
        st.subheader("📧 생성된 이메일")
        
        # 이메일 결과 표시 (스타일링)
        email_container = st.container(border=True)
        with email_container:
            st.markdown(f"**제목:** {st.session_state.email_subject}")
            st.divider()
            st.markdown(st.session_state.email_body)
        
        # # 복사 버튼
        # copy_cols = st.columns(3)
        # full_email = f"제목: {st.session_state.email_subject}\n\n{st.session_state.email_body}"
        
        # if copy_cols[0].button("📋 전체 복사"):
        #     try:
        #         pyperclip.copy(full_email)
        #         st.toast("이메일 전체가 클립보드에 복사되었습니다!")
        #     except:
        #         st.warning("클립보드 복사가 실패했습니다. 웹 브라우저 설정을 확인해주세요.")
        
        # if copy_cols[1].button("📋 제목만 복사"):
        #     try:
        #         pyperclip.copy(st.session_state.email_subject)
        #         st.toast("이메일 제목이 클립보드에 복사되었습니다!")
        #     except:
        #         st.warning("클립보드 복사가 실패했습니다. 웹 브라우저 설정을 확인해주세요.")
        
        # if copy_cols[2].button("📋 본문만 복사"):
        #     try:
        #         pyperclip.copy(st.session_state.email_body)
        #         st.toast("이메일 본문이 클립보드에 복사되었습니다!")
        #     except:
        #         st.warning("클립보드 복사가 실패했습니다. 웹 브라우저 설정을 확인해주세요.")
        
        # # 다시 작성하기 버튼
        # if st.button("🔄 다른 이메일 작성하기", type="primary"):
        #     st.session_state.messages = []
        #     st.session_state.email_subject = ""
        #     st.session_state.email_body = ""
        #     st.rerun()