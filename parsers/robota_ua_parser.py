from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from data.resume import Resume
from utils.filters import sort_resumes_by_relevance


class WebDriverConfig:
    @staticmethod
    def get_driver():
        options = ChromeOptions()
        options.headless = True
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--incognito")

        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )


class RobotaUAParser:
    BASE_URL = "https://robota.ua/candidates"

    EXPERIENCE_MAP = {
        "0": "0",  # With no experience
        "1": "1",  # Up to 1 year
        "2": "2",  # From 1 to 2
        "3": "3",  # From 2 to 5
        "4": "4",  # From 5 to 10
        "5": "5",  # More than 10
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
            driver = WebDriverConfig.get_driver()
            page = 1
            resumes = []

            while True:
                url = RobotaUAParser._build_robota_ua_url(
                    position, location, page, experience, salary
                )
                driver.get(url)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "santa-no-underline")
                    )
                )

                page_content = driver.page_source
                soup = BeautifulSoup(page_content, "html.parser")

                resume_links = RobotaUAParser._extract_resume_links(soup)
                if not resume_links:
                    break

                for link in resume_links:
                    resume_url = RobotaUAParser._build_resume_url(link)
                    driver.get(resume_url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "santa-typo-regular")
                        )
                    )

                    resume_page_content = driver.page_source
                    resume_soup = BeautifulSoup(resume_page_content, "html.parser")
                    resume = RobotaUAParser.parse_resume(resume_soup, resume_url)
                    if resume:
                        resumes.append(resume)
                    else:
                        print(f"Failed to parse resume at URL: {resume_url}")

                if not RobotaUAParser._has_next_page(soup):
                    break

                page += 1

            sorted_resumes = sort_resumes_by_relevance(resumes, keywords)
            if limit:
                sorted_resumes = sorted_resumes[:limit]

            driver.quit()
            return sorted_resumes

        except Exception as e:
            print(f"Error fetching resumes: {e}")
            return []

    @staticmethod
    def _has_next_page(soup):
        """
        Checks if there is a next page available in the pagination.
        """
        pagination = soup.find("santa-pagination-with-links")
        if pagination:
            active_link = pagination.find("a", class_="active")
            if active_link and active_link.find_next_sibling("a"):
                return True
        return False

    @staticmethod
    def _build_robota_ua_url(position, location, page, experience, salary):
        """
        Builds the URL for Robota.ua based on the given position, location, minimum experience, and maximum salary.

        Args:
            position (str): The job position to search for.
            location (str, optional): The location to search in. Defaults to None.
            experience (str, optional): Years of experience required. Defaults to None.
            salary (str, optional): Maximum expected salary. Defaults to None.
            page (int, optional): The page to search for.

        Returns:
            str: The constructed URL.
        """
        base_url = RobotaUAParser.BASE_URL
        position = position.replace(" ", "-")

        if location:
            url = f"{base_url}/{position}/{location}"
        else:
            url = f"{base_url}/{position}/ukraine"

        url += f"?page={page}&"

        query_params = []
        if salary:
            query_params.append(
                rf"salary=%7B%22from%22%3Anull%2C%22to%22%3A{salary}%7D"
            )
        if experience:
            query_params.append(rf"experienceIds=%5B%22{experience}%22%5D")
        if query_params:
            url += "&".join(query_params)

        return url

    @staticmethod
    def _extract_resume_links(soup):
        return [
            link.get("href")
            for link in soup.find_all("a", class_="santa-no-underline")
            if link.get("href") and link.get("href").startswith("/candidates/")
        ]

    @staticmethod
    def _build_resume_url(link):
        resume_id = link.split("/")[-1]
        return f"{RobotaUAParser.BASE_URL}/{resume_id}/"

    @staticmethod
    def parse_resume(soup, link):
        """
        Parses a resume from the given BeautifulSoup object.
        """
        try:
            job_position = RobotaUAParser._extract_job_position(soup)
            experience = RobotaUAParser._extract_experience(soup)
            skills = RobotaUAParser._extract_skills(soup)
            location = RobotaUAParser._extract_location(soup)
            salary = RobotaUAParser._extract_salary(soup)

            return Resume(job_position, experience, skills, location, salary, link)

        except Exception as e:
            print(f"Error parsing individual resume: {e}")
            return None

    @staticmethod
    def _extract_job_position(soup):
        """
        Extracts the job position from the resume.
        """
        position_tag = soup.find(
            "p", class_="santa-mt-10 santa-typo-secondary santa-text-black-700"
        )
        return position_tag.get_text(strip=True) if position_tag else "Unknown"

    @staticmethod
    def _extract_experience(soup):
        """
        Extracts the work experience from the resume.
        """
        experience_tag = soup.find(
            "span",
            class_="santa-text-red-500 santa-whitespace-nowrap",
        )
        return experience_tag.get_text(strip=True) if experience_tag else "Unknown"

    @staticmethod
    def _extract_skills(soup):
        """
        Extracts the skills from the resume.
        """
        skills_tag = soup.find(
            "div",
            class_="santa-m-0 santa-mb-20 760:santa-mb-40 last:santa-mb-0 santa-typo-regular santa-text-black-700 santa-list empty:santa-hidden",
        )
        if not skills_tag:
            return "Unknown"

        skill_elements = skills_tag.find_all(["p", "li"])

        if skill_elements:
            skills = [skill.get_text(strip=True) for skill in skill_elements]
        else:
            skills = skills_tag.get_text(strip=True).split(", ")

        return ", ".join(skills).lower()

    @staticmethod
    def _extract_location(soup):
        """
        Extracts the location from the resume.
        """
        location_info = soup.find("lib-resume-main-info")
        if location_info:
            location_tag = location_info.find(
                "p", class_="santa-typo-regular santa-text-black-700"
            )
            return location_tag.get_text(strip=True)
        else:
            return "Unknown"

    @staticmethod
    def _extract_salary(soup):
        """
        Extracts the salary from the resume.
        """
        resume_main_info_tag = soup.find("lib-resume-main-info")
        if resume_main_info_tag:
            salary_info = resume_main_info_tag.find(
                "p", class_="santa-flex santa-items-center santa-mb-10"
            )
            if salary_info:
                salary_tag = salary_info.find(
                    "span", class_="santa-typo-regular santa-text-black-700"
                )
                return salary_tag.get_text(strip=True) if salary_tag else "Unknown"
            else:
                return "Unknown"
        else:
            return "Unknown"
