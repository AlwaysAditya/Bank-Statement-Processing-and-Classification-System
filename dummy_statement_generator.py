from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime, timedelta
import random


# ============================================================
# SYNTHETIC ACCOUNT STATEMENT GENERATOR
# ============================================================
# Creates exactly ONE synthetic PDF per execution.
#
# The PDF uses real-world bank/merchant names as transaction
# data, but uses fictional account identifiers and a generic
# document layout.
#
# IMPORTANT:
# Category is NOT included in the generated statement.
# The classifier must determine the category itself.
#
# Date format:
# DD/MM/YYYY
# ============================================================


REAL_BANK_NAMES = [
    "HDFC Bank",
    "ICICI Bank",
    "State Bank of India",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "IndusInd Bank",
    "Yes Bank",
    "IDFC FIRST Bank",
    "Federal Bank",
    "Bank of Baroda",
    "Punjab National Bank",
    "Canara Bank",
    "Union Bank of India",
    "Bank of India",
    "Indian Bank",
    "AU Small Finance Bank",
    "RBL Bank",
    "South Indian Bank",
    "IDBI Bank",
    "Bandhan Bank",
]


CUSTOMERS = [
    "Aarav Mehta",
    "Priya Nair",
    "Rohan Kapoor",
    "Sneha Rao",
    "Vikram Shah",
    "Ananya Iyer",
    "Karan Malhotra",
    "Neha Verma",
    "Arjun Menon",
    "Ishita Das",
    "Rahul Sen",
    "Maya Joshi",
    "Aditya Kumar",
    "Kavya Reddy",
    "Nikhil Sharma",
    "Meera Patel",
]


BRANCHES = [
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Gurugram",
    "Noida",
    "Jaipur",
    "Kochi",
    "Indore",
    "Chandigarh",
]


# ============================================================
# INTERNAL CATEGORY → MERCHANT MAPPING
# ============================================================
# Category is used ONLY to select realistic merchants.
# Category is NOT written into the PDF.
#
# Later, this can also be used as ground truth for evaluating
# the classifier if we decide to build a controlled dataset.
# ============================================================

