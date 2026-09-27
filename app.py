import os
import json
import datetime
import csv
import ssl
import random
import streamlit as st
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="FinLit AI — Financial Literacy Chatbot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base directory for reliable relative path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure SSL & NLTK data path
ssl._create_default_https_context = ssl._create_unverified_context
nltk.data.path.append(os.path.join(BASE_DIR, "nltk_data"))
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# File paths
intents_file_path = os.path.join(BASE_DIR, "intents.json")
chat_log_path = os.path.join(BASE_DIR, "chat_log.csv")

# Load intents knowledge base
@st.cache_data(show_spinner=False)
def load_intents():
    with open(intents_file_path, "r", encoding="utf-8") as file:
        return json.load(file)

intents = load_intents()

# Cache and train the TF-IDF vectorizer and Logistic Regression classifier
@st.cache_resource(show_spinner=False)
def train_model():
    vectorizer = TfidfVectorizer(ngram_range=(1, 4))
    clf = LogisticRegression(random_state=0, max_iter=10000)

    tags = []
    patterns = []
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            tags.append(intent['tag'])
            patterns.append(pattern)

    x = vectorizer.fit_transform(patterns)
    y = tags
    clf.fit(x, y)
    return vectorizer, clf

vectorizer, clf = train_model()

# Chatbot inference logic
def chatbot_predict(input_text):
    if not input_text or not input_text.strip():
        return "Please enter a valid question regarding personal finance.", "general"

    input_vec = vectorizer.transform([input_text])
    tag = str(clf.predict(input_vec)[0])

    for intent in intents['intents']:
        if intent['tag'] == tag:
            response = random.choice(intent['responses'])
            return response, tag

    fallback_response = (
        "I'm sorry, I couldn't find a direct answer to that. "
        "Try asking about budgeting, investments, compound interest, credit scores, taxes, or loans!"
    )
    return fallback_response, "fallback"

# Legacy wrapper for backward compatibility
def chatbot(input_text):
    response, _ = chatbot_predict(input_text)
    return response

