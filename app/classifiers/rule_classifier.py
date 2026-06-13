def Categorize(text: str):

    t = text.lower()

    if any(k in t for k in ["github", "project", "api", "docker"]):
        return "Projects"

    if any(k in t for k in ["resume", "cv", "internship", "job"]):
        return "Internships"

    if any(k in t for k in ["lecture", "course", "paper", "university"]):
        return "Learning"

    return "Other"