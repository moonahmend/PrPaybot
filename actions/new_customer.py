from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from actions.buy_tokens import buy_tokens
from actions.create_payment import create_payment
from actions.back_to_menu import back_to_menu
from actions.my_customers import my_customers
from actions.my_orders import my_orders
from actions.marketplace import marketplace
from actions.balance import balance
from actions.subscribe import subscribe
from actions.help import help
import re
import sqlite3
import uuid
from datetime import datetime

# US States and Major Cities Data
US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# Major cities for each state (top 5-10 cities per state)
STATE_CITIES = {
    'AL': ['Birmingham', 'Montgomery', 'Huntsville', 'Mobile', 'Tuscaloosa', 'Auburn', 'Dothan', 'Hoover'],
    'AK': ['Anchorage', 'Fairbanks', 'Juneau', 'Sitka', 'Ketchikan', 'Kodiak', 'Bethel', 'Palmer'],
    'AZ': ['Phoenix', 'Tucson', 'Mesa', 'Chandler', 'Scottsdale', 'Glendale', 'Gilbert', 'Tempe', 'Peoria'],
    'AR': ['Little Rock', 'Fort Smith', 'Fayetteville', 'Springdale', 'Jonesboro', 'North Little Rock', 'Conway', 'Rogers'],
    'CA': ['Los Angeles', 'San Diego', 'San Jose', 'San Francisco', 'Fresno', 'Sacramento', 'Long Beach', 'Oakland', 'Bakersfield', 'Anaheim'],
    'CO': ['Denver', 'Colorado Springs', 'Aurora', 'Fort Collins', 'Lakewood', 'Thornton', 'Arvada', 'Westminster', 'Pueblo', 'Boulder'],
    'CT': ['Bridgeport', 'New Haven', 'Stamford', 'Hartford', 'Waterbury', 'Norwalk', 'Danbury', 'New Britain', 'Bristol', 'Meriden'],
    'DE': ['Wilmington', 'Dover', 'Newark', 'Middletown', 'Smyrna', 'Milford', 'Seaford', 'Georgetown', 'Elsmere', 'New Castle'],
    'FL': ['Jacksonville', 'Miami', 'Tampa', 'Orlando', 'St. Petersburg', 'Hialeah', 'Tallahassee', 'Fort Lauderdale', 'Port St. Lucie', 'Cape Coral'],
    'GA': ['Atlanta', 'Augusta', 'Columbus', 'Macon', 'Savannah', 'Athens', 'Sandy Springs', 'Roswell', 'Albany', 'Johns Creek'],
    'HI': ['Honolulu', 'Hilo', 'Kailua', 'Kapolei', 'Kaneohe', 'Mililani Town', 'Ewa Gentry', 'Kihei', 'Makakilo', 'Wahiawa'],
    'ID': ['Boise', 'Meridian', 'Nampa', 'Idaho Falls', 'Pocatello', 'Caldwell', 'Coeur d\'Alene', 'Twin Falls', 'Lewiston', 'Post Falls'],
    'IL': ['Chicago', 'Aurora', 'Rockford', 'Joliet', 'Naperville', 'Springfield', 'Peoria', 'Elgin', 'Waukegan', 'Champaign'],
    'IN': ['Indianapolis', 'Fort Wayne', 'Evansville', 'South Bend', 'Carmel', 'Bloomington', 'Fishers', 'Hammond', 'Gary', 'Lafayette'],
    'IA': ['Des Moines', 'Cedar Rapids', 'Davenport', 'Sioux City', 'Iowa City', 'Waterloo', 'Ames', 'West Des Moines', 'Council Bluffs', 'Dubuque'],
    'KS': ['Wichita', 'Overland Park', 'Kansas City', 'Olathe', 'Topeka', 'Lawrence', 'Shawnee', 'Manhattan', 'Lenexa', 'Salina'],
    'KY': ['Louisville', 'Lexington', 'Bowling Green', 'Owensboro', 'Covington', 'Richmond', 'Georgetown', 'Florence', 'Elizabethtown', 'Nicholasville'],
    'LA': ['New Orleans', 'Baton Rouge', 'Shreveport', 'Lafayette', 'Lake Charles', 'Kenner', 'Bossier City', 'Monroe', 'Alexandria', 'Houma'],
    'ME': ['Portland', 'Lewiston', 'Bangor', 'South Portland', 'Auburn', 'Biddeford', 'Sanford', 'Brunswick', 'Augusta', 'Scarborough'],
    'MD': ['Baltimore', 'Frederick', 'Rockville', 'Gaithersburg', 'Bowie', 'Hagerstown', 'Annapolis', 'College Park', 'Salisbury', 'Laurel'],
    'MA': ['Boston', 'Worcester', 'Springfield', 'Lowell', 'Cambridge', 'New Bedford', 'Brockton', 'Quincy', 'Lynn', 'Fall River'],
    'MI': ['Detroit', 'Grand Rapids', 'Warren', 'Sterling Heights', 'Ann Arbor', 'Lansing', 'Flint', 'Dearborn', 'Livonia', 'Westland'],
    'MN': ['Minneapolis', 'Saint Paul', 'Rochester', 'Duluth', 'Bloomington', 'Brooklyn Park', 'Plymouth', 'St. Cloud', 'Eagan', 'Woodbury'],
    'MS': ['Jackson', 'Gulfport', 'Southaven', 'Hattiesburg', 'Biloxi', 'Meridian', 'Tupelo', 'Greenville', 'Olive Branch', 'Horn Lake'],
    'MO': ['Kansas City', 'St. Louis', 'Springfield', 'Columbia', 'Independence', 'Lee\'s Summit', 'O\'Fallon', 'St. Joseph', 'St. Charles', 'St. Peters'],
    'MT': ['Billings', 'Missoula', 'Great Falls', 'Bozeman', 'Butte', 'Helena', 'Kalispell', 'Havre', 'Anaconda', 'Miles City'],
    'NE': ['Omaha', 'Lincoln', 'Bellevue', 'Grand Island', 'Kearney', 'Fremont', 'Hastings', 'Norfolk', 'Columbus', 'Scottsbluff'],
    'NV': ['Las Vegas', 'Henderson', 'Reno', 'North Las Vegas', 'Sparks', 'Carson City', 'Fernley', 'Elko', 'Mesquite', 'Boulder City'],
    'NH': ['Manchester', 'Nashua', 'Concord', 'Dover', 'Rochester', 'Keene', 'Derry', 'Portsmouth', 'Laconia', 'Lebanon'],
    'NJ': ['Newark', 'Jersey City', 'Paterson', 'Elizabeth', 'Edison', 'Woodbridge', 'Lakewood', 'Toms River', 'Hamilton', 'Trenton'],
    'NM': ['Albuquerque', 'Las Cruces', 'Rio Rancho', 'Santa Fe', 'Roswell', 'Farmington', 'South Valley', 'Clovis', 'Hobbs', 'Alamogordo'],
    'NY': ['New York City', 'Buffalo', 'Rochester', 'Yonkers', 'Syracuse', 'Albany', 'New Rochelle', 'Mount Vernon', 'Schenectady', 'Utica'],
    'NC': ['Charlotte', 'Raleigh', 'Greensboro', 'Durham', 'Winston-Salem', 'Fayetteville', 'Cary', 'Wilmington', 'High Point', 'Greenville'],
    'ND': ['Fargo', 'Bismarck', 'Grand Forks', 'Minot', 'West Fargo', 'Williston', 'Dickinson', 'Mandan', 'Jamestown', 'Wahpeton'],
    'OH': ['Columbus', 'Cleveland', 'Cincinnati', 'Toledo', 'Akron', 'Dayton', 'Parma', 'Canton', 'Lorain', 'Hamilton'],
    'OK': ['Oklahoma City', 'Tulsa', 'Norman', 'Broken Arrow', 'Lawton', 'Edmond', 'Moore', 'Midwest City', 'Enid', 'Stillwater'],
    'OR': ['Portland', 'Salem', 'Eugene', 'Gresham', 'Hillsboro', 'Beaverton', 'Bend', 'Medford', 'Springfield', 'Corvallis'],
    'PA': ['Philadelphia', 'Pittsburgh', 'Allentown', 'Erie', 'Reading', 'Scranton', 'Bethlehem', 'Lancaster', 'Harrisburg', 'Altoona'],
    'RI': ['Providence', 'Warwick', 'Cranston', 'Pawtucket', 'East Providence', 'Woonsocket', 'Coventry', 'Cumberland', 'North Providence', 'West Warwick'],
    'SC': ['Columbia', 'Charleston', 'North Charleston', 'Mount Pleasant', 'Rock Hill', 'Greenville', 'Summerville', 'Sumter', 'Hilton Head Island', 'Florence'],
    'SD': ['Sioux Falls', 'Rapid City', 'Aberdeen', 'Brookings', 'Watertown', 'Mitchell', 'Yankton', 'Pierre', 'Huron', 'Vermillion'],
    'TN': ['Nashville', 'Memphis', 'Knoxville', 'Chattanooga', 'Clarksville', 'Murfreesboro', 'Franklin', 'Jackson', 'Johnson City', 'Hendersonville'],
    'TX': ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth', 'El Paso', 'Arlington', 'Corpus Christi', 'Plano', 'Lubbock'],
    'UT': ['Salt Lake City', 'West Valley City', 'Provo', 'West Jordan', 'Orem', 'Sandy', 'Ogden', 'St. George', 'Layton', 'South Jordan'],
    'VT': ['Burlington', 'South Burlington', 'Rutland', 'Barre', 'Montpelier', 'Winooski', 'St. Albans', 'Newport', 'Vergennes', 'Middlebury'],
    'VA': ['Virginia Beach', 'Norfolk', 'Arlington', 'Richmond', 'Newport News', 'Alexandria', 'Hampton', 'Roanoke', 'Portsmouth', 'Suffolk'],
    'WA': ['Seattle', 'Spokane', 'Tacoma', 'Vancouver', 'Bellevue', 'Kent', 'Everett', 'Renton', 'Yakima', 'Federal Way'],
    'WV': ['Charleston', 'Huntington', 'Parkersburg', 'Morgantown', 'Wheeling', 'Weirton', 'Fairmont', 'Martinsburg', 'Beckley', 'Clarksburg'],
    'WI': ['Milwaukee', 'Madison', 'Green Bay', 'Kenosha', 'Racine', 'Appleton', 'Waukesha', 'Oshkosh', 'Eau Claire', 'Janesville'],
    'WY': ['Cheyenne', 'Casper', 'Laramie', 'Gillette', 'Rock Springs', 'Sheridan', 'Green River', 'Evanston', 'Riverton', 'Cody']
}

