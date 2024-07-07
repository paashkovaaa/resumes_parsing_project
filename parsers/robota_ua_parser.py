from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from data.resume import Resume


class RobotaUAParser:
    BASE_URL = "https://robota.ua/candidates"

    @staticmethod
    def fetch_resumes(position, location=None):
        try:
            options = ChromeOptions()
            options.headless = False  # Set to True for production
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--incognito")

            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()), options=options
            )

            if location:
                url = f"{RobotaUAParser.BASE_URL}/{position}/{location}/"
            else:
                url = f"{RobotaUAParser.BASE_URL}/{position}/ukraine/"

            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "santa-no-underline"))
            )

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, "html.parser")
            resumes = []

            resume_links = soup.find_all("a", class_="santa-no-underline")
            if not resume_links:
                print("No resume links found.")
                driver.quit()
                return []

            for link in resume_links:
                href = link.get("href")
                if href and href.startswith("/candidates/"):
                    resume_id = href.split("/")[-1]
                    resume_url = f"{RobotaUAParser.BASE_URL}/{resume_id}/"

                    driver.get(resume_url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "santa-typo-regular")
                        )
                    )

                    resume_page_content = driver.page_source
                    resume_soup = BeautifulSoup(resume_page_content, "html.parser")
                    resume = RobotaUAParser.parse_resume(resume_soup)
                    if resume:
                        resumes.append(resume)
                    else:
                        print(f"Failed to parse resume with ID: {resume_id}")

            driver.quit()
            return resumes

        except Exception as e:
            print(f"Error fetching resumes: {e}")
            return []

    @staticmethod
    def parse_resume(soup):
        try:
            position_tag = soup.find(
                "p", class_="santa-mt-10 santa-typo-secondary santa-text-black-700"
            )
            job_position = (
                position_tag.get_text(strip=True) if position_tag else "Unknown"
            )

            experience_tag = soup.find(
                "span",
                class_="santa-text-red-500 santa-whitespace-nowrap",
            )
            experience = (
                experience_tag.get_text(strip=True) if experience_tag else "Unknown"
            )

            skills_tag = soup.find(
                "div",
                class_="santa-m-0 santa-mb-20 760:santa-mb-40 last:santa-mb-0 santa-typo-regular santa-text-black-700 santa-list empty:santa-hidden",
            )
            skills = skills_tag.get_text(strip=True) if skills_tag else "Unknown"

            location_tag = soup.find("lib-resume-main-info").find(
                "p", class_="santa-typo-regular santa-text-black-700"
            )

            location = location_tag.get_text(strip=True) if location_tag else "Unknown"

            resume_main_info = soup.find("lib-resume-main-info")

            if resume_main_info.find(
                "p", class_="santa-flex santa-items-center santa-mb-10"
            ):
                salary_tag = resume_main_info.find(
                    "p",
                    class_="santa-flex santa-items-center santa-mb-10",
                ).find("span", class_="santa-typo-regular santa-text-black-700")
                salary = salary_tag.get_text(strip=True)

            else:
                salary = "Unknown"

            return Resume(job_position, experience, skills, location, salary)

        except Exception as e:
            print(f"Error parsing individual resume: {e}")
            return None
