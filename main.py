from parsers.work_ua_parser import WorkUAParser


def main():
    position = "data-scientist"
    location = "kyiv"

    try:
        all_resumes = WorkUAParser.fetch_resumes(position, location)

        if not all_resumes:
            print("No resumes fetched or an error occurred.")
            return

        for resume in all_resumes:
            print(resume)

    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