# Define steps and their prompts, and which are mandatory
steps = [
    {"id": 1, "prompt": "📝 <b>Customer Registration Process</b>\n\nLet's collect customer information for order fulfillment. This is a secure 15-step process.\n\n<b>Step 1 of 15: First Name*</b> 👤\nPlease enter the customer's <b>first name*</b>:\n\n💡 <i>Example: John</i>", "mandatory": True, "field": "first_name"},
    {"id": 2, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 2 of 15: Middle Name</b> 👤\nPlease enter the customer's <b>middle name</b> (optional):\n\n💡 <i>Click Skip if they don't have a middle name</i>", "mandatory": False, "field": "middle_name"},
    {"id": 3, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 3 of 15: Last Name*</b> 👤\nPlease enter the customer's <b>last name*</b>:\n\n💡 <i>Example: Doe</i>", "mandatory": True, "field": "last_name"},
    {"id": 4, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 4 of 15: Phone Number*</b> 📞\nPlease enter the customer's <b>phone number*</b> (USA format):\n\n💡 <i>Examples: +1-555-123-4567 or 555-123-4567</i>", "mandatory": True, "field": "phone_number"},
    {"id": 5, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 5 of 15: Email*</b> 📧\nPlease enter the customer's <b>email address*</b>:\n\n💡 <i>Example: john.doe@example.com</i>", "mandatory": True, "field": "email"},
    {"id": 6, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 6 of 15: Gender*</b> ⚧️\nPlease select the customer's <b>gender*</b> from the options below:", "mandatory": True, "field": "gender"},
    {"id": 7, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 7 of 15: Date of Birth</b> 🎂\nPlease enter the customer's <b>date of birth</b> (MM-DD-YYYY):\n\n💡 <i>Format: MM-DD-YYYY (Example: 03-15-1990)</i>", "mandatory": False, "field": "date_of_birth"},
    {"id": 8, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 8 of 15: Street Address*</b> 🏠\nPlease enter the customer's <b>street address*</b>:\n\n💡 <i>Example: 123 Main Street</i>", "mandatory": True, "field": "address_line_1"},
    {"id": 9, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 9 of 15: Apt/Suite</b> 🏢\nPlease enter the customer's <b>apartment or suite</b> (optional):\n\n💡 <i>Example: Apt 4B</i>", "mandatory": False, "field": "address_line_2"},
    {"id": 10, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 10 of 15: State*</b> 🗺️\nPlease select the customer's <b>state*</b> from the options below:", "mandatory": True, "field": "state"},
    {"id": 11, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 11 of 15: City*</b> 🌆\nPlease select the customer's <b>city*</b> from the options below, or type your city name if not listed:", "mandatory": True, "field": "city"},
    {"id": 12, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 12 of 15: ZIP Code*</b> ✉️\nPlease enter the customer's <b>ZIP code*</b> (5 digits):\n\n💡 <i>Example: 90210</i>", "mandatory": True, "field": "postal_code"},
    {"id": 13, "prompt": "📝 <b>Customer Registration Process</b>\n\n<b>Step 13 of 15: Password</b> 🔑\nPlease set a <b>password</b> for the customer (optional):\n\n💡 <i>Click Skip if you don't want to set a password</i>", "mandatory": False, "field": "password"},
]

CITY_ZIP_PREFIXES = {
    'NY': {'New York': ['100', '101', '102']},
    'CA': {
        'Los Angeles': ['900'], 'San Diego': ['921'], 'San Jose': ['951'], 'San Francisco': ['941'], 'Fresno': ['936', '937'], 'Sacramento': ['942', '958'], 'Long Beach': ['908'], 'Oakland': ['946'], 'Bakersfield': ['933'], 'Anaheim': ['928'], 'Santa Ana': ['927'], 'Riverside': ['925'], 'Stockton': ['952'], 'Irvine': ['926'], 'Chula Vista': ['919', '921'], 'Fremont': ['945'], 'San Bernardino': ['924'], 'Modesto': ['953'], 'Oxnard': ['930'], 'Fontana': ['923'],
    },
    'IL': {'Chicago': ['606'], 'Aurora': ['605'], 'Naperville': ['605'], 'Joliet': ['604'], 'Rockford': ['611']},
    'TX': {
        'Houston': ['770'], 'San Antonio': ['782'], 'Dallas': ['752', '753'], 'Austin': ['733', '787'], 'Fort Worth': ['761'], 'El Paso': ['799'], 'Arlington': ['760'], 'Corpus Christi': ['784'], 'Plano': ['750'], 'Laredo': ['780'], 'Lubbock': ['794'], 'Garland': ['750'], 'Irving': ['750'], 'Amarillo': ['791'], 'Grand Prairie': ['750'], 'Brownsville': ['785'], 'McKinney': ['750'], 'Frisco': ['750'], 'Pasadena': ['775'], 'Killeen': ['765'],
    },
    'AZ': {'Phoenix': ['850'], 'Tucson': ['857'], 'Mesa': ['852'], 'Chandler': ['852'], 'Gilbert': ['852'], 'Glendale': ['853'], 'Scottsdale': ['852'], 'Peoria': ['853'], 'Tempe': ['852'], 'Surprise': ['853']},
    'PA': {'Philadelphia': ['190', '191'], 'Pittsburgh': ['152'], 'Allentown': ['181'], 'Erie': ['165'], 'Reading': ['196']},
    'FL': {'Jacksonville': ['320', '322'], 'Miami': ['331'], 'Tampa': ['336'], 'Orlando': ['328'], 'St. Petersburg': ['337'], 'Hialeah': ['330'], 'Tallahassee': ['323'], 'Fort Lauderdale': ['333'], 'Port St. Lucie': ['349'], 'Cape Coral': ['339']},
    'OH': {'Columbus': ['430', '432'], 'Cleveland': ['441'], 'Cincinnati': ['452'], 'Toledo': ['436'], 'Akron': ['443']},
    'NC': {'Charlotte': ['282'], 'Raleigh': ['276'], 'Greensboro': ['274'], 'Durham': ['277'], 'Winston-Salem': ['271']},
    'MI': {'Detroit': ['482'], 'Grand Rapids': ['495'], 'Warren': ['480'], 'Sterling Heights': ['483'], 'Ann Arbor': ['481']},
    'WA': {'Seattle': ['981'], 'Spokane': ['992'], 'Tacoma': ['984'], 'Vancouver': ['986'], 'Bellevue': ['980']},
    'CO': {'Denver': ['800', '802'], 'Aurora': ['800', '802'], 'Colorado Springs': ['809'], 'Fort Collins': ['805'], 'Lakewood': ['802']},
    'MA': {'Boston': ['021'], 'Worcester': ['016'], 'Springfield': ['011'], 'Lowell': ['018'], 'Cambridge': ['021']},
    'NV': {'Las Vegas': ['889', '891'], 'Henderson': ['890'], 'Reno': ['895'], 'North Las Vegas': ['890'], 'Sparks': ['894']},
    'TN': {'Nashville': ['372'], 'Memphis': ['375', '381'], 'Knoxville': ['379'], 'Chattanooga': ['374'], 'Clarksville': ['370']},
    'MD': {'Baltimore': ['212'], 'Columbia': ['210'], 'Germantown': ['208'], 'Silver Spring': ['209'], 'Waldorf': ['206']},
    'WI': {'Milwaukee': ['532'], 'Madison': ['537'], 'Green Bay': ['543'], 'Kenosha': ['531'], 'Racine': ['534']},
    'OR': {'Portland': ['970', '972'], 'Salem': ['973'], 'Eugene': ['974'], 'Gresham': ['970'], 'Hillsboro': ['971']},
    'OK': {'Oklahoma City': ['731'], 'Tulsa': ['741'], 'Norman': ['730'], 'Broken Arrow': ['740'], 'Lawton': ['735']},
    'KY': {'Louisville': ['402'], 'Lexington': ['405'], 'Bowling Green': ['421'], 'Owensboro': ['423'], 'Covington': ['410']},
    'NM': {'Albuquerque': ['871'], 'Las Cruces': ['880'], 'Rio Rancho': ['871'], 'Santa Fe': ['875'], 'Roswell': ['882']},
    'GA': {'Atlanta': ['303', '311'], 'Augusta': ['309'], 'Columbus': ['319'], 'Macon': ['312'], 'Savannah': ['314']},
    'VA': {'Virginia Beach': ['234'], 'Norfolk': ['235'], 'Chesapeake': ['233'], 'Richmond': ['232'], 'Newport News': ['236']},
    'MO': {'Kansas City': ['641'], 'St. Louis': ['631'], 'Springfield': ['658'], 'Independence': ['640'], 'Columbia': ['652']},
    'IN': {'Indianapolis': ['462'], 'Fort Wayne': ['468'], 'Evansville': ['477'], 'South Bend': ['466'], 'Carmel': ['460']},
    'MN': {'Minneapolis': ['554'], 'St. Paul': ['551'], 'Rochester': ['559'], 'Duluth': ['558'], 'Bloomington': ['554']},
    'KS': {'Wichita': ['672'], 'Overland Park': ['662'], 'Kansas City': ['661'], 'Olathe': ['660'], 'Topeka': ['666']},
    'LA': {'New Orleans': ['701'], 'Baton Rouge': ['708'], 'Shreveport': ['711'], 'Lafayette': ['705'], 'Lake Charles': ['706']},
    'NE': {'Omaha': ['681'], 'Lincoln': ['685'], 'Bellevue': ['680'], 'Grand Island': ['688'], 'Kearney': ['688']},
    'OK': {'Oklahoma City': ['731'], 'Tulsa': ['741'], 'Norman': ['730'], 'Broken Arrow': ['740'], 'Lawton': ['735']},
    'ID': {'Boise': ['837'], 'Meridian': ['836'], 'Nampa': ['836'], 'Idaho Falls': ['834'], 'Pocatello': ['832']},
    'MS': {'Jackson': ['392'], 'Gulfport': ['395'], 'Southaven': ['386'], 'Hattiesburg': ['394'], 'Biloxi': ['395']},
    'AR': {'Little Rock': ['722'], 'Fort Smith': ['729'], 'Fayetteville': ['727'], 'Springdale': ['727'], 'Jonesboro': ['724']},
    'UT': {'Salt Lake City': ['841'], 'West Valley City': ['841'], 'Provo': ['846'], 'West Jordan': ['840'], 'Orem': ['840']},
    'IA': {'Des Moines': ['503'], 'Cedar Rapids': ['524'], 'Davenport': ['528'], 'Sioux City': ['511'], 'Iowa City': ['522']},
    'HI': {'Honolulu': ['968']},
    'AK': {'Anchorage': ['995']},
    'SD': {'Sioux Falls': ['571']},
    'ND': {'Fargo': ['581']},
    'MT': {'Billings': ['591']},
    'WY': {'Cheyenne': ['820']},
    'WV': {'Charleston': ['253']},
    'DE': {'Wilmington': ['198']},
    'NH': {'Manchester': ['031']},
    'ME': {'Portland': ['041']},
    'RI': {'Providence': ['029']},
    'DC': {'Washington': ['200']},
}

def get_city_zip_prefixes(state, city):
    return CITY_ZIP_PREFIXES.get(state, {}).get(city, [])

def build_summary(step, registration_data):
    fields = [
        ('first_name', 'First Name'),
        ('middle_name', 'Middle Name'),
        ('last_name', 'Last Name'),
        ('phone_number', 'Phone'),
        ('email', 'Email'),
        ('gender', 'Gender'),
        ('date_of_birth', 'Date of Birth'),
        ('address_line_1', 'Street Address'),
        ('address_line_2', 'Apt/Suite'),
        ('city', 'City'),
        ('state', 'State'),
        ('postal_code', 'ZIP'),
        ('password', 'Password'),
        ('country', 'Country'),
        ('profile_id', 'Profile ID'),
    ]
    if step <= 1:
        return ""
    prev_idx = step - 2
    if 0 <= prev_idx < len(fields):
        key, label = fields[prev_idx]
        value = registration_data.get(key)
        if value:
            return f"✅ {label}: {value}\n"
    return ""

async def new_customer(update, context):
    query = getattr(update, 'callback_query', None)
    user = update.effective_user
    telegram_id = user.id
    
    # Initialize user data in context if not present
    if 'registration_data' not in context.user_data:
        context.user_data['registration_data'] = {}
    if 'step' not in context.user_data:
        context.user_data['step'] = 1

    step = context.user_data['step']
    registration_data = context.user_data['registration_data']

    gender_options = [
        [InlineKeyboardButton("Male", callback_data='gender_Male'), InlineKeyboardButton("Female", callback_data='gender_Female')],
        [InlineKeyboardButton("Other", callback_data='gender_Other'), InlineKeyboardButton("Prefer not to say", callback_data='gender_Prefer not to say')]
    ]

    # Create state buttons (3 per row)
    state_buttons = []
    state_list = list(US_STATES.items())
    for i in range(0, len(state_list), 3):
        row = []
        for j in range(3):
            if i + j < len(state_list):
                state_code, state_name = state_list[i + j]
                row.append(InlineKeyboardButton(state_name, callback_data=f'state_{state_code}'))
        state_buttons.append(row)

    # City buttons will be created in 3 rows in the city step logic

    if step <= len(steps):
        current_step = steps[step - 1]
        # Build summary of previous answers
        summary = build_summary(step, registration_data)
        message = summary + current_step["prompt"] if summary else current_step["prompt"]
        is_mandatory = current_step.get("mandatory", False)
        
        # Step 15: show Confirm and Edit buttons in a row
        if step == 15:
            keyboard = [[
                InlineKeyboardButton("✅ Confirm", callback_data='confirm_registration'),
                InlineKeyboardButton("✏️ Edit", callback_data='edit_registration')
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        elif step == 6:
            reply_markup = InlineKeyboardMarkup(gender_options + [[InlineKeyboardButton("❌ Cancel", callback_data='cancel')]])
        elif step == 10:
            # State selection
            reply_markup = InlineKeyboardMarkup(state_buttons + [[InlineKeyboardButton("❌ Cancel", callback_data='cancel')]])
        elif step == 11:
            # City selection: only show cities for selected state
            city_buttons = []
            selected_state = registration_data.get('selected_state') or registration_data.get('state')
            if selected_state and selected_state in STATE_CITIES:
                cities = STATE_CITIES[selected_state]
                cities_per_row = (len(cities) + 2) // 3  # Divide cities into 3 rows
                for i in range(0, len(cities), cities_per_row):
                    row = []
                    for j in range(cities_per_row):
                        if i + j < len(cities):
                            city_name = cities[i + j]
                            row.append(InlineKeyboardButton(city_name, callback_data=f'city_{city_name}'))
                    city_buttons.append(row)
                city_buttons.append([InlineKeyboardButton("📍 Other City (Type manually)", callback_data='city_other')])
                reply_markup = InlineKeyboardMarkup(city_buttons + [[InlineKeyboardButton("❌ Cancel", callback_data='cancel')]])
            else:
                keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='cancel')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
        elif step == 13:
            message = (
                "<b>Step 13 of 15: Password (Optional)</b> 🔐\n"
                "Would you like to add a password for email confirmation services?\n\n"
                "💡 <i>This is optional and only needed if you plan to order email confirmation services</i>\n"
                "🛠️ <i>You can create a simple temporary password if you want access to email services</i>"
            )
            keyboard = [
                [InlineKeyboardButton("🔐 Add Password", callback_data='add_password')],
                [InlineKeyboardButton("⏭️ Skip Password", callback_data='skip')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if query:
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            return
        else:
            keyboard = [
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel')]
            ]
            # Only show Skip for optional steps
            if not is_mandatory:
                keyboard.append([InlineKeyboardButton("⏭️ Skip", callback_data='skip')])
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.answer()
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    else:
        # Handle completion (e.g., save data and confirm)
        # Do nothing here; final summary is handled by show_final_summary_and_save
        return

# Handler for text input (to be added in bot.py)
async def handle_text(update, context):
    print("[DEBUG] handle_text called")
    print(f"[DEBUG] step: {context.user_data.get('step')}, awaiting_password: {context.user_data.get('awaiting_password')}")
    # Ensure registration_data is initialized
    if 'registration_data' not in context.user_data:
        context.user_data['registration_data'] = {}
    # Handle manual city input
    if context.user_data.get('awaiting_city_input'):
        city_name = update.message.text.strip()
        if len(city_name) < 2:
            await update.message.reply_text("❌ City name is too short. Please enter a valid city name.")
            return
        context.user_data['registration_data']['city'] = city_name
        context.user_data['awaiting_city_input'] = False
        context.user_data['step'] += 1
        await new_customer(update, context)
        return

    if context.user_data.get('editing'):
        field = update.message.text.strip().lower()
        field_to_step = {
            'first_name': 1,
            'middle_name': 2,
            'last_name': 3,
            'phone_number': 4,
            'email': 5,
            'gender': 6,
            'date_of_birth': 7,
            'address_line_1': 8,
            'address_line_2': 9,
            'city': 11,
            'state': 10,
            'postal_code': 12,
            'password': 13,
            'country': 14,
            'profile_id': 15
        }
        if field in field_to_step:
            context.user_data['step'] = field_to_step[field]
            context.user_data['editing'] = False
            await new_customer(update, context)
        else:
            await update.message.reply_text("❌ Invalid field name. Please type a valid field name to edit.")
        return
    
    if 'step' in context.user_data and context.user_data['step'] <= 15:
        step = context.user_data['step']
        registration_data = context.user_data['registration_data']
        text = update.message.text.strip()

        # Validation functions
        def is_valid_email(email):
            return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)
        def is_valid_phone(phone):
            # Accepts +1-555-123-4567 or 555-123-4567
            return re.match(r"^(\+1-)?\d{3}-\d{3}-\d{4}$", phone)
        def is_valid_zip(zipcode):
            return re.match(r"^\d{5}$", zipcode)
        def is_valid_state(state):
            return state in US_STATES.values()
        def is_valid_address(addr):
            return len(addr) > 4
        def is_valid_dob(dob):
            try:
                datetime.strptime(dob, "%m-%d-%Y")
                return True
            except ValueError:
                return False

        # Step-specific validation and saving
        if step == 1:
            registration_data['first_name'] = text
        elif step == 2:
            registration_data['middle_name'] = text
        elif step == 3:
            registration_data['last_name'] = text
        elif step == 4:
            if not is_valid_phone(text):
                await update.message.reply_text("❌ Invalid phone number. Please use USA format: +1-202-555-0173")
                return
            registration_data['phone_number'] = text
        elif step == 5:
            if not is_valid_email(text):
                await update.message.reply_text("❌ Invalid email format. Please enter a valid email address (e.g., john.doe@example.com).")
                return
            registration_data['email'] = text
        elif step == 6:
            registration_data['gender'] = text
        elif step == 7:
            if text and not is_valid_dob(text):
                await update.message.reply_text("❌ Invalid date format. Please use MM-DD-YYYY (Example: 03-15-1990)")
                return
            registration_data['date_of_birth'] = text
        elif step == 8:
            if not is_valid_address(text):
                await update.message.reply_text("❌ Address too short. Please enter a valid address (e.g., 123 Main Street).")
                return
            registration_data['address_line_1'] = text
        elif step == 9:
            registration_data['address_line_2'] = text
        elif step == 10:
            # State validation - check if it's a valid state name
            if not is_valid_state(text):
                await update.message.reply_text("❌ Please select a state from the provided options or enter a valid US state name.")
                return
            registration_data['state'] = text
        elif step == 11:
            # City validation - allow any city name
            if len(text) < 2:
                await update.message.reply_text("❌ City name is too short. Please enter a valid city name.")
                return
            registration_data['city'] = text
        elif step == 12:
            state = registration_data.get('state')
            city = registration_data.get('city')
            zip_prefixes = get_city_zip_prefixes(state, city)
            # Show ZIP prefix hint in the prompt if available
            if zip_prefixes:
                prefix_hint = f"ZIP should start with {' or '.join(zip_prefixes)}"
                message = build_summary(step, registration_data) + f"<b>Step 12 of 15: ZIP Code*</b> ✉️\nPlease enter the customer's <b>ZIP code*</b> (5 digits):\n💡 <i>{prefix_hint}</i>"
                if query:
                    await query.edit_message_text(
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                else:
                    await update.message.reply_text(
                        text=message,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
            # Validation
            if zip_prefixes and not any(text.startswith(prefix) for prefix in zip_prefixes):
                await update.message.reply_text(
                    f"❌ That ZIP doesn’t match {city}, {state}. ZIP should start with {' or '.join(zip_prefixes)}. Try again."
                )
                return
            if not is_valid_zip(text):
                await update.message.reply_text("❌ Invalid ZIP code. Please enter a 5-digit ZIP code (e.g., 90210).")
                return
            registration_data['postal_code'] = text
        elif step == 13 or (step == 14 and context.user_data.get('awaiting_password')):
            if context.user_data.get('awaiting_password'):
                password = text.strip()
                if len(password) < 6:
                    await update.message.reply_text("❌ Password must be at least 6 characters. Please try again:")
                    return
                registration_data['password'] = password
                context.user_data['awaiting_password'] = False
                print("[DEBUG] Password received, calling show_final_summary_and_save")
                await show_final_summary_and_save(update, context)
                return
            else:
                return
        elif step == 14:
            registration_data['country'] = 'USA'
        elif step == 15:
            # Profile ID will be auto-generated after confirmation
            pass

        context.user_data['step'] += 1
        await new_customer(update, context)

# Handler for button clicks (to be updated in bot.py)
async def button(update, context):
    query = update.callback_query
    await query.answer()
    option = query.data

    # Handle state selection
    if option.startswith('state_'):
        state_code = option[len('state_'):]
        state_name = US_STATES.get(state_code, state_code)
        context.user_data['registration_data']['state'] = state_name
        context.user_data['registration_data']['selected_state'] = state_code
        context.user_data['step'] += 1
        await new_customer(update, context)
        return

    # Handle city selection
    if option.startswith('city_'):
        city = option[len('city_'):]
        if city == 'other':
            # User wants to type city manually
            await query.edit_message_text(
                text="📝 <b>Enter City Name</b>\n\nPlease type your city name:",
                parse_mode='HTML'
            )
            context.user_data['awaiting_city_input'] = True
            return
        else:
            context.user_data['registration_data']['city'] = city
            context.user_data['step'] += 1
            await new_customer(update, context)
            return

    # Handle gender selection
    if option.startswith('gender_'):
        gender = option[len('gender_'):]
        context.user_data['registration_data']['gender'] = gender
        context.user_data['step'] += 1
        await new_customer(update, context)
        return

    if option == 'next':
        if 'step' in context.user_data and context.user_data['step'] <= 15:
            context.user_data['step'] += 1
            await new_customer(update, context)
    elif option == 'cancel':
        await query.edit_message_text(
            text="📝 <b>Registration Cancelled</b>\n\nThe registration process has been cancelled. Start again with /start.",
            parse_mode='HTML'
        )
        if 'registration_data' in context.user_data:
            del context.user_data['registration_data']
        if 'step' in context.user_data:
            del context.user_data['step']
        if 'awaiting_city_input' in context.user_data:
            del context.user_data['awaiting_city_input']
        if 'awaiting_password' in context.user_data:
            del context.user_data['awaiting_password']
    elif option == 'confirm_registration':
        # Save registration data to customer_profiles table
        user = update.effective_user
        telegram_id = user.id
        username = user.username if user.username else user.first_name
        full_name = user.full_name
        conn = sqlite3.connect('users.db', check_same_thread=False)
        c = conn.cursor()
        
        # Create customer_profiles table if not exists
        c.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            profile_number INTEGER,
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            email TEXT,
            phone_number TEXT,
            address_line_1 TEXT,
            address_line_2 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            date_of_birth TEXT,
            gender TEXT,
            identification_number TEXT,
            preferred_contact_method TEXT,
            password TEXT, -- Added password column
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Get the next profile number for this user
        c.execute("SELECT COUNT(*) FROM customer_profiles WHERE telegram_id = ?", (telegram_id,))
        profile_count = c.fetchone()[0]
        profile_number = profile_count + 1
        
        # Before saving the profile in the final step, ensure country and profile_id are set
        # Ensure country is always set
        registration_data['country'] = 'USA'
        # Generate a unique profile ID if not already set
        if not registration_data.get('profile_id'):
            registration_data['profile_id'] = str(uuid.uuid4())

        # Insert new customer profile
        c.execute("""
        INSERT INTO customer_profiles (
            telegram_id, profile_number, first_name, middle_name, last_name, email, phone_number,
            address_line_1, address_line_2, city, state, postal_code, country,
            date_of_birth, gender, identification_number, preferred_contact_method, password, profile_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            profile_number,
            registration_data.get('first_name', ''),
            registration_data.get('middle_name', ''),
            registration_data.get('last_name', ''),
            registration_data.get('email', ''),
            registration_data.get('phone_number', ''),
            registration_data.get('address_line_1', ''),
            registration_data.get('address_line_2', ''),
            registration_data.get('city', ''),
            registration_data.get('state', ''),
            registration_data.get('postal_code', ''),
            registration_data.get('country', ''),
            registration_data.get('date_of_birth', ''),
            registration_data.get('gender', ''),
            registration_data.get('identification_number', ''),
            registration_data.get('preferred_contact_method', ''),
            registration_data.get('password', ''), # Ensure password is saved
            registration_data.get('profile_id', '') # Ensure profile_id is saved
        ))
        conn.commit()
        conn.close()
        
        # Show success message with new buttons
        profile_id = registration_data.get('profile_id', '')
        password_set = registration_data.get('password', '')
        password_status = "Set (for email services)" if password_set else "Not set"
        summary = (
            "🎉 <b>Customer Registration Complete!</b>\n\n"
            "✅ <b>Customer Profile Created Successfully</b>\n\n"
            f"👤 <b>Name:</b> {registration_data.get('first_name', '')} {registration_data.get('middle_name', '')} {registration_data.get('last_name', '')}\n"
            f"📞 <b>Phone:</b> {registration_data.get('phone_number', '')}\n"
            f"📧 <b>Email:</b> {registration_data.get('email', '')}\n"
            f"🧑‍🦰 <b>Gender:</b> {registration_data.get('gender', '')}\n"
            f"🎂 <b>Date of Birth:</b> {registration_data.get('date_of_birth', '')}\n"
            f"🏠 <b>Address:</b> {registration_data.get('address_line_1', '')}\n"
            f"🏢 <b>Apt/Suite:</b> {registration_data.get('address_line_2', '')}\n"
            f"🏙️ <b>City:</b> {registration_data.get('city', '')}\n"
            f"🗺️ <b>State:</b> {registration_data.get('state', '')}\n"
            f"✉️ <b>ZIP:</b> {registration_data.get('postal_code', '')}\n"
            f"🌎 <b>Country:</b> {registration_data.get('country', '')}\n"
            f"🔐 <b>Password:</b> {password_status}\n"
            f"🆔 <b>Profile ID:</b> {str(profile_id)[:8]}...\n\n"
            "🛒 <b>Ready to shop!</b> You can now place orders for this customer."
        )
        keyboard = [
            [InlineKeyboardButton("👥 View All Customers", callback_data='customers')],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text=summary,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        context.user_data.pop('registration_data', None)
        context.user_data.pop('step', None)
        return
    elif option == 'edit_registration':
        await query.edit_message_text(
            text="📝 <b>Registration Edit</b>\n\nPlease enter the field name you want to edit:\n\nAvailable fields: first_name, middle_name, last_name, email, phone_number, address_line_1, address_line_2, city, state, postal_code, country, date_of_birth, gender, preferred_contact_method",
            parse_mode='HTML'
        )
        context.user_data['editing'] = True
    elif option == 'skip':
        # If skipping password (step 13), show summary immediately
        if 'step' in context.user_data and context.user_data['step'] == 13:
            await show_final_summary_and_save(update, context)
            return
        # For other optional fields, increment step as before
        if 'step' in context.user_data and context.user_data['step'] < len(steps):
            context.user_data['step'] += 1
            await new_customer(update, context)
        return
    elif option == 'add_password':
        context.user_data['step'] = 14
        context.user_data['awaiting_password'] = True
        message = (
            "<b>Step 14 of 15: Create Password</b> 🔐\n\n"
            "Please enter a password (minimum 6 characters):\n\n"
            "💡 <i>This password will be used for email confirmation services</i>\n"
            "🛠️ <b>Quick Option:</b> You can create a temporary password for now and update it later if needed."
        )
        keyboard = [[InlineKeyboardButton('❌ Cancel', callback_data='cancel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    else:
        handlers = {
            'buy': buy_tokens,
            '100': create_payment,
            '250': create_payment,
            '550': create_payment,
            '1000': create_payment,
            '1500': create_payment,
            'custom': create_payment,
            'back': back_to_menu,
            'new': new_customer,
            'customers': my_customers,
            'orders': my_orders,
            'marketplace': marketplace,
            'balance': balance,
            'subscribe': subscribe,
            'help': help
        }
        handler = handlers.get(option)
        if handler:
            await handler(update, context)
        else:
            await query.edit_message_text(text="Option not recognized!")

async def show_final_summary_and_save(update, context):
    print("[DEBUG] Inside show_final_summary_and_save")
    try:
        registration_data = context.user_data['registration_data']
        from uuid import uuid4
        registration_data['country'] = 'USA'
        if not registration_data.get('profile_id'):
            registration_data['profile_id'] = str(uuid4())
        user = update.effective_user
        telegram_id = user.id
        username = user.username if user.username else user.first_name
        full_name = user.full_name
        conn = sqlite3.connect('users.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            profile_number INTEGER,
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            email TEXT,
            phone_number TEXT,
            address_line_1 TEXT,
            address_line_2 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            date_of_birth TEXT,
            gender TEXT,
            identification_number TEXT,
            preferred_contact_method TEXT,
            password TEXT,
            profile_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        c.execute("SELECT COUNT(*) FROM customer_profiles WHERE telegram_id = ?", (telegram_id,))
        profile_count = c.fetchone()[0]
        profile_number = profile_count + 1
        c.execute("""
        INSERT INTO customer_profiles (
            telegram_id, profile_number, first_name, middle_name, last_name, email, phone_number,
            address_line_1, address_line_2, city, state, postal_code, country,
            date_of_birth, gender, identification_number, preferred_contact_method, password, profile_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            profile_number,
            registration_data.get('first_name', ''),
            registration_data.get('middle_name', ''),
            registration_data.get('last_name', ''),
            registration_data.get('email', ''),
            registration_data.get('phone_number', ''),
            registration_data.get('address_line_1', ''),
            registration_data.get('address_line_2', ''),
            registration_data.get('city', ''),
            registration_data.get('state', ''),
            registration_data.get('postal_code', ''),
            registration_data.get('country', ''),
            registration_data.get('date_of_birth', ''),
            registration_data.get('gender', ''),
            registration_data.get('identification_number', ''),
            registration_data.get('preferred_contact_method', ''),
            registration_data.get('password', ''),
            registration_data.get('profile_id', '')
        ))
        conn.commit()
        conn.close()
        profile_id = registration_data.get('profile_id', '')
        password_set = registration_data.get('password', '')
        password_status = "Set (for email services)" if password_set else "Not set"
        summary = (
            "🎉 <b>Customer Registration Complete!</b>\n\n"
            "✅ <b>Customer Profile Created Successfully</b>\n\n"
            f"👤 <b>Name:</b> {registration_data.get('first_name', '')} {registration_data.get('middle_name', '')} {registration_data.get('last_name', '')}\n"
            f"📞 <b>Phone:</b> {registration_data.get('phone_number', '')}\n"
            f"📧 <b>Email:</b> {registration_data.get('email', '')}\n"
            f"🧑‍🦰 <b>Gender:</b> {registration_data.get('gender', '')}\n"
            f"🎂 <b>Date of Birth:</b> {registration_data.get('date_of_birth', '')}\n"
            f"🏠 <b>Address:</b> {registration_data.get('address_line_1', '')}\n"
            f"🏢 <b>Apt/Suite:</b> {registration_data.get('address_line_2', '')}\n"
            f"🏙️ <b>City:</b> {registration_data.get('city', '')}\n"
            f"🗺️ <b>State:</b> {registration_data.get('state', '')}\n"
            f"✉️ <b>ZIP:</b> {registration_data.get('postal_code', '')}\n"
            f"🌎 <b>Country:</b> {registration_data.get('country', '')}\n"
            f"🔐 <b>Password:</b> {password_status}\n"
            f"🆔 <b>Profile ID:</b> {str(profile_id)[:8]}...\n\n"
            "🛒 <b>Ready to shop!</b> You can now place orders for this customer."
        )
        keyboard = [
            [InlineKeyboardButton("👥 View All Customers", callback_data='customers')],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        print("[DEBUG] Preparing to send summary message...")
        if hasattr(update, "message") and update.message:
            await update.message.reply_text(
                text=summary,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        elif hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.edit_message_text(
                text=summary,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            # Fallback: send message directly to chat
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=summary,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        print("[DEBUG] Summary message sent (or attempted)")
        context.user_data.pop('registration_data', None)
        context.user_data.pop('step', None)
    except Exception as e:
        print(f"[DEBUG] Error in show_final_summary_and_save: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='❌ Something went wrong. Please try again.'
        )