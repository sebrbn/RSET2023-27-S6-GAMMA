# ---------------------------------------------------
# RAG CONTEXT BUILDER
# ---------------------------------------------------

def build_explanation_context(
    resume_data,
    jd_data
):

    context = f"""
    JOB REQUIREMENTS:

    Skills Required:
    {', '.join(jd_data['skills'])}

    Experience Required:
    {jd_data['experience']} years


    CANDIDATE PROFILE:

    Skills Found:
    {', '.join(resume_data['skills'])}

    Experience:
    {resume_data['experience']} years
    """

    return context
