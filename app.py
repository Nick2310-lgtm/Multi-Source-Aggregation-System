import streamlit as st
from src.rag_pipeline import RAGSystem

st.title("Multi-Source Research Paper Aggregation System")

if "system" not in st.session_state:
    st.session_state.system = RAGSystem()

query = st.text_input("Enter research topic")

if st.button("Search"):
    if not query.strip():
        st.warning("Enter a query")
    else:
        with st.spinner("Fetching and ranking papers..."):
            results = st.session_state.system.query(query)

        if not results:
            st.warning("No results found")
        else:
            for i, p in enumerate(results):
                with st.expander(f"{i+1}. {p.get('title','')}"):
                    st.write(f"Source: {p.get('source','')}")
                    st.write(f"Authors: {p.get('authors','')}")
                    st.write(f"Year: {p.get('year','')}")
                    st.write(f"Abstract: {p.get('abstract','')}")
