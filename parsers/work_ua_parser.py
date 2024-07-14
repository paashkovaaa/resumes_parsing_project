import re
import requests
from bs4 import BeautifulSoup
from data.resume import Resume
from utils.filters import sort_resumes_by_relevance


class WorkUAParser:
    BASE_URL = "https://www.work.ua/resumes"

    EXPERIENCE_MAP = {
        "0": "0",  # No experience
        "1": "1",  # Up to 1 year
        "2": "164",  # From 1 to 2
        "3": "165",  # From 2 to 5
        "4": "166",  # More than 5
    }

    SALARY_MAP = {
        "5000": "5",  # up to 5000
        "15000": "11",  # up to 15000
        "20000": "12",  # up to 20000
        "25000": "13",  # up to 25000
        "30000": "14",  # up to 30000
        "40000": "15",  # up to 40000
        "50000": "16",  # up to 50000
        "100000": "17",  # up to 100000
    }

    @staticmethod
    def fetch_resumes(
        position, location=None, keywords=None, experience=None, salary=None, limit=None
    ):
        """
        Fetches resumes from Robota.ua based on the given position, location, keywords and limit.

        Args:
            position (str): The job position to search for.
            location (str, optional): The location to search in. Defaults to None.
            keywords (str, optional): The keywords to search for. Defaults to None.
            experience (int, optional): The experience to search for. Defaults to None.
            salary (int, optional): The salary to search for. Defaults to None.
            limit (int, optional): The maximum number of resumes to return. Defaults to None.

        Returns:
            list: A list of Resume objects.

        """
        try:
            page = 1
            resumes = []

            while True:
                url = WorkUAParser._build_work_ua_url(
                    position, location, experience, salary, page
                )
                response = requests.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                resume_ids = WorkUAParser._extract_resume_ids(soup)
                if not resume_ids:
                    break

                for resume_id in resume_ids:
                    resume_url = f"{WorkUAParser.BASE_URL}/{resume_id}/"
                    resume_response = requests.get(resume_url)
                    resume_response.raise_for_status()

                    resume_soup = BeautifulSoup(resume_response.content, "html.parser")
                    resume = WorkUAParser.parse_resume(resume_soup, resume_url)
                    if resume:
                        resumes.append(resume)
                    else:
                        print(f"Failed to parse resume at URL: {resume_url}")

                if not WorkUAParser._has_next_page(soup):
                    break

                page += 1

            sorted_resumes = sort_resumes_by_relevance(resumes, keywords)
            if limit:
                sorted_resumes = sorted_resumes[:limit]

            return sorted_resumes

        except requests.exceptions.RequestException as e:
            print(f"Error fetching resumes: {e}")
            return []

        except Exception as e:
            print(f"Error parsing resumes: {e}")
            return []

    @staticmethod
    def _has_next_page(soup):
        """
        Checks if there is a next page available in the pagination.
        """
        next_page = soup.find("a", class_="glyphicon-chevron-right")
        if next_page and "pointer-none-in-all" not in next_page.get("class", []):
            return True
        return False

    @staticmethod
    def _build_work_ua_url(position, location, experience, salary, page):
        """
        Builds the URL for Work.ua based on the given position, location, minimum experience, and maximum salary.

        Args:
            position (str): The job position to search for.
            location (str, optional): The location to search in. Defaults to None.
            experience (str, optional): Years of experience required. Defaults to None.
            salary (str, optional): Maximum expected salary. Defaults to None.
            page (int, optional): The page to search for.

        Returns:
            str: The constructed URL.
        """
        base_url = WorkUAParser.BASE_URL
        position = position.replace(" ", "+")
        if location:
            url = f"{base_url}-{location}-{position}/"
        else:
            url = f"{base_url}-{position}/"

        query_params = []
        if salary and salary in WorkUAParser.SALARY_MAP:
            query_params.append(f"salaryto={WorkUAParser.SALARY_MAP[salary]}")
        if experience and experience in WorkUAParser.EXPERIENCE_MAP:
            query_params.append(f"experience={WorkUAParser.EXPERIENCE_MAP[experience]}")
        if query_params:
            url += "?" + "&".join(query_params)

        url += f"&page={page}"

        return url

    @staticmethod
    def _extract_resume_ids(soup):
        return [
            a_tag["name"] for a_tag in soup.select("a[name]") if a_tag["name"].isdigit()
        ]

    @staticmethod
    def parse_resume(soup, link):
        """
        Parses a resume from the given BeautifulSoup object.
        """
        try:
            job_position = WorkUAParser._extract_job_position(soup)
            experience = WorkUAParser._extract_experience(soup)
            skills = WorkUAParser._extract_skills(soup)
            location = WorkUAParser._extract_location(soup)
            salary = WorkUAParser._extract_salary(soup)

            return Resume(job_position, experience, skills, location, salary, link)

        except Exception as e:
            print(f"Error parsing individual resume: {e}")
            return None

    @staticmethod
    def _extract_job_position(soup):
        """
        Extracts the job position from the resume.
        """
        position_tag = soup.find("h2", class_="mt-lg sm:mt-xl")
        return position_tag.get_text(strip=True) if position_tag else "Unknown"

    @staticmethod
    def _extract_experience(soup):
        """
        Extracts the work experience from the resume.
        """
        experience_field = soup.find("h2", text="Досвід роботи")
        if not experience_field:
            return "0 years, 0 months"

        experience_tags = []
        for sibling in experience_field.find_next_siblings():
            if sibling.name == "h2" and sibling.get_text(strip=True) == "Освіта":
                break
            experience_tags.extend(sibling.find_all("span", class_="text-default-7"))

        total_experience_years, total_experience_months = 0, 0
        for tag in experience_tags:
            experience_text = tag.get_text(strip=True)
            years_match = re.search(r"(\d+)\s*(рік|роки|років)", experience_text)
            months_match = re.search(
                r"(\d+)\s*(місяць|місяці|місяців)", experience_text
            )

            if years_match:
                total_experience_years += int(years_match.group(1))
            if months_match:
                total_experience_months += int(months_match.group(1))

        total_experience_years += total_experience_months // 12
        total_experience_months = total_experience_months % 12
        return f"{total_experience_years} years, {total_experience_months} months"

    @staticmethod
    def _extract_skills(soup):

        skills_tags = soup.find_all("span", class_="label label-skill label-gray-100")
        skills = [
            tag.find("span", class_="ellipsis").get_text(strip=True).lower()
            for tag in skills_tags
        ]

        return ", ".join(skills)

    @staticmethod
    def _extract_location(soup):
        """
        Extracts the location from the resume.
        """
        location_tag = soup.find("dt", text="Місто проживання:")
        return (
            location_tag.find_next_sibling("dd").get_text(strip=True)
            if location_tag
            else "Unknown"
        )

    @staticmethod
    def _extract_salary(soup):
        """
        Extracts the salary from the resume.
        """
        salary_tag = soup.find("span", class_="text-muted-print")
        return salary_tag.get_text(strip=True)[2:] if salary_tag else "Unknown"
