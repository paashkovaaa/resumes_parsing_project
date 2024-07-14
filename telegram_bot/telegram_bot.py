import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from parsers.robota_ua_parser import RobotaUAParser
from parsers.work_ua_parser import WorkUAParser

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

(
    SELECT_SITE,
    SET_POSITION,
    SET_LOCATION,
    SET_YEARS_OF_EXPERIENCE,
    SET_EXPECTED_SALARY,
    SET_KEYWORDS,
    FETCH_RESUMES,
) = range(7)

user_data = {}


async def start(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation and asks the user to choose a site.
    """

    reply_keyboard = [["work.ua", "robota.ua"]]

    await update.message.reply_text(
        "Welcome to the Resumes Parser Bot!\n\n"
        "Please choose the site you want to parse resumes from.\n\n"
        "<i>If nothing happens, please try again</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )

    return SELECT_SITE


async def select_site(update: Update, context: CallbackContext) -> int:
    """
    Stores the selected site and asks for the job position.
    """
    site = update.message.text
    if site not in ["work.ua", "robota.ua"]:
        await update.message.reply_text(
            "Invalid site selected. Please choose either 'work.ua' or 'robota.ua'."
        )
        return SELECT_SITE

    user_data[update.message.from_user.id] = {"site": site}
    await update.message.reply_text(
        f"You have selected {site}.\n\nPlease set the job position you want to search (example: data scientist):\n\n"
        "If nothing happens, please try again"
    )
    return SET_POSITION


async def set_position(update: Update, context: CallbackContext) -> int:
    """
    Stores the job position and asks for the location.
    """
    position = update.message.text.lower()
    user_data[update.message.from_user.id]["position"] = position
    await update.message.reply_text(
        f"Position set to {position}.\n\nPlease enter the location (example: kyiv) or type 'skip' to skip:\n\n"
        "If nothing happens, please try again"
    )
    return SET_LOCATION


async def set_location(update: Update, context: CallbackContext) -> int:
    """
    Stores the location and asks for years of experience.
    """
    location = update.message.text.lower()

    if location != "skip":
        user_data[update.message.from_user.id]["location"] = location
    else:
        user_data[update.message.from_user.id]["location"] = None

    site = user_data[update.message.from_user.id]["site"]
    if site == "work.ua":
        await update.message.reply_text(
            "Location set.\n\nPlease enter the years of experience\n"
            "(0 - No experience,\n"
            "1 - Up to 1 year,\n"
            "2 - From 1 to 2,\n"
            "3 - From 2 to 5,\n"
            "4 - More than 5 years)\n"
            "or type 'skip' to skip.\n\n"
            "If nothing happens, please try again"
        )

    if site == "robota.ua":
        await update.message.reply_text(
            "Location set.\n\nPlease enter the years of experience\n"
            "(0 - No experience,\n"
            "1 - Up to 1 year,\n"
            "2 - From 1 to 2,\n"
            "3 - From 2 to 5,\n"
            "4 - From 5 to 10 years,\n"
            "5 - More than 10 years)\n"
            "or type 'skip' to skip.\n\n"
            "If nothing happens, please try again"
        )
    return SET_YEARS_OF_EXPERIENCE


async def set_years_of_experience(update: Update, context: CallbackContext) -> int:
    """
    Stores the minimum years of experience and asks for expected salary.
    """
    experience = update.message.text.lower()
    site = user_data[update.message.from_user.id]["site"]

    if site == "work.ua":
        if experience != "skip":
            if experience in WorkUAParser.EXPERIENCE_MAP.keys():
                user_data[update.message.from_user.id]["experience"] = experience
            else:
                await update.message.reply_text(
                    "Invalid input.\n\nPlease enter the years of experience\n"
                    "(0 - No experience,\n"
                    "1 - Up to 1 year,\n"
                    "2 - From 1 to 2,\n"
                    "3 - From 2 to 5,\n"
                    "4 - More than 5 years)\n"
                    "5 - More than 10 years) or type 'skip' to skip."
                )
                return SET_YEARS_OF_EXPERIENCE
        else:
            user_data[update.message.from_user.id]["experience"] = None

        await update.message.reply_text(
            "Years of experience set.\n\n"
            "Please enter the expected maximum salary in uah\n\n"
            "Possible options:\n"
            "5000, 15000, 20000, 25000, 30000, 40000, 50000, 100000\n"
            "or type 'skip' to skip:\n\n"
            "If nothing happens, please try again"
        )

    if site == "robota.ua":
        if experience != "skip":
            user_data[update.message.from_user.id]["experience"] = experience
        else:
            user_data[update.message.from_user.id]["experience"] = None

        await update.message.reply_text(
            "Years of experience set.\n\n"
            "Please enter the expected maximum salary in uah (example: 75000)\n"
            "or type 'skip' to skip:\n\n"
            "If nothing happens, please try again"
        )

    return SET_EXPECTED_SALARY


async def set_expected_salary(update: Update, context: CallbackContext) -> int:
    """
    Stores the expected maximum salary and asks for keywords.
    """
    salary = update.message.text.lower()
    site = user_data[update.message.from_user.id]["site"]
    if site == "work.ua":
        if salary != "skip":
            if salary in WorkUAParser.SALARY_MAP.keys():
                user_data[update.message.from_user.id]["salary"] = salary
            else:
                await update.message.reply_text(
                    "Please enter the expected maximum salary in uah\n\n"
                    "Possible options:\n"
                    "5000, 15000, 20000, 25000, 30000, 40000, 50000, 100000\n"
                    "or type 'skip' to skip:\n\n"
                    "If nothing happens, please try again"
                )
        else:
            user_data[update.message.from_user.id]["salary"] = None
    if site == "robota.ua":
        if salary != "skip":
            user_data[update.message.from_user.id]["salary"] = salary
        else:
            user_data[update.message.from_user.id]["salary"] = None

    await update.message.reply_text(
        "Expected maximum salary set.\n\n"
        "Please enter the keywords, separated by commas (example: python, sql) or type 'skip' to skip:\n\n"
        "If nothing happens, please try again"
    )
    return SET_KEYWORDS


async def set_keywords(update: Update, context: CallbackContext) -> int:
    """
    Stores the keywords and asks the user to fetch resumes.
    """
    keywords = update.message.text.lower()
    if keywords != "skip":
        user_data[update.message.from_user.id]["keywords"] = [
            keyword.strip() for keyword in keywords.split(",")
        ]
    else:
        user_data[update.message.from_user.id]["keywords"] = []

    await update.message.reply_text(
        "Keywords set.\n\nType /fetch to get resumes based on these criteria.\n\n"
        "If nothing happens, please try again",
        reply_markup=ReplyKeyboardRemove(),
    )

    return FETCH_RESUMES


async def fetch_resumes(update: Update, context: CallbackContext) -> int:
    """
    Fetches the resumes based on the stored criteria.
    """
    await update.message.reply_text("Fetching resumes, please wait...")

    site = user_data[update.message.from_user.id]["site"]
    position = user_data[update.message.from_user.id]["position"]
    location = user_data[update.message.from_user.id]["location"]
    keywords = user_data[update.message.from_user.id]["keywords"]
    experience = user_data[update.message.from_user.id].get("experience")
    salary = user_data[update.message.from_user.id].get("salary")

    if site == "work.ua":
        resumes = WorkUAParser.fetch_resumes(
            position,
            location,
            keywords,
            limit=5,
            experience=experience,
            salary=salary,
        )
    elif site == "robota.ua":
        resumes = RobotaUAParser.fetch_resumes(
            position,
            location,
            keywords,
            limit=5,
            experience=experience,
            salary=salary,
        )

    if resumes:
        for resume in resumes:
            await update.message.reply_text(
                f"<b>Position:</b> {resume.position}\n"
                f"<b>Experience:</b> {resume.experience}\n"
                f"<b>Skills:</b> {resume.skills}\n"
                f"<b>Location:</b> {resume.location}\n"
                f"<b>Salary:</b> {resume.salary}\n"
                f"<a href='{resume.link}'>Resume Link</a>",
                parse_mode="HTML",
            )
    else:
        await update.message.reply_text("No resumes found.")

    await update.message.reply_text("If you want to start again print /start")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """
    Cancels the current conversation.
    """
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END
