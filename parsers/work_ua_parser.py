import re

import requests
from bs4 import BeautifulSoup
from data.resume import Resume


class WorkUAParser:
    BASE_URL = "https://www.work.ua/resumes"

    @staticmethod
    def fetch_resumes(position, location=None):
        """
        Fetches resumes from Work.ua based on the given position and location.

        Args:
            position (str): The job position to search for.
            location (str, optional): The location to search in. Defaults to None.

        Returns:
            list: A list of Resume objects.
        """
        try:
            url = WorkUAParser._build_url(position, location)
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            resumes = []

            resume_ids = WorkUAParser._extract_resume_ids(soup)
            for resume_id in resume_ids:
                resume_url = f"{WorkUAParser.BASE_URL}/{resume_id}/"
                resume_response = requests.get(resume_url)
                resume_response.raise_for_status()

                resume_soup = BeautifulSoup(resume_response.content, "html.parser")
                resume = WorkUAParser.parse_resume(resume_soup, resume_url)
                if resume:
                    resumes.append(resume)

            return resumes

        except requests.exceptions.RequestException as e:
            print(f"Error fetching resumes: {e}")
            return []

        except Exception as e:
            print(f"Error parsing resumes: {e}")
            return []

    @staticmethod
    def _build_url(position, location):
        if location:
            return f"{WorkUAParser.BASE_URL}-{location}-{position}/"
        else:
            return f"{WorkUAParser.BASE_URL}/-{position}/"

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
        """
        Extracts the skills from the resume.
        """
        skills_tags = soup.find_all("span", class_="label label-skill label-gray-100")
        return [
            tag.find("span", class_="ellipsis").get_text(strip=True)
            for tag in skills_tags
        ]

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
        return salary_tag.get_text(strip=True) if salary_tag else "Unknown"
