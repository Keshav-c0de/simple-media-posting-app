import streamlit as st
import requests
import base64
import urllib.parse

st.set_page_config(page_title="Simple Social", layout="wide")

# Use 127.0.0.1 for better stability on local machines
BASE_URL = "http://127.0.0.1:8000"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("🚀 Welcome to Simple Social")

    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                login_data = {"username": email, "password": password}
                try:
                    # FastAPI Users uses lowercase 'jwt' in the default path
                    response = requests.post(f"{BASE_URL}/auth/jwt/login", data=login_data)

                    if response.status_code == 200:
                        token_data = response.json()
                        st.session_state.token = token_data.get("access_token")

                        # Get user info
                        user_response = requests.get(f"{BASE_URL}/users/me", headers=get_headers())
                        if user_response.status_code == 200:
                            st.session_state.user = user_response.json()
                            st.rerun()
                        else:
                            st.error("Logged in, but failed to fetch user profile.")
                    else:
                        st.error("Invalid email or password!")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to Backend. Is Uvicorn running?")

        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                signup_data = {"email": email, "password": password}
                try:
                    response = requests.post(f"{BASE_URL}/auth/register", json=signup_data)
                    if response.status_code == 201:
                        st.success("Account created! You can now Login.")
                    else:
                        error_detail = response.json().get("detail", "Registration failed")
                        st.error(f"Error: {error_detail}")
                except requests.exceptions.ConnectionError:
                    st.error("Backend server is offline.")
    else:
        st.info("Enter your credentials to continue")


def upload_page():
    st.title("📸 Share Something")

    uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.success("Posted successfully!")
                st.rerun()
            else:
                st.error(f"Upload failed (Status: {response.status_code})")


def encode_text_for_overlay(text):
    if not text: return ""
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if not original_url: return ""
    
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    try:
        parts = original_url.split("/")
        # Standard ImageKit structure: https://ik.imagekit.io/your_id/endpoint/file.jpg
        base_url = "/".join(parts[:4])
        file_path = "/".join(parts[4:])
        return f"{base_url}/tr:{transformation_params}/{file_path}"
    except Exception:
        return original_url


def feed_page():
    st.title("🏠 Feed")

    try:
        response = requests.get(f"{BASE_URL}/feed", headers=get_headers())
        if response.status_code == 200:
            posts = response.json().get("posts", [])

            if not posts:
                st.info("The feed is empty. Start by uploading something!")
                return

            for post in posts:
                st.markdown("---")
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{post.get('email', 'User')}** • {post.get('created_at', '')[:10]}")
                
                with col2:
                    # Logic for showing delete button
                    if post.get('is_owner', False):
                        if st.button("🗑️", key=f"del_{post['id']}"):
                            # Note: Route changed to singular /post/ to match your backend
                            res = requests.delete(f"{BASE_URL}/post/{post['id']}", headers=get_headers())
                            if res.status_code == 200:
                                st.rerun()
                            else:
                                st.error("Delete failed")

                caption = post.get('caption', '')
                # Basic display logic
                if "image" in post.get('file_type', 'image'):
                    img_url = create_transformed_url(post['url'], "", caption)
                    st.image(img_url, use_container_width=True)
                else:
                    st.video(post['url'])
                    st.caption(caption)
        else:
            st.error("Failed to load feed data.")
    except Exception as e:
        st.error(f"Feed error: {e}")


# App Entry Point
if st.session_state.user is None:
    login_page()
else:
    st.sidebar.title(f"👋 {st.session_state.user.get('email')}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    choice = st.sidebar.radio("Menu", ["🏠 Feed", "📸 Upload"])

    if choice == "🏠 Feed":
        feed_page()
    else:
        upload_page()