import re


# ============================================================
# TRANSACTION CLASSIFICATION
# ============================================================
# Non-LLM rule-based classification.
#
# Input:
#     Transaction description
#
# Output:
#     Category
# ============================================================


CATEGORY_KEYWORDS = {

    # ========================================================
    # GROCERIES
    # ========================================================

    "Groceries": [
        "dmart",
        "bigbasket",
        "blinkit",
        "zepto",
        "swiggy instamart",
        "jiomart",
        "reliance smart",
        "reliance fresh",
        "spencers",
        "more supermarket",

        "walmart",
        "kroger",
        "whole foods",
        "trader joes",
        "safeway",
        "publix",
        "aldi",

        "tesco",
        "sainsburys",
        "asda",
        "morrisons",
        "waitrose",
        "ocado",

        "loblaws",
        "sobeys",
        "metro grocery",
        "nofrills",

        "woolworths",
        "coles",
        "iga australia",
    ],


    # ========================================================
    # FOOD & DINING
    # ========================================================

    "Food & Dining": [
        "swiggy",
        "zomato",

        # Domino's variations
        "domino",
        "dominos",
        "domino s",
        "domino pizza",
        "dominos pizza",

        "mcdonald",
        "mcdonalds",
        "mcdonald s",

        "kfc",
        "pizza hut",
        "starbucks",
        "burger king",
        "wendy",
        "wendys",
        "taco bell",
        "chipotle",
        "chick fil a",
        "dunkin",

        "pret a manger",
        "greggs",
        "pizza express",
        "wagamama",

        "tim hortons",
        "harveys",
        "pizza pizza",
        "second cup",

        "hungry jacks",
        "grilld",
        "boost juice",
        "guzman y gomez",
    ],


    # ========================================================
    # TRANSPORT
    # ========================================================

    "Transport": [
        "uber",
        "ola",
        "rapido",

        "indian oil",
        "hpcl",
        "bharat petroleum",
        "reliance petrol",

        "lyft",
        "shell",
        "exxon",
        "chevron",
        "bp",

        "esso",
        "national express",
        "stagecoach",

        "petro canada",
        "presto",

        "ampol",
        "caltex",
        "7 eleven fuel",
    ],


    # ========================================================
    # UTILITIES
    # ========================================================

    "Utilities": [
        "airtel",
        "jio",
        "vi",
        "act fibernet",
        "tata play",
        "bescom",
        "adani electricity",
        "tata power",

        "comcast",
        "verizon",
        "at&t",
        "t mobile",
        "spectrum",
        "xfinity",

        "bt",
        "sky",
        "virgin media",
        "vodafone",
        "o2",
        "ee",

        "bell canada",
        "rogers",
        "telus",
        "shaw",
        "fido",

        "telstra",
        "optus",
        "tpg telecom",
        "aussie broadband",
        "origin energy",
    ],


    # ========================================================
    # SHOPPING
    # ========================================================

    "Shopping": [
        "amazon",
        "flipkart",
        "myntra",
        "ajio",
        "reliance digital",
        "croma",
        "tata cliq",

        "ebay",
        "best buy",
        "target",
        "macys",
        "nordstrom",
        "kohls",
        "costco",

        "argos",
        "john lewis",
        "marks spencer",
        "next",
        "currys",

        "canadian tire",
        "hudsons bay",
        "winners",
        "simons",

        "kmart",
        "big w",
        "myer",
        "harvey norman",
        "jb hi fi",
    ],


    # ========================================================
    # ENTERTAINMENT
    # ========================================================

    "Entertainment": [
        "netflix",
        "spotify",
        "youtube premium",
        "bookmyshow",
        "pvr",
        "inox",
        "sony liv",
        "jiosaavn",
        "hotstar",

        "hulu",
        "disney",
        "max",
        "paramount",
        "peacock",
        "apple tv",

        "bbc iplayer",
        "itvx",
        "now tv",
        "sky cinema",

        "crave",
        "cbc gem",
        "bell fibe",

        "stan",
        "binge",
        "foxtel",
        "abc iview",
        "7plus",
    ],


    # ========================================================
    # HEALTHCARE
    # ========================================================

    "Healthcare": [
        "apollo pharmacy",
        "apollo hospitals",
        "tata 1mg",
        "pharmeasy",
        "netmeds",
        "fortis",
        "max healthcare",
        "manipal hospitals",

        "cvs pharmacy",
        "walgreens",
        "rite aid",
        "cigna",
        "kaiser permanente",
        "mayo clinic",
        "cleveland clinic",

        "boots",
        "lloyds pharmacy",
        "superdrug",
        "nhs",

        "shoppers drug mart",
        "rexall",
        "london drugs",
        "pharmasave",

        "chemist warehouse",
        "terrywhite chemmart",
        "priceline pharmacy",
        "amcal",
    ],


    # ========================================================
    # INSURANCE
    # ========================================================

    "Insurance": [
        "lic",
        "hdfc life",
        "icici prudential",
        "sbi life",
        "max life",
        "tata aia",
        "bajaj allianz",
        "star health",

        "state farm",
        "geico",
        "allstate",
        "progressive",
        "liberty mutual",
        "farmers insurance",
        "nationwide",

        "aviva",
        "admiral",
        "direct line",
        "legal general",
        "axa",

        "manulife",
        "sun life",
        "desjardins insurance",
        "intact insurance",
        "td insurance",

        "qbe",
        "iag",
        "suncorp",
        "aami",
        "nrma",
    ],


    # ========================================================
    # INVESTMENTS
    # ========================================================

    "Investments": [
        "sbi mutual fund",
        "hdfc mutual fund",
        "icici prudential mutual fund",
        "axis mutual fund",
        "nippon india mutual fund",
        "aditya birla sun life",
        "kotak mutual fund",
        "mirae asset",

        "vanguard",
        "fidelity",
        "blackrock",
        "charles schwab",
        "td ameritrade",
        "morgan stanley",
        "jpmorgan investments",
        "etrade",

        "hargreaves lansdown",
        "aj bell",
        "fidelity uk",
        "barclays investments",
        "interactive investor",

        "wealthsimple",
        "questrade",
        "rbc direct investing",
        "td direct investing",
        "bmo investorline",

        "commsec",
        "selfwealth",
        "stake",
        "superhero",
        "nabtrade",
    ],


    # ========================================================
    # TRAVEL & BOOKING
    # ========================================================

    "Travel & Booking": [
        "irctc",
        "makemytrip",
        "cleartrip",
        "easemytrip",
        "air india",
        "indigo",
        "vistara",
        "akasa air",

        "delta air lines",
        "united airlines",
        "american airlines",
        "southwest airlines",
        "jetblue",
        "expedia",
        "booking.com",
        "airbnb",

        "british airways",
        "easyjet",
        "ryanair",
        "virgin atlantic",
        "tui",
        "trainline",

        "air canada",
        "westjet",
        "porter airlines",
        "via rail",

        "qantas",
        "virgin australia",
        "jetstar",
        "rex airlines",
        "webjet",
    ],


    # ========================================================
    # INCOME
    # ========================================================

    "Income": [
        "salary",
        "salary credit",
        "payroll",
        "payroll credit",
        "wages",
        "wage credit",
        "client payment",
        "freelance payment",
        "transfer credit",
        "direct deposit",
        "paycheck",
    ],


    # ========================================================
    # REFUND / CASHBACK
    # ========================================================

    # Keep these BEFORE generic merchant keywords in the
    # classifier matching priority.
    "Refund / Cashback": [
        "amazon refund",
        "flipkart refund",
        "swiggy refund",
        "zomato refund",
        "dominos refund",
        "domino refund",
        "merchant refund",

        "refund credit",
        "refund",
        "cashback",
        "cash back",
        "chargeback",
        "reversal",
    ],
}

# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_description(description):
    """
    Normalize transaction description before classification.
    """

    if description is None:
        return ""

    text = str(description).lower().strip()

    # Remove excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ============================================================
# SINGLE TRANSACTION CLASSIFICATION
# ============================================================

def classify_transaction(description):
    """
    Classify one transaction using keyword rules.

    Returns:
        Category
    """

    text = normalize_description(
        description
    )

    if not text:
        return "Unknown"

    # --------------------------------------------------------
    # Check categories
    # --------------------------------------------------------

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                return category

    # --------------------------------------------------------
    # No rule matched
    # --------------------------------------------------------

    return "Other"


# ============================================================
# CLASSIFY DATAFRAME
# ============================================================

def classify_transactions(df):
    """
    Add a Category column to transaction DataFrame.
    """

    df = df.copy()

    df["Category"] = (
        df["Description"]
        .apply(classify_transaction)
    )

    return df