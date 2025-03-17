import streamlit as st
from openai import OpenAI
import requests
from datetime import datetime

st.set_page_config(page_title="뉴스 브리핑 챗봇", page_icon="📰")

st.title("📰 실시간 뉴스 브리핑 챗봇")

# OpenAI 및 NewsAPI 키 설정
openai_api_key = st.secrets["OPENAI_API_KEY"]
news_api_key = st.secrets["NEWS_API_KEY"]

client = OpenAI(api_key=openai_api_key)

# 뉴스 브리핑 스타일 옵션
NEWS_STYLES = {
    "핵심 요약": "핵심 정보만 간결하게 요약합니다.",
    "상세 설명": "중요 내용을 상세히 설명합니다.",
}

# 국가 옵션
COUNTRIES = {
    "미국": "us",
}

# GPT 모델 설정
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# 대화 내역 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 최근 뉴스 캐시
if "latest_news" not in st.session_state:
    st.session_state.latest_news = None
if "last_fetch_time" not in st.session_state:
    st.session_state.last_fetch_time = None

# 사이드바 설정
with st.sidebar:
    st.header("설정")

    # 뉴스 스타일 선택
    selected_style = st.selectbox(
        "브리핑 스타일 선택",
        options=list(NEWS_STYLES.keys()),
        index=0
    )
    
    # 국가 선택
    selected_country = st.selectbox(
        "국가 선택",
        options=list(COUNTRIES.keys()),
        index=0
    )
    
    # 뉴스 개수 선택
    news_count = st.slider("가져올 뉴스 개수", min_value=3, max_value=10, value=5)
    
    # 뉴스 새로고침 버튼
    if st.button("🔄 뉴스 새로고침"):
        st.session_state.latest_news = None
        st.session_state.last_fetch_time = None
        st.rerun()
    
    st.markdown("---")
    st.caption("이 앱은 NewsAPI와 OpenAI API를 사용하여 실시간 뉴스 브리핑을 생성합니다.")

# 실제 뉴스 가져오기 함수
def fetch_news(country="us", page_size=5):
    url = "https://newsapi.org/v2/top-headlines"
    
    params = {
        'apiKey': news_api_key,
        'country': COUNTRIES[country],
        'pageSize': page_size
    }
    
    try:
        # 디버깅용 출력
        # st.write(f"API 요청 URL: {url}")
        # st.write(f"API 요청 매개변수: {params}")
        
        response = requests.get(url, params=params)
        
        # 상태 코드 확인
        # st.write(f"API 응답 상태 코드: {response.status_code}")
        
        # 응답이 성공적이지 않은 경우
        if response.status_code != 200:
            st.error(f"API 오류: {response.status_code} - {response.text}")
            return None
        
        # JSON 응답 가져오기
        data = response.json()
        
        # 응답 구조 확인
        if 'status' in data and data['status'] == 'ok':
            if 'articles' in data and len(data['articles']) > 0:
                st.success(f"{len(data['articles'])}개의 뉴스를 가져왔습니다.")
                return data
            else:
                st.warning("뉴스 기사가 없습니다.")
                return None
        else:
            st.error(f"API 응답 오류: {data.get('message', '알 수 없는 오류')}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"뉴스 API 요청 중 오류 발생: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"JSON 파싱 오류: {str(e)}")
        return None
    except Exception as e:
        st.error(f"예상치 못한 오류: {str(e)}")
        return None

# 뉴스 데이터를 문자열로 변환
def news_to_string(news_data):
    if not news_data or 'articles' not in news_data or not news_data['articles']:
        return "뉴스를 가져올 수 없습니다."
    
    news_text = ""
    for i, article in enumerate(news_data['articles'], 1):
        if not article:
            continue
            
        title = article.get('title', '제목 없음')
        source_name = article.get('source', {}).get('name', '출처 없음')
        published_at = article.get('publishedAt', '날짜 없음')
        description = article.get('description', '내용 없음')
        url = article.get('url', '#')
        
        news_text += f"{i}. 제목: {title}\n"
        news_text += f"   출처: {source_name}\n"
        news_text += f"   작성일: {published_at}\n"
        news_text += f"   내용: {description}\n"
        news_text += f"   URL: {url}\n\n"
    
    return news_text

