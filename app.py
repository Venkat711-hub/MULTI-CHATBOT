import streamlit as st
import os
from dotenv import load_dotenv
from utils.llm import GroqClientWrapper, get_available_models, get_model_id
from utils.prompts import get_system_prompt, get_prompt_names

# Load env variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi CHATBOT Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply Outfit font */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title styling */
    .title-container {
        padding: 1.5rem 0rem;
        text-align: left;
    }
    
    .gradient-title {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 50%, #00F2FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        color: #718096;
        font-size: 1.15rem;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    
    /* Styled container cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
    }
    
    /* Glassmorphism sidebar elements */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 116, 139, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Section
st.markdown(
    """
    <div class="title-container">
        <h1 class="gradient-title">🤖 Multi CHATBOT Hub</h1>
        <p class="subtitle">Interact with state-of-the-art LLMs powered by Groq, optimized for blazing fast speed.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize Session State
if "single_chat_history" not in st.session_state:
    st.session_state.single_chat_history = []
if "compare_history" not in st.session_state:
    st.session_state.compare_history = []

# Resolve API Key
env_key = os.getenv("GROQ_API_KEY", "")
api_key = env_key

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/bot.png", width=80)
    st.title("Settings")
    
    # API Key Section
    st.subheader("🔑 API Configuration")
    user_api_key = st.text_input(
        "Groq API Key", 
        value=env_key, 
        type="password",
        help="Provide your Groq API Key. If set in .env, it loads automatically."
    )
    
    if user_api_key:
        api_key = user_api_key

    # Initialize client wrapper
    wrapper = GroqClientWrapper(api_key=api_key)
    
    if not wrapper.is_configured():
        st.warning("⚠️ Groq API key missing. Please enter it above or define GROQ_API_KEY in a .env file.")
    else:
        st.success("⚡ Groq API Connected!")

    st.markdown("---")
    
    # Global Parameters
    st.subheader("⚙️ Global Parameters")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.7, step=0.1, help="Higher values mean more creative but less predictable responses.")
    max_tokens = st.slider("Max Tokens", min_value=128, max_value=4096, value=2048, step=128, help="Max length of the generated response.")
    
    st.markdown("---")
    
    # Clear conversation actions
    st.subheader("🗑️ Reset Options")
    if st.button("Clear Single Chat History", use_container_width=True):
        st.session_state.single_chat_history = []
        st.toast("Single chat history cleared!")
        st.rerun()
        
    if st.button("Clear Compare History", use_container_width=True):
        st.session_state.compare_history = []
        st.toast("Comparison history cleared!")
        st.rerun()

# Tabs
tab1, tab2 = st.tabs(["💬 Single Chat Agent", "📊 Compare Models side-by-side"])

# ==================== TAB 1: SINGLE CHAT ====================
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("### Agent Settings")
        models_list = get_available_models()
        selected_model = st.selectbox("Select Model", models_list, index=0, key="single_model")
        
        personas = get_prompt_names()
        selected_persona = st.selectbox("Select Persona", personas, index=0, key="single_persona")
        
        st.markdown(
            f"""
            **Current Model:** `{get_model_id(selected_model)}`  
            **System Prompt:** *{selected_persona}*
            """
        )
        st.info("The system prompt sets the model's behavioral guidelines and context.")
        
    with col1:
        # Display chat messages
        for message in st.session_state.single_chat_history:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Check API Key
        if not wrapper.is_configured():
            st.info("Please configure your Groq API Key in the sidebar to start chatting.")
        else:
            # Chat Input
            if prompt := st.chat_input("Ask anything..."):
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Format system message & chat history
                messages = []
                system_prompt = get_system_prompt(selected_persona)
                messages.append({"role": "system", "content": system_prompt})
                
                for msg in st.session_state.single_chat_history:
                    messages.append(msg)
                
                # Append user prompt to state & request list
                st.session_state.single_chat_history.append({"role": "user", "content": prompt})
                messages.append({"role": "user", "content": prompt})
                
                # Display Assistant response with streaming
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    full_response = ""
                    try:
                        response_stream = wrapper.get_chat_completion(
                            messages=messages,
                            model_name=selected_model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            stream=True
                        )
                        
                        for chunk in response_stream:
                            if chunk.choices[0].delta.content is not None:
                                full_response += chunk.choices[0].delta.content
                                placeholder.markdown(full_response + "▌")
                        
                        placeholder.markdown(full_response)
                        # Append assistant response to session state
                        st.session_state.single_chat_history.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==================== TAB 2: COMPARE MODELS ====================
with tab2:
    st.markdown("### Model Comparison Mode")
    st.write("Submit a prompt to see responses from two different models side-by-side.")
    
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        model_a = st.selectbox("Select Model A", get_available_models(), index=0, key="model_a_select")
    with col_config2:
        model_b = st.selectbox("Select Model B", get_available_models(), index=1, key="model_b_select")
        
    personas_compare = get_prompt_names()
    compare_persona = st.selectbox("Comparison Persona", personas_compare, index=0, key="compare_persona")
    
    st.markdown("---")
    
    # Comparison chat input
    # Since Streamlit allows only one chat_input per page, we use a form with text_area + submit button for comparison mode
    with st.form("compare_form"):
        compare_prompt = st.text_area("Enter your prompt for comparison:", height=100, placeholder="e.g. Write a quick python function to reverse a linked list.")
        submit_compare = st.form_submit_button("🚀 Run Comparison")
        
    if submit_compare:
        if not wrapper.is_configured():
            st.error("Please configure your Groq API Key in the sidebar.")
        elif not compare_prompt.strip():
            st.warning("Please enter a valid prompt.")
        else:
            # Build messages for each model
            sys_prompt = get_system_prompt(compare_persona)
            messages_a = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": compare_prompt}
            ]
            messages_b = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": compare_prompt}
            ]
            
            # Setup columns for the output stream
            col_out_a, col_out_b = st.columns(2)
            
            with col_out_a:
                st.subheader(f"🟢 Model A: {model_a}")
                placeholder_a = st.empty()
                
            with col_out_b:
                st.subheader(f"🔵 Model B: {model_b}")
                placeholder_b = st.empty()
                
            # Stream Model A response
            content_a = ""
            try:
                placeholder_a.markdown("*Streaming model A...*")
                stream_a = wrapper.get_chat_completion(
                    messages=messages_a,
                    model_name=model_a,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                for chunk in stream_a:
                    if chunk.choices[0].delta.content is not None:
                        content_a += chunk.choices[0].delta.content
                        placeholder_a.markdown(content_a + "▌")
                placeholder_a.markdown(content_a)
            except Exception as e:
                placeholder_a.error(f"Error Model A: {e}")
                
            # Stream Model B response
            content_b = ""
            try:
                placeholder_b.markdown("*Streaming model B...*")
                stream_b = wrapper.get_chat_completion(
                    messages=messages_b,
                    model_name=model_b,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
                for chunk in stream_b:
                    if chunk.choices[0].delta.content is not None:
                        content_b += chunk.choices[0].delta.content
                        placeholder_b.markdown(content_b + "▌")
                placeholder_b.markdown(content_b)
            except Exception as e:
                placeholder_b.error(f"Error Model B: {e}")
                
            # Save to comparison history
            st.session_state.compare_history.append({
                "prompt": compare_prompt,
                "model_a": model_a,
                "response_a": content_a,
                "model_b": model_b,
                "response_b": content_b
            })
            
    # Display comparison history
    if st.session_state.compare_history:
        st.markdown("---")
        st.subheader("📜 Previous Comparisons")
        
        for idx, item in enumerate(reversed(st.session_state.compare_history)):
            with st.expander(f"Comparison {len(st.session_state.compare_history) - idx}: {item['prompt'][:60]}..."):
                col_hist_a, col_hist_b = st.columns(2)
                with col_hist_a:
                    st.markdown(f"**Model A: {item['model_a']}**")
                    st.info(item['response_a'])
                with col_hist_b:
                    st.markdown(f"**Model B: {item['model_b']}**")
                    st.info(item['response_b'])
