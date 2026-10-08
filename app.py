"""
ARCHIMEDES — Visual Intelligence for Physics, Mathematics & Science

A Streamlit visual AI tutor:

- Upload a scientific image
- Ask questions about it
- Analyze images with a multimodal AI model through OpenRouter
- Continue the conversation
- Email the latest explanation through Gmail
"""

import base64
import re
from email.mime.text import MIMEText

import requests
import streamlit as st

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from prompts import SYSTEM_PROMPT


# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL = "openrouter/free"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ARCHIMEDES",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# CUSTOM UI
# ============================================================================

st.markdown(
    """
    <style>

    /* Main page spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main title */
    .archimedes-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }

    .archimedes-subtitle {
        font-size: 1.05rem;
        opacity: 0.72;
        margin-bottom: 1.5rem;
    }

    /* Feature cards */
    .feature-card {
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.18);
        margin-bottom: 0.7rem;
    }

    /* Sidebar branding */
    .sidebar-brand {
        font-size: 1.7rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .sidebar-subtitle {
        opacity: 0.7;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    /* Image container */
    .image-label {
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* Small footer */
    .archimedes-footer {
        text-align: center;
        opacity: 0.5;
        font-size: 0.8rem;
        margin-top: 3rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# SECRETS
# ============================================================================

def get_secret(name: str) -> str:
    """
    Safely retrieve a Streamlit secret.

    Returns an empty string if the secret does not exist.
    Secrets are never displayed.
    """
    try:
        return str(st.secrets[name]).strip()
    except Exception:
        return ""


OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY")
GMAIL_ADDRESS = get_secret("GMAIL_ADDRESS")


# ============================================================================
# SESSION STATE
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_image" not in st.session_state:
    st.session_state.current_image = None

if "current_image_type" not in st.session_state:
    st.session_state.current_image_type = None

if "current_image_sig" not in st.session_state:
    st.session_state.current_image_sig = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "last_email_status" not in st.session_state:
    st.session_state.last_email_status = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_math(text: str) -> str:
    """
    Convert common LaTeX delimiters into formats that
    Streamlit's Markdown renderer handles well.
    """

    if not text:
        return ""

    # Display math: \[ ... \] -> $$ ... $$
    text = re.sub(
        r"\\\[(.+?)\\\]",
        lambda match: (
            "\n$$\n"
            + match.group(1).strip()
            + "\n$$\n"
        ),
        text,
        flags=re.DOTALL,
    )

    # Inline math: \( ... \) -> $ ... $
    text = re.sub(
        r"\\\((.+?)\\\)",
        lambda match: (
            "$"
            + match.group(1).strip()
            + "$"
        ),
        text,
        flags=re.DOTALL,
    )

    return text


def get_latest_assistant_message():
    """
    Return the latest ARCHIMEDES response.
    """

    for message in reversed(st.session_state.messages):

        if (
            message.get("role") == "assistant"
            and message.get("content", "").strip()
        ):
            return message["content"]

    return None


def build_messages(user_question: str) -> list:
    """
    Build the multimodal OpenRouter conversation.

    Structure:

    System prompt
        ↓
    Previous conversation
        ↓
    Current user question + current image
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # Previous conversation
    for message in st.session_state.messages:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"],
            }
        )

    # Current question
    if st.session_state.current_image:

        image_url = (
            f"data:{st.session_state.current_image_type};"
            f"base64,{st.session_state.current_image}"
        )

        current_content = [
            {
                "type": "text",
                "text": user_question,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            },
        ]

    else:

        current_content = user_question

    messages.append(
        {
            "role": "user",
            "content": current_content,
        }
    )

    return messages


# ============================================================================
# OPENROUTER AI
# ============================================================================