# 사용법
with st.expander("💡 이 페이지 사용법", expanded=False):
    st.markdown("""
    ## 실시간 뉴스 브리핑 도우미 사용법
    
    NewsAPI와 OpenAI를 활용하여 실시간 최신 뉴스를 요약하고 브리핑해드립니다.
    
    1. **사이드바 설정**
       - **브리핑 스타일**: 원하는 브리핑 스타일(핵심 요약, 상세 설명)을 선택하세요.
       - **국가**: 뉴스를 가져올 국가를 선택하세요.
       - **뉴스 개수**: 가져올 뉴스 개수를 설정하세요.
       - **뉴스 새로고침**: 최신 뉴스를 다시 가져옵니다.
    
    2. **질문 입력**
       - 아래 입력창에 관심 있는 뉴스 주제나 질문을 입력하세요.
       - 예시: "오늘 주요 뉴스를 요약해줘"
       - 실시간으로 가져온 뉴스를 바탕으로 AI가 답변합니다.
    
    3. **AI 응답 확인**
       - AI가 실시간 뉴스를 기반으로 브리핑을 제공합니다.
       - 선택한 스타일에 맞춰 정보가 제공됩니다.
       - 각 뉴스에 대한 출처 및 링크도 함께 제공됩니다.
    
    4. **추가 질문(반복복)**
       - 브리핑 내용에 대해 더 알고 싶은 점이 있으면 추가 질문을 입력하세요.
    """)

# 최신 뉴스 가져오기
def get_latest_news():
    current_time = datetime.now()
     
    with st.spinner("최신 뉴스를 가져오는 중..."):
        news_data = fetch_news( 
            country=selected_country,
            page_size=news_count
        )
        
        if news_data:
            st.session_state.latest_news = news_data
            st.session_state.last_fetch_time = current_time
    
    return st.session_state.latest_news

# 기존 대화 표시
st.subheader("뉴스 브리핑")
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 채팅 입력창
chat_input_placeholder = "예시: 오늘의 주요 뉴스 알려줘"
prompt = st.chat_input(chat_input_placeholder)

if prompt:
    # 최신 뉴스 가져오기
    news_data = get_latest_news()
    
    if not news_data:
        st.error("뉴스 데이터를 가져오지 못했습니다. 잠시 후 다시 시도해주세요.")
        st.stop()
    
    # 뉴스 텍스트로 변환
    news_text = news_to_string(news_data)
    
    # 시스템 메시지 설정 (최초 입력시에만)
    if len(st.session_state.messages) == 0:
        system_message = f"""당신은 실시간 뉴스 브리핑을 제공하는 전문가입니다.
        다음 실시간 뉴스 데이터를 기반으로 사용자의 질문에 답변해주세요:

        {news_text}

        브리핑 스타일: {selected_style}
        브리핑 스타일 설명: {NEWS_STYLES[selected_style]}
        국가: {selected_country}

        다음 형식으로 뉴스 브리핑을 제공해주세요:

        ---

        ## 📰 미국 뉴스 브리핑

        ### 주요 뉴스 요약
        [주요 뉴스 요약]

        ### 상세 내용
        [선택한 스타일에 맞는 상세 내용]

        ### 영향 및 전망
        [해당 뉴스의 영향과 앞으로의 전망]

        ### 참고 자료
        [뉴스 출처 및 참고 링크 목록]

        ---

        반드시 제공된 뉴스 데이터만 사용하여 답변하세요.
        각 뉴스의 출처와 URL을 참고 자료 섹션에 포함시켜 주세요.
        사용자의 질문에 맞게 관련 뉴스만 선별하여 제공하세요."""
        
        st.session_state.messages.append({"role": "system", "content": system_message})
    else:
        # 요약 이후의 대화
        system_message = f"""당신은 실시간 뉴스 브리핑을 제공하는 전문가입니다.
        다음 실시간 뉴스 데이터를 기반으로 사용자의 질문에 답변해주세요:

        {news_text}

        브리핑 스타일: {selected_style}
        브리핑 스타일 설명: {NEWS_STYLES[selected_style]}
        국가: {selected_country}

        반드시 제공된 뉴스 데이터만 사용하여 답변하세요.
        각 뉴스의 출처와 URL을 참고 자료로 포함시켜 주세요."""
        
        st.session_state.messages[0] = {"role": "system", "content": system_message}
    
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 응답 생성 및 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # 스트리밍 응답을 올바르게 처리
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content or ""
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            # 최종 응답 표시
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            full_response = "죄송합니다, 응답을 생성하는 중에 오류가 발생했습니다. 다시 시도해 주세요."
            message_placeholder.markdown(full_response)
        
        # 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": full_response})