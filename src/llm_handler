def generate_response(query, retrieved_papers):
    if not retrieved_papers:
        return "No relevant research papers found."

    response = "Top relevant research papers:\n\n"

    for i, paper in enumerate(retrieved_papers, 1):
        response += f"{i}. {paper['title']} ({paper['year']})\n"

    return response
