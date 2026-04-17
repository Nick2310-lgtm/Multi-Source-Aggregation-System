import streamlit as st
from src.rag_pipeline import RAGSystem

st.set_page_config(page_title="Multi-Source Research Paper Aggregation System")

st.title("Multi-Source Research Paper Aggregation System")

if "system" not in st.session_state:
    st.session_state.system = RAGSystem()

query = st.text_input("Enter research topic")

if st.button("Search"):
    if query.strip():
        results = st.session_state.system.query(query)

        if not results:
            st.warning("No results found")
        else:
            st.write(f"Top Results: {len(results)}")

            for i, p in enumerate(results):
                with st.expander(f"{i+1}. {p['title']}"):
                    st.write(f"Source: {p['source']}")
                    st.write(f"Authors: {p['authors']}")
                    st.write(f"Year: {p['year']}")
                    st.write(f"Abstract: {p['abstract']}")
    else:
        st.warning("Enter a valid query")