CATEGORIES = {
    "Groceries": [
        ("DMart", 250, 6000),
        ("BigBasket", 250, 5000),
        ("Blinkit", 100, 3000),
        ("Zepto", 100, 3000),
        ("Swiggy Instamart", 150, 4000),
    ],

    "Food & Dining": [
        ("Swiggy", 150, 3000),
        ("Zomato", 150, 3000),
        ("McDonald's", 150, 1500),
        ("Domino's", 200, 1800),
        ("Starbucks", 250, 2000),
    ],

    "Transport": [
        ("Uber", 100, 2500),
        ("Ola", 100, 2500),
        ("Rapido", 50, 1200),
        ("Indian Oil", 500, 6000),
        ("HPCL", 500, 6000),
        ("Bharat Petroleum", 500, 6000),
    ],

    "Utilities": [
        ("Airtel", 199, 3000),
        ("Jio", 199, 3000),
        ("Vi", 199, 3000),
        ("ACT Fibernet", 500, 2500),
        ("Tata Play", 250, 1500),
        ("BESCOM", 500, 6000),
        ("Adani Electricity", 500, 6000),
    ],

    "Shopping": [
        ("Amazon", 300, 15000),
        ("Flipkart", 300, 15000),
        ("Myntra", 500, 10000),
        ("Ajio", 500, 10000),
        ("Reliance Digital", 1000, 30000),
        ("Croma", 1000, 30000),
    ],

    "Entertainment": [
        ("Netflix", 149, 999),
        ("Spotify", 119, 999),
        ("YouTube Premium", 129, 999),
        ("BookMyShow", 200, 4000),
        ("PVR INOX", 250, 4000),
        ("Sony LIV", 299, 999),
    ],

    "Healthcare": [
        ("Apollo Pharmacy", 150, 5000),
        ("Tata 1mg", 150, 5000),
        ("PharmEasy", 150, 5000),
        ("Netmeds", 150, 5000),
        ("Apollo Hospitals", 500, 25000),
    ],

    "Insurance": [
        ("LIC", 1000, 30000),
        ("HDFC Life", 1000, 30000),
        ("ICICI Prudential Life", 1000, 30000),
        ("SBI Life", 1000, 30000),
        ("Max Life Insurance", 1000, 30000),
    ],

    "Investments": [
        ("SBI Mutual Fund", 500, 30000),
        ("HDFC Mutual Fund", 500, 30000),
        ("ICICI Prudential Mutual Fund", 500, 30000),
        ("Axis Mutual Fund", 500, 30000),
        ("Nippon India Mutual Fund", 500, 30000),
    ],

    "Travel & Booking": [
        ("IRCTC", 200, 10000),
        ("MakeMyTrip", 500, 30000),
        ("Cleartrip", 500, 30000),
        ("EaseMyTrip", 500, 30000),
        ("Air India", 2000, 50000),
        ("IndiGo", 2000, 50000),
    ],
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_synthetic_account_id():
    """Generate a fictional account identifier."""

    return "SYN-ACCT-" + "".join(
        random.choices(
            "0123456789",
            k=8,
        )
    )


def random_transaction_reference():
    """Generate a fictional transaction reference."""

    return "TEST-" + "".join(
        random.choices(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            k=10,
        )
    )


# ============================================================
# MAIN GENERATOR
# ============================================================

def create_random_statement(filename=None):
    """
    Create exactly ONE random synthetic account statement PDF.

    If filename is omitted, the PDF is saved to the user's
    Downloads folder.
    """

    # --------------------------------------------------------
    # Random account information
    # --------------------------------------------------------

    bank = random.choice(
        REAL_BANK_NAMES
    )

    customer = random.choice(
        CUSTOMERS
    )

    branch = random.choice(
        BRANCHES
    )

    transaction_count = random.randint(
        35,
        70,
    )

    # --------------------------------------------------------
    # Generate valid date range
    # --------------------------------------------------------

    start_date = datetime(
        random.randint(2024, 2026),
        random.randint(1, 12),
        random.randint(1, 20),
    )

    end_date = start_date + timedelta(
        days=transaction_count - 1
    )

    # --------------------------------------------------------
    # Default output → Downloads
    # --------------------------------------------------------

    if filename is None:

        downloads_dir = (
            Path.home() / "Downloads"
        )

        downloads_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            downloads_dir
            / (
                "synthetic_statement_"
                + datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )
                + "_"
                + str(
                    random.randint(
                        1000,
                        9999,
                    )
                )
                + ".pdf"
            )
        )

    filename = str(
        Path(filename)
        .expanduser()
        .resolve()
    )

    Path(filename).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Create PDF
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=32,
        bottomMargin=32,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Account Statement",
            styles["Title"],
        )
    )

    story.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # Account information
    # --------------------------------------------------------

    info = [
        ["Bank Name", bank],

        ["Customer", customer],

        [
            "Synthetic Account ID",
            random_synthetic_account_id(),
        ],

        [
            "Transaction Reference",
            random_transaction_reference(),
        ],

        [
            "Branch / City",
            branch,
        ],

        [
            "Statement Period",
            (
                f"{start_date:%d/%m/%Y}"
                f" to "
                f"{end_date:%d/%m/%Y}"
            ),
        ],

        [
            "Document Type",
            "Synthetic test dataset",
        ],
    ]

    info_table = Table(
        info,
        colWidths=[
            160,
            350,
        ],
    )

    info_table.setStyle(
        TableStyle([
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica",
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.whitesmoke,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.grey,
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(info_table)

    story.append(
        Spacer(
            1,
            18,
        )
    )

    # ========================================================
    # TRANSACTION TABLE
    # ========================================================
    # IMPORTANT:
    # No Category column.
    # ========================================================

    data = [[
        "Date",
        "Merchant / Description",
        "Debit",
        "Credit",
        "Balance",
    ]]

    balance = random.randint(
        25000,
        250000,
    )

    # Salary date
    salary_day = random.randint(
        1,
        5,
    )

    # Second credit date
    second_credit_day = random.randint(
        max(
            7,
            transaction_count // 3,
        ),
        max(
            8,
            transaction_count // 2,
        ),
    )

    # ========================================================
    # GENERATE TRANSACTIONS
    # ========================================================

    for i in range(
        transaction_count
    ):

        date = (
            start_date
            + timedelta(days=i)
        )

        # ----------------------------------------------------
        # Salary
        # ----------------------------------------------------

        if i + 1 == salary_day:

            credit = random.randint(
                35000,
                120000,
            )

            balance += credit

            data.append([
                date.strftime(
                    "%d/%m/%Y"
                ),

                "SALARY CREDIT",

                "",

                f"{credit:,.2f}",

                f"{balance:,.2f}",
            ])

            continue

        # ----------------------------------------------------
        # Other income
        # ----------------------------------------------------

        if i + 1 == second_credit_day:

            credit = random.randint(
                2500,
                20000,
            )

            balance += credit

            data.append([
                date.strftime(
                    "%d/%m/%Y"
                ),

                random.choice([
                    "CLIENT PAYMENT",
                    "FREELANCE PAYMENT",
                    "TRANSFER CREDIT",
                ]),

                "",

                f"{credit:,.2f}",

                f"{balance:,.2f}",
            ])

            continue

        # ----------------------------------------------------
        # Refund / cashback
        # ----------------------------------------------------

        if random.random() < 0.08:

            credit = random.randint(
                100,
                5000,
            )

            balance += credit

            data.append([
                date.strftime(
                    "%d/%m/%Y"
                ),

                random.choice([
                    "AMAZON REFUND",
                    "FLIPKART REFUND",
                    "SWIGGY REFUND",
                    "ZOMATO REFUND",
                    "CASHBACK CREDIT",
                ]),

                "",

                f"{credit:,.2f}",

                f"{balance:,.2f}",
            ])

            continue

        # ----------------------------------------------------
        # Normal expense
        # ----------------------------------------------------

        # Category is selected internally ONLY to choose
        # a realistic merchant.
        category = random.choice(
            list(CATEGORIES.keys())
        )

        merchant, minimum, maximum = random.choice(
            CATEGORIES[category]
        )

        amount = random.randint(
            minimum,
            maximum,
        )

        # Keep balance positive.
        if amount > balance - 1000:

            amount = max(
                100,
                int(balance * 0.10),
            )

        balance -= amount

        data.append([
            date.strftime(
                "%d/%m/%Y"
            ),

            merchant,

            f"{amount:,.2f}",

            "",

            f"{balance:,.2f}",
        ])

    # ========================================================
    # TRANSACTION TABLE FORMAT
    # ========================================================

    table = Table(
        data,
        colWidths=[
            70,
            220,
            70,
            70,
            85,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(
                    "#444444"
                ),
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                8,
            ),

            (
                "FONTSIZE",
                (0, 1),
                (-1, -1),
                7,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                colors.grey,
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "RIGHT",
            ),

            (
                "TOPPADDING",
                (0, 1),
                (-1, -1),
                3,
            ),

            (
                "BOTTOMPADDING",
                (0, 1),
                (-1, -1),
                3,
            ),
        ])
    )

    story.append(table)

    story.append(
        Spacer(
            1,
            12,
        )
    )

    story.append(
        Paragraph(
            "Dummy Bank Statement",
            styles["Normal"],
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(story)

    # ========================================================
    # LOG
    # ========================================================

    print("=" * 60)
    print("GENERATED ONE RANDOM SYNTHETIC PDF")
    print("=" * 60)

    print(
        f"Bank data field : {bank}"
    )

    print(
        f"Customer        : {customer}"
    )

    print(
        f"Transactions    : {transaction_count}"
    )

    print(
        f"Categories      : {len(CATEGORIES)}"
    )

    print(
        f"Output          : {filename}"
    )

    return filename


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    # Exactly ONE new random PDF per execution.
    create_random_statement()