def ask_archimedes(user_question: str):
    """
    Send the user's question, image and conversation history
    to OpenRouter.

    Returns:

        (answer, None)

    or:

        (None, error_message)
    """

    if not OPENROUTER_API_KEY:

        return None, (
            "OpenRouter API key is missing. "
            "Add OPENROUTER_API_KEY to Streamlit secrets."
        )

    messages = build_messages(user_question)

    try:

        response = requests.post(
            OPENROUTER_URL,

            headers={
                "Authorization": (
                    f"Bearer {OPENROUTER_API_KEY}"
                ),
                "Content-Type": "application/json",
                "HTTP-Referer": (
                    "https://archimedes.streamlit.app"
                ),
                "X-Title": "ARCHIMEDES",
            },

            json={
                "model": MODEL,
                "messages": messages,
            },

            timeout=180,
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:

        return None, (
            "ARCHIMEDES took too long to respond. "
            "Please try again."
        )

    except requests.exceptions.ConnectionError:

        return None, (
            "Could not connect to OpenRouter. "
            "Please check your internet connection."
        )

    except requests.exceptions.HTTPError:

        detail = ""

        try:

            error_data = response.json().get(
                "error",
                {}
            )

            if isinstance(error_data, dict):

                detail = error_data.get(
                    "message",
                    ""
                )

        except Exception:
            pass

        message = (
            f"OpenRouter returned HTTP "
            f"{response.status_code}."
        )

        if response.status_code in (401, 403):

            message += (
                " Your API key may be invalid "
                "or unavailable."
            )

        elif response.status_code == 429:

            message += (
                " Rate limit reached. "
                "Please wait and try again."
            )

        if detail:

            message += f" Details: {detail}"

        return None, message

    except requests.exceptions.RequestException as error:

        return None, (
            "Unexpected network problem: "
            f"{type(error).__name__}."
        )

    # ------------------------------------------------------------------------
    # Parse response
    # ------------------------------------------------------------------------

    try:

        data = response.json()

        answer = (
            data["choices"][0]
            ["message"]
            ["content"]
        )

    except (
        ValueError,
        KeyError,
        IndexError,
        TypeError,
    ):

        return None, (
            "OpenRouter returned an unexpected "
            "response. Please try again."
        )

    # Some models can return content as a list.
    if isinstance(answer, list):

        answer = "".join(
            part.get("text", "")
            for part in answer
            if isinstance(part, dict)
        )

    answer = str(answer).strip()

    if not answer:

        return None, (
            "ARCHIMEDES received an empty answer. "
            "Please try again."
        )

    return answer, None


# ============================================================================
# GMAIL API
# ============================================================================

def send_explanation_email(
    recipient: str,
    explanation: str,
):
    """
    Send the latest ARCHIMEDES explanation using
    the Gmail API.

    Returns:

        (True, None) on success

    or:

        (False, error_message) on failure
    """

    try:

        # ------------------------------------------------------------
        # Load OAuth credentials
        # ------------------------------------------------------------

        creds = Credentials.from_authorized_user_file(
            "token.json",
            [
                "https://www.googleapis.com/auth/gmail.send"
            ],
        )

        # ------------------------------------------------------------
        # Build Gmail API service
        # ------------------------------------------------------------

        service = build(
            "gmail",
            "v1",
            credentials=creds,
        )

        # ------------------------------------------------------------
        # Create email
        # ------------------------------------------------------------

        message = MIMEText(
            (
                "ARCHIMEDES\n"
                "Visual Intelligence for Physics, "
                "Mathematics & Science\n\n"
                "----------------------------------------\n\n"
                f"{explanation}\n"
            ),
            "plain",
            "utf-8",
        )

        message["Subject"] = (
            "ARCHIMEDES — Your Scientific Explanation"
        )

        message["From"] = GMAIL_ADDRESS
        message["To"] = recipient

        # ------------------------------------------------------------
        # Encode email for Gmail API
        # ------------------------------------------------------------

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        # ------------------------------------------------------------
        # Send through Gmail API
        # ------------------------------------------------------------

        result = service.users().messages().send(
            userId="me",
            body={
                "raw": raw_message
            },
        ).execute()

        print(
            "Gmail API Message ID:",
            result.get("id")
        )

        return True, None

    except FileNotFoundError:

        return False, (
            "Gmail OAuth token was not found. "
            "Make sure token.json exists in "
            "the ARCHIMEDES folder."
        )

    except Exception as error:

        return False, (
            "Gmail API could not send the email: "
            f"{type(error).__name__}: {error}"
        )


# ============================================================================
# CLEAR CONVERSATION
# ============================================================================

def clear_conversation():
    """
    Reset the conversation and uploaded image.
    """

    st.session_state.messages = []

    st.session_state.current_image = None

    st.session_state.current_image_type = None

    st.session_state.current_image_sig = None

    st.session_state.last_email_status = None

    st.session_state.uploader_key += 1


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">🧠 ARCHIMEDES</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Visual Intelligence for Physics, '
        'Mathematics & Science.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Capabilities")

    st.markdown(
        """
        📷 **Image Understanding**

        🧮 **Mathematical Reasoning**

        ⚙️ **Physics Problem Solving**

        📐 **Geometry Analysis**

        🔬 **Scientific Explanation**

        📖 **Step-by-Step Teaching**
        """
    )

    st.divider()

    st.button(
        "🗑️ Clear Conversation",
        on_click=clear_conversation,
        use_container_width=True,
    )

    st.divider()

    # ------------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------------

    st.markdown("### 📧 Save Explanation")

    st.caption(
        "Email the latest ARCHIMEDES explanation."
    )

    email_address = st.text_input(
        "Email address",
        placeholder="you@example.com",
        key="email_address",
    )

    if st.button(
        "📧 Send Latest Explanation",
        use_container_width=True,
    ):

        recipient = email_address.strip()

        latest = get_latest_assistant_message()

        if not recipient:

            st.warning(
                "Please enter an email address first."
            )

        elif not EMAIL_PATTERN.match(recipient):

            st.error(
                "Please enter a valid email address."
            )

        elif latest is None:

            st.warning(
                "Ask ARCHIMEDES a question first."
            )

        else:

            with st.spinner(
                "📧 Sending explanation..."
            ):

                success, error = (
                    send_explanation_email(
                        recipient,
                        latest,
                    )
                )

            if success:

                st.success(
                    "Explanation sent successfully! 📧"
                )

            else:

                st.error(error)


# ============================================================================
# MAIN HEADER
# ============================================================================

st.markdown(
    '<div class="archimedes-title">'
    '🧠 ARCHIMEDES'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="archimedes-subtitle">'
    'Visual Intelligence for Physics, Mathematics & Science.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================================
# API STATUS
# ============================================================================

if not OPENROUTER_API_KEY:

    st.warning(
        "⚠️ OpenRouter API key is not configured. "
        "Add OPENROUTER_API_KEY to Streamlit secrets."
    )


# ============================================================================
# IMAGE UPLOAD
# ============================================================================

st.markdown("### 📷 Upload a Scientific Image")

st.caption(
    "Upload a problem, diagram, equation, graph, "
    "circuit, experiment or scientific notes."
)

uploaded_file = st.file_uploader(
    "Choose an image",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp",
    ],
    key=f"uploader_{st.session_state.uploader_key}",
)


# ============================================================================
# PROCESS IMAGE
# ============================================================================

if uploaded_file is not None:

    signature = (
        uploaded_file.name,
        uploaded_file.size,
    )

    if signature != st.session_state.current_image_sig:

        image_bytes = uploaded_file.getvalue()

        st.session_state.current_image = (
            base64.b64encode(
                image_bytes
            ).decode("utf-8")
        )

        st.session_state.current_image_type = (
            uploaded_file.type or "image/png"
        )

        st.session_state.current_image_sig = signature


# ============================================================================
# IMAGE PREVIEW
# ============================================================================

if st.session_state.current_image:

    with st.expander(
        "🖼️ Current Scientific Image",
        expanded=True,
    ):

        st.image(
            base64.b64decode(
                st.session_state.current_image
            ),
            caption=(
                "ARCHIMEDES will use this image "
                "for your questions."
            ),
            use_container_width=True,
        )

else:

    st.info(
        "Upload an image above, or ask ARCHIMEDES "
        "a text-only question."
    )


st.divider()


# ============================================================================
# CHAT HISTORY
# ============================================================================

if not st.session_state.messages:

    st.markdown("### 💡 Try asking")

    st.markdown(
        """
        **Explain the diagram step by step.**

        **Solve this problem and show all working.**

        **What physics principle is shown here?**

        **Explain this equation intuitively.**
        """
    )


for message in st.session_state.messages:

    role = message.get("role")

    content = message.get(
        "content",
        "",
    )

    with st.chat_message(role):

        if role == "assistant":

            st.markdown(
                normalize_math(content)
            )

        else:

            st.markdown(content)


# ============================================================================
# CHAT INPUT
# ============================================================================

user_question = st.chat_input(
    "Ask ARCHIMEDES a question..."
)


# ============================================================================
# PROCESS QUESTION
# ============================================================================

if user_question:

    # ------------------------------------------------------------------------
    # Display user message
    # ------------------------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(user_question)

    # ------------------------------------------------------------------------
    # Ask AI
    # ------------------------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🧠 ARCHIMEDES is analyzing..."
        ):

            answer, error = ask_archimedes(
                user_question
            )

        if error:

            st.error(error)

        else:

            # Display answer
            st.markdown(
                normalize_math(answer)
            )

            # Save conversation only after
            # successful AI generation.
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_question,
                }
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )


# ============================================================================
# FOOTER
# ============================================================================

st.markdown(
    """
    <div class="archimedes-footer">
        ARCHIMEDES • Visual Intelligence for Physics,
        Mathematics & Science
    </div>
    """,








    
    unsafe_allow_html=True,
)