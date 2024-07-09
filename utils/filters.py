from typing import List
from data.resume import Resume


def sort_resumes_by_relevance(
    resumes: List[Resume], keywords: List[str]
) -> List[Resume]:
    """
    Sorts resumes by relevance based on a scoring mechanism.

    Args:
        resumes (List[Resume]): List of Resume objects.
        keywords (List[str]): List of keywords to match in the skills section.

    Returns:
        List[Resume]: Sorted list of Resume objects based on relevance score.
    """
    for resume in resumes:
        resume.relevance_score = resume.score(keywords)

    sorted_resumes = sorted(resumes, key=lambda x: x.relevance_score, reverse=True)

    return sorted_resumes