# Log conversation to CSV
def log_interaction(user_text, bot_response, tag=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(chat_log_path)
    
    with open(chat_log_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['User Input', 'Chatbot Response', 'Timestamp'])
        writer.writerow([user_text, bot_response, timestamp])

# Custom CSS for Modern, Professional Polish
st.markdown("""
<style>
    /* Main container and font styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #0D9488 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    .hero-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 15px;
        opacity: 0.92;
        line-height: 1.5;
    }

    /* Tag badges */
    .intent-badge {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Metric cards */
    .metric-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 13px;
        color: #64748B;
        margin-top: 4px;
    }

    /* Chat bubble styling tweaks */
    .stChatMessage {
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 12px;
    }

    /* Quick prompt button styling */
    .quick-chip-button {
        font-size: 13px !important;
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation and App Info
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/money-bag.png", width=70)
    st.title("FinLit AI")
    st.caption("Empowering Smarter Financial Decisions")
    st.markdown("---")

    menu_options = [
        "💬 Live Chat",
        "🧮 Financial Calculators",
        "📜 Conversation History",
        "📚 Topics Directory",
        "ℹ️ About Project"
    ]
    choice = st.radio("Navigation", menu_options, index=0)

    st.markdown("---")
    st.markdown("### 📊 System Specs")
    st.markdown("""
    - **Model:** Logistic Regression
    - **Features:** TF-IDF (1-4 n-grams)
    - **Vocabulary:** 64 Financial Intents
    - **Engine:** Python 3.11 & NLTK
    """)

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 12px; color: #64748B;'>
        <b>Developer:</b> Harsh Kumar<br>
        <b>Reg No:</b> 250301120321<br>
        <b>Status:</b> Active v2.0
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MENU 1: LIVE CHAT
# ==============================================================================
if choice == "💬 Live Chat":
    # Top Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🤖 FinLit AI Financial Advisor</div>
        <div class="hero-subtitle">
            Ask any question about budgeting, saving, investing, credit scores, debt management, or taxes. 
            Get instant, reliable financial explanations powered by Natural Language Processing.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Hello! I'm your Financial Literacy Assistant.**\n\n"
                    "I can help you understand personal finance concepts, create budgets, explore investments, "
                    "or answer banking queries. What would you like to learn today?"
                ),
                "tag": "welcome",
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            }
        ]

    # Quick Prompts Section
    st.markdown("##### 💡 Suggested Questions to Get Started")
    col1, col2, col3 = st.columns(3)
    quick_query = None

    with col1:
        if st.button("📊 How does the 50/30/20 rule work?", use_container_width=True):
            quick_query = "How does the 50/30/20 budget rule work?"
        if st.button("📈 Difference between saving and investing?", use_container_width=True):
            quick_query = "What is the difference between saving and investing?"

    with col2:
        if st.button("💳 How can I improve my credit score?", use_container_width=True):
            quick_query = "How can I improve my credit score?"
        if st.button("🚀 Explain compound interest with an example", use_container_width=True):
            quick_query = "Explain compound interest and how it works"

    with col3:
        if st.button("🛡️ How do I identify financial scams?", use_container_width=True):
            quick_query = "How do I protect myself from financial scams?"
        if st.button("💼 What is Return on Investment (ROI)?", use_container_width=True):
            quick_query = "What is ROI?"

    st.markdown("---")

    # Render Conversation Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if msg.get("tag") and msg["role"] == "assistant" and msg["tag"] != "welcome":
                st.markdown(f"<span class='intent-badge'>🏷️ Topic: {msg['tag'].replace('_', ' ').title()}</span>", unsafe_allow_html=True)

    # Top-right action controls
    col_ctrl1, col_ctrl2 = st.columns([8, 2])
    with col_ctrl2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Conversation cleared. How can I help you with your finances?",
                    "tag": "welcome",
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                }
            ]
            st.rerun()

    # Chat Input Box
    user_input = st.chat_input("Type your financial question here... (e.g., 'What is liquidity?', 'How do taxes work?')")
    
    # Check if a quick suggestion button was clicked instead
    active_prompt = quick_query if quick_query else user_input

    if active_prompt:
        # Add user message to state
        st.session_state.messages.append({
            "role": "user",
            "content": active_prompt,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })

        # Generate response
        response, tag = chatbot_predict(active_prompt)

        # Log conversation to CSV
        log_interaction(active_prompt, response, tag)

        # Add assistant message to state
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "tag": tag,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })

        st.rerun()


# ==============================================================================
# MENU 2: FINANCIAL CALCULATORS
# ==============================================================================
elif choice == "🧮 Financial Calculators":
    st.header("🧮 Interactive Financial Planning Tools")
    st.write("Put financial literacy into practice with these real-time planning calculators.")

    tab1, tab2 = st.tabs(["📊 50/30/20 Budget Calculator", "📈 Compound Interest Calculator"])

    with tab1:
        st.subheader("The 50/30/20 Budgeting Method")
        st.markdown("""
        The **50/30/20 rule** is an intuitive budgeting framework:
        - **50% Needs**: Housing, utilities, groceries, transportation, minimum debt payments.
        - **30% Wants**: Dining out, entertainment, subscriptions, hobbies.
        - **20% Savings & Debt Repayment**: Emergency fund, investments, retirement, extra debt payoff.
        """)

        income = st.number_input("Enter your Monthly Take-Home (Net) Income ($ or ₹):", min_value=100.0, value=5000.0, step=100.0)

        needs = income * 0.50
        wants = income * 0.30
        savings = income * 0.20

        st.markdown("#### Your Recommended Monthly Allocation:")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🏠 Needs (50%)", f"{needs:,.2f}")
            st.caption("Essentials you cannot live without.")
        with c2:
            st.metric("🎉 Wants (30%)", f"{wants:,.2f}")
            st.caption("Lifestyle choices and entertainment.")
        with c3:
            st.metric("💰 Savings & Debt (20%)", f"{savings:,.2f}")
            st.caption("Investments and financial security.")

        st.progress(0.50)
        st.caption("50% Needs | 30% Wants | 20% Savings")

    with tab2:
        st.subheader("Compound Interest Growth Simulator")
        st.markdown("See how compound interest turns small consistent savings into wealth over time.")

        ci_col1, ci_col2 = st.columns(2)
        with ci_col1:
            principal = st.number_input("Initial Deposit / Principal ($ or ₹):", min_value=0.0, value=1000.0, step=500.0)
            monthly_addition = st.number_input("Monthly Contribution ($ or ₹):", min_value=0.0, value=200.0, step=50.0)

        with ci_col2:
            annual_rate = st.slider("Expected Annual Return / Interest Rate (%):", min_value=1.0, max_value=25.0, value=8.0, step=0.5)
            years = st.slider("Investment Horizon (Years):", min_value=1, max_value=40, value=10, step=1)

        # Compound calculation
        r = (annual_rate / 100) / 12
        months = years * 12
        
        # Future value with regular contributions
        fv_principal = principal * ((1 + r) ** months)
        if r > 0:
            fv_contributions = monthly_addition * (((1 + r) ** months - 1) / r)
        else:
            fv_contributions = monthly_addition * months

        total_future_value = fv_principal + fv_contributions
        total_invested = principal + (monthly_addition * months)
        total_interest = total_future_value - total_invested

        st.markdown("#### Projected Results:")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Total Final Balance", f"{total_future_value:,.2f}")
        with r2:
            st.metric("Total Capital Invested", f"{total_invested:,.2f}")
        with r3:
            st.metric("Compound Returns Earned", f"{total_interest:,.2f}", delta=f"+{(total_interest/total_invested)*100:.1f}%")

        st.info(f"💡 Compounding accounted for **{(total_interest/total_future_value)*100:.1f}%** of your total accumulated wealth!")


# ==============================================================================
# MENU 3: CONVERSATION HISTORY
# ==============================================================================
elif choice == "📜 Conversation History":
    st.header("📜 Conversation History & Analytics")
    st.write("Review past user queries and AI responses logged from user sessions.")

    if os.path.exists(chat_log_path):
        rows = []
        with open(chat_log_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for r in reader:
                if len(r) >= 3:
                    rows.append({"User": r[0], "Chatbot": r[1], "Timestamp": r[2]})

        if rows:
            # Summary Metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Questions Asked", len(rows))
            with m2:
                unique_queries = len(set([r["User"].lower().strip() for r in rows]))
                st.metric("Unique Queries", unique_queries)
            with m3:
                last_time = rows[-1]["Timestamp"] if rows else "N/A"
                st.metric("Latest Activity", last_time.split(" ")[0])

            st.markdown("---")

            # Search Filter
            search_term = st.text_input("🔍 Search Past Conversations (by keyword):", "")

            # Download CSV Button
            with open(chat_log_path, "rb") as log_file:
                st.download_button(
                    label="📥 Export Chat Log (CSV)",
                    data=log_file,
                    file_name="chat_log.csv",
                    mime="text/csv"
                )

            # Display filtered list
            filtered_rows = [r for r in rows if search_term.lower() in r["User"].lower() or search_term.lower() in r["Chatbot"].lower()]

            if filtered_rows:
                for idx, entry in enumerate(reversed(filtered_rows)):
                    with st.expander(f"💬 Query: \"{entry['User']}\" — {entry['Timestamp']}"):
                        st.markdown(f"**User Question:** {entry['User']}")
                        st.markdown(f"**Chatbot Answer:** {entry['Chatbot']}")
                        st.caption(f"Logged at: {entry['Timestamp']}")
            else:
                st.warning("No interactions matched your search keyword.")
        else:
            st.info("The conversation log is currently empty. Start chatting in the Live Chat tab!")
    else:
        st.info("No conversation log found yet. As you ask questions in the chat, they will be saved here automatically.")


# ==============================================================================
# MENU 4: TOPICS DIRECTORY
# ==============================================================================
elif choice == "📚 Topics Directory":
    st.header("📚 Supported Financial Topics Directory")
    st.write(f"FinLit AI is trained to understand **{len(intents['intents'])}** distinct financial literacy domains.")

    search_topic = st.text_input("Filter Topics (e.g., 'credit', 'budget', 'interest', 'tax'):", "")

    matching_intents = [
        it for it in intents['intents'] 
        if search_topic.lower() in it['tag'].lower() or any(search_topic.lower() in p.lower() for p in it['patterns'])
    ]

    st.caption(f"Showing {len(matching_intents)} of {len(intents['intents'])} topics")

    cols = st.columns(2)
    for i, intent in enumerate(matching_intents):
        col = cols[i % 2]
        with col:
            with st.expander(f"🏷️ {intent['tag'].replace('_', ' ').title()}"):
                st.markdown("**Sample Questions You Can Ask:**")
                for pat in intent['patterns'][:3]:
                    st.markdown(f"- *\"{pat}\"*")
                st.markdown("**Example Response:**")
                st.success(intent['responses'][0])


# ==============================================================================
# MENU 5: ABOUT PROJECT
# ==============================================================================
elif choice == "ℹ️ About Project":
    st.header("ℹ️ About the Financial Literacy Chatbot")
    
    st.markdown("""
    ### 🎯 Mission & Purpose
    Financial literacy is an essential life skill. Many individuals struggle with personal finance fundamentals like 
    budgeting, investing, compound growth, and debt management due to intimidating jargon or inaccessible education. 

    The **Financial Literacy Chatbot** was created to democratize financial knowledge by providing an intuitive, 
    conversational AI interface that gives straightforward, dependable guidance 24/7.
    """)

    st.markdown("---")
    st.subheader("🛠️ Technical Architecture")

    st.markdown("""
    | Stage | Technology | Function |
    | :--- | :--- | :--- |
    | **User Interface** | Streamlit | Responsive, web-based chat and calculator interface. |
    | **NLP Processing** | NLTK | Tokenization and sentence structuring via `punkt`. |
    | **Feature Extraction** | Scikit-Learn `TfidfVectorizer` | Extracts unigram to 4-gram numerical vectors ($1-4$ n-grams). |
    | **Intent Classifier** | Scikit-Learn `LogisticRegression` | Multinomial classification mapping vectors to intent tags. |
    | **Knowledge Base** | JSON (`intents.json`) | 64 domain topics with hundreds of curated training patterns. |
    | **Persistence** | CSV (`chat_log.csv`) | Historical tracking with timestamps for conversation auditing. |
    """)

    st.markdown("---")
    st.subheader("👨‍💻 Developer Information")
    st.markdown("""
    - **Developer:** Harsh Kumar
    - **Registration Number:** 250301120321
    - **GitHub Repository:** [https://github.com/hkumar7794/financial-literacy-chatbot2](https://github.com/hkumar7794/financial-literacy-chatbot2)
    """)

if __name__ == '__main__':
    pass
