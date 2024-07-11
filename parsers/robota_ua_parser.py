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

    @staticmethod
    def fetch_resumes(position, location=None, keywords=None, limit=None):
        """
        Fetches resumes from Robota.ua based on the given position, location, keywords and limit.

        Args:
            position (str): The job position to search for.
            location (str, optional): The location to search in. Defaults to None.
            keywords (str, optional): The keywords to search for. Defaults to None.
            limit (int, optional): The maximum number of resumes to fetch. Defaults to None.

        Returns:
            list: A list of Resume objects.

        """
        try:
            driver = WebDriverConfig.get_driver()
            url = RobotaUAParser._build_url(position, location)
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "santa-no-underline"))
            )

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, "html.parser")
            resumes = []

            resume_links = RobotaUAParser._extract_resume_links(soup)
            if not resume_links:
                print("No resume links found.")
                driver.quit()
                return []

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
            sorted_resumes = sort_resumes_by_relevance(resumes, keywords)
            if limit:
                sorted_resumes = sorted_resumes[:limit]

            driver.quit()
            return sorted_resumes

        except Exception as e:
            print(f"Error fetching resumes: {e}")
            return []

    @staticmethod
    def _build_url(position, location):
        if location:
            return f"{RobotaUAParser.BASE_URL}/{position}/{location}/"
        else:
            return f"{RobotaUAParser.BASE_URL}/{position}/ukraine/"

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
        return skills_tag.get_text(strip=True).lower() if skills_tag else "Unknown"

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
