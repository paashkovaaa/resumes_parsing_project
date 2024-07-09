from parsers.robota_ua_parser import RobotaUAParser
from parsers.work_ua_parser import WorkUAParser
from utils.filters import sort_resumes_by_relevance


def main():
    position = "data-scientist"
    location = "kyiv"
    keywords = ["Python", "Machine Learning", "Data Analysis", "SQL"]

    try:
        all_resumes = RobotaUAParser.fetch_resumes(
            position, location
        ) + WorkUAParser.fetch_resumes(position, location)

        if not all_resumes:
            print("No resumes fetched or an error occurred.")
        else:
            sorted_resumes = sort_resumes_by_relevance(all_resumes, keywords)
            for resume in sorted_resumes:
                print(f"Resume URL: {resume.link}, Score: {resume.score(keywords)}")
                print(resume)

    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
