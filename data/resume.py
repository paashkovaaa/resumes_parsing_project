from dataclasses import dataclass
from typing import List


@dataclass
class Resume:
    position: str
    experience: str
    skills: List[str]
    location: str
    salary: str
    link: str = ""

    def score(self, keywords: List[str]):
        """
        Calculate the relevance score of the resume based on various attributes.

        Scoring Criteria:
        - Job position: +2 points if specified.
        - Experience: +2 points if specified.
        - Skills: +2 points if specified.
        - Location: +1 point if specified.
        - Salary: +1 point if specified.
        - Skills matching keywords: +2 points for each matching skill.

        Args:
            keywords (List[str]): List of keywords to match in the skills section.

        Returns:
            int: Total relevance score for the resume.
        """

        score = 0

        if self.position != "Unknown":
            score += 2

        if self.experience != "Unknown":
            score += 2

        if self.skills != "Unknown":
            score += 2

        if self.location != "Unknown":
            score += 1

        if self.salary != "Unknown":
            score += 1

        skill_keywords = set(keywords)
        matching_skills = skill_keywords.intersection(set(self.skills))
        score += 2 * len(matching_skills)

        return score
