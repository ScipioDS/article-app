import streamlit as st
import requests
import os
from datetime import datetime

# Backend API URL
api_host = os.getenv('API_HOST', 'backend')
API_URL = f'http://{api_host}:5000'

st.title("📝 Article Management System")

# Initialize session state
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'success_message' not in st.session_state:
    st.session_state.success_message = ""
if 'editing_article' not in st.session_state:
    st.session_state.editing_article = None


# Function to load articles
def load_articles():
    try:
        response = requests.get(f'{API_URL}/articles')
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        st.error("Cannot connect to backend service")
    return []


# Show success message if needed
if st.session_state.show_success:
    st.success(st.session_state.success_message)
    st.session_state.show_success = False

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📝 Create Article", "📖 View Articles", "✏️ Edit/Delete"])

with tab1:
    st.header("Create New Article")
    with st.form("create_article_form", clear_on_submit=True):
        title = st.text_input("Title")
        author = st.text_input("Author")
        content = st.text_area("Content", height=150)
        submit = st.form_submit_button("Publish Article")

        if submit and title and author and content:
            article_data = {
                'title': title,
                'author': author,
                'content': content
            }
            response = requests.post(f'{API_URL}/articles', json=article_data)
            if response.status_code == 201:
                st.session_state.show_success = True
                st.session_state.success_message = "Article published successfully! 🎉"

with tab2:
    st.header("Published Articles")
    articles = load_articles()

    if articles:
        for article in articles:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.subheader(article['title'])
                    st.write(f"**By:** {article['author']}")
                    st.write(f"**Published:** {article['created_at'][:10]}")
                    if 'updated_at' in article:
                        st.write(f"**Updated:** {article['updated_at'][:10]}")
                    st.write(article['content'])
                with col2:
                    if st.button("Edit", key=f"edit_{article['id']}"):
                        st.session_state.editing_article = article
                    if st.button("Delete", key=f"delete_{article['id']}", type="secondary"):
                        response = requests.delete(f"{API_URL}/articles/{article['id']}")
                        if response.status_code == 200:
                            st.session_state.show_success = True
                            st.session_state.success_message = "Article deleted successfully! 🗑️"
                st.divider()
    else:
        st.info("No articles published yet. Be the first to publish!")

with tab3:
    st.header("Edit Article")

    if st.session_state.editing_article:
        article = st.session_state.editing_article

        with st.form("edit_article_form"):
            st.write(f"Editing: **{article['title']}**")
            new_title = st.text_input("Title", value=article['title'])
            new_author = st.text_input("Author", value=article['author'])
            new_content = st.text_area("Content", value=article['content'], height=150)

            col1, col2 = st.columns(2)
            with col1:
                update = st.form_submit_button("Update Article", type="primary")
            with col2:
                cancel = st.form_submit_button("Cancel")

            if update and new_title and new_author and new_content:
                update_data = {
                    'title': new_title,
                    'author': new_author,
                    'content': new_content
                }

                # Debug information
                st.write(f"DEBUG: Updating article ID: {article['id']}")
                st.write(f"DEBUG: Article ID type: {type(article['id'])}")
                st.write(f"DEBUG: Update URL: {API_URL}/articles/{article['id']}")

                try:
                    response = requests.put(f"{API_URL}/articles/{article['id']}", json=update_data)
                    st.write(f"DEBUG: Response status: {response.status_code}")
                    st.write(f"DEBUG: Response text: {response.text}")

                    if response.status_code == 200:
                        st.session_state.show_success = True
                        st.session_state.success_message = "Article updated successfully! ✏️"
                        st.session_state.editing_article = None
                    else:
                        st.error(f"Update failed with status code: {response.status_code}")
                        st.error(f"Response: {response.text}")
                except Exception as e:
                    st.error(f"Error updating article: {str(e)}")

            if cancel:
                st.session_state.editing_article = None
    else:
        st.info("Select an article from the 'View Articles' tab to edit it.")

        # Show all articles for selection
        articles = load_articles()
        if articles:
            st.write("**Available Articles:**")
            for article in articles:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {article['title']} by {article['author']}")
                with col2:
                    if st.button("Select", key=f"select_{article['id']}"):
                        st.session_state.editing_article = article
