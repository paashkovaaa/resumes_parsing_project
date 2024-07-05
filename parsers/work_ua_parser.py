import re

import requests
from bs4 import BeautifulSoup
from data.resume import Resume


class WorkUAParser:
    BASE_URL = "https://www.work.ua/resumes"

    @staticmethod
    def fetch_resumes(position, location=None):
        try:
            if location:
                url = f"{WorkUAParser.BASE_URL}-{location}-{position}/"
            else:
                url = f"{WorkUAParser.BASE_URL}/-{position}/"

            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            resumes = []

            resume_ids = [
                a_tag["name"]
                for a_tag in soup.select("a[name]")
                if a_tag["name"].isdigit()
            ]

            for resume_id in resume_ids:
                resume_url = f"{WorkUAParser.BASE_URL}/{resume_id}/"
                resume_response = requests.get(resume_url)
                resume_response.raise_for_status()

                resume_soup = BeautifulSoup(resume_response.content, "html.parser")
                resume = WorkUAParser.parse_resume(resume_soup)
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
    def parse_resume(soup):
        try:
            position_tag = soup.find("h2", class_="mt-lg sm:mt-xl")
            job_position = (
                position_tag.get_text(strip=True) if position_tag else "Unknown"
            )

            experience_field = soup.find("h2", text="Досвід роботи")
            if not experience_field:
                experience = "0 years, 0 months"
            else:
                experience_tags = []
                for sibling in experience_field.find_next_siblings():
                    if (
                        sibling.name == "h2"
                        and sibling.get_text(strip=True) == "Освіта"
                    ):
                        break
                    experience_tags.extend(
                        sibling.find_all("span", class_="text-default-7")
                    )

                total_experience_years = 0
                total_experience_months = 0
                for tag in experience_tags:
                    experience_text = tag.get_text(strip=True)
                    years_match = re.search(
                        r"(\d+)\s*(рік|роки|років)", experience_text
                    )
                    months_match = re.search(
                        r"(\d+)\s*(місяць|місяці|місяців)", experience_text
                    )

                    if years_match:
                        total_experience_years += int(years_match.group(1))
                    if months_match:
                        total_experience_months += int(months_match.group(1))

                total_experience_years += total_experience_months // 12
                total_experience_months = total_experience_months % 12
                experience = (
                    f"{total_experience_years} years, {total_experience_months} months"
                )

            skills_tags = soup.find_all(
                "span",
                class_="label label-skill label-gray-100",
            )
            skills = [
                tag.find("span", class_="ellipsis").get_text(strip=True)
                for tag in skills_tags
            ]

            location_tag = soup.find("dt", text="Місто проживання:")
            city = (
                location_tag.find_next_sibling("dd").get_text(strip=True)
                if location_tag
                else "Unknown"
            )

            salary_tag = soup.find("span", class_="text-muted-print")
            salary = salary_tag.get_text(strip=True) if salary_tag else "Unknown"

            return Resume(job_position, experience, skills, city, salary)
        except Exception as e:
            print(f"Error parsing individual resume: {e}")
            return None
