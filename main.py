import random
import requests
import asyncio
import aiohttp
import telebot
from datetime import datetime, timedelta

# Initialize bot with token
token = input('Enter your bot token: ')
bot = telebot.TeleBot(token)

# Dictionary to track last request time for each user
user_last_request = {}
request_limit_time = 5  # time limit in seconds for requests

# Helper function to make asynchronous requests
async def safe_request(session, url):
    try:
        async with session.get(url) as response:
            return response
    except Exception:
        return None

# Rate limiting check
def is_request_allowed(user_id):
    now = datetime.now()
    last_request_time = user_last_request.get(user_id)

    if last_request_time is None or (now - last_request_time) > timedelta(seconds=request_limit_time):
        user_last_request[user_id] = now
        return True
    return False

async def check_website_properties(session, url):
    results = {}
    
    # Check if website has captcha
    results['captcha'] = await safe_request(session, url)

    # Check payment gateways
    results['payment'] = await safe_request(session, url)

    # Check for cloud services
    results['cloud'] = await safe_request(session, url)

    # Check GraphQL
    results['graphql'] = await safe_request(session, url)

    # Check auth path
    auth_path = url.rstrip('/') + '/my-account/add-payment-method/'
    results['auth_path'] = await safe_request(session, auth_path)

    # Check platform
    results['platform'] = await safe_request(session, url)

    # Check error logs
    results['error_logs'] = await safe_request(session, url)

    # Get status code
    results['status_code'] = await safe_request(session, url)

    return results

@bot.message_handler(commands=['url'])
def check_url(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Please provide a valid URL after the /url command.')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, 'Please wait a few seconds before making another request.')
        return

    url = message.text.split()[1]

    async def handle_request():
        async with aiohttp.ClientSession() as session:
            results = await check_website_properties(session, url)

            # Process results to format response
            captcha = 'Captcha detected' if results['captcha'] else 'No Captcha'
            cloud = 'Cloudflare detected' if results['cloud'] else 'No Cloudflare'
            payment = 'Payment gateways found' if results['payment'] else 'No payment gateways'
            auth_path = 'Auth ✔️' if results['auth_path'] and results['auth_path'].status == 200 else 'None ❌'
            platform = 'Platform detected' if results['platform'] else 'None'
            error_logs = 'Error logs found' if results['error_logs'] and 'error' in await results['error_logs'].text() else 'None'
            status_code = results['status_code'].status if results['status_code'] else 'Error'

            response_message = (
                "🔍 Gateways Fetched Successfully ✅\n"
                "━━━━━━━━━━━━━━\n"
                f"🔹 URL: <code>{url}</code>\n"
                f"🔹 Payment Gateways: {payment}\n"
                f"🔹 Captcha: {captcha}\n"
                f"🔹 Cloudflare: {cloud}\n"
                f"🔹 GraphQL: {'Exists' if results['graphql'] else 'Not Found'}\n"
                f"🔹 Auth Path: {auth_path}\n"
                f"🔹 Platform: {platform}\n"
                f"🔹 Error Logs: {error_logs}\n"
                f"🔹 Status: {status_code}\n"
                "\nBot by: <a href='tg://user?id=1984468312'> 𝚉𝚘𝚍 𝙼𝚊𝚍𝚊𝚛𝚊</a>"
            )

            bot.reply_to(message, response_message, parse_mode='HTML')

    # Run the asynchronous request handling
    asyncio.run(handle_request())

# Command to check sk_live key
@bot.message_handler(commands=['sk'])
def check_sk_key(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Please provide a valid sk_live key after the /sk command.')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, 'Please wait a few seconds before making another request.')
        return

    key = message.text.split()[1]
    balance_response = requests.get('https://api.stripe.com/v1/balance', auth=(key, ''))
    account_response = requests.get('https://api.stripe.com/v1/account', auth=(key, ''))

    if balance_response.status_code == 200 and account_response.status_code == 200:
        account_info = account_response.json()
        balance_info = balance_response.json()

        # Collect account information
        publishable_key = account_info.get('keys', {}).get('publishable', 'Not Available')
        account_id = account_info.get('id', 'Not Available')
        charges_enabled = account_info.get('charges_enabled', 'Not Available')
        live_mode = account_info.get('livemode', 'Not Available')
        country = account_info.get('country', 'Not Available')
        currency = balance_info.get('currency', 'Not Available')
        available_balance = balance_info.get('available', [{'amount': '0'}])[0]['amount']
        pending_balance = balance_info.get('pending', [{'amount': '0'}])[0]['amount']
        payments_enabled = account_info.get('payouts_enabled', 'Not Available')
        name = account_info.get('business_name', 'Not Available')
        phone = account_info.get('support_phone', 'Not Available')
        email = account_info.get('email', 'Not Available')
        url = account_info.get('url', 'Not Available')

        response = (
    f'''[ϟ] 𝗦𝗸 𝗞𝗘𝗬\n<code>{key}</code>\n\n'''
    f'''[ϟ] 𝗣𝗸 𝗞𝗘𝗬\n<code>{publishable_key}</code>\n'''
    "－－－－－－－－－－－－－－－\n"
    f'''[✮] 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐃 ⬇️ [✮]\n{account_id}\n'''
    "－－－－－－－－－－－－－－－\n"
    "[✮] 𝐊𝐞𝐲 𝐈𝐧𝐟𝐨 ⬇️ [✮]\n"
    f"[ϟ] 𝗖𝗵𝗮𝗿𝗴𝗲𝘀 𝗘𝗻𝗮𝗯𝗹𝗲𝗱 : {charges_enabled}\n"
    f"[ϟ] 𝗟𝗶𝘃𝗲 𝗠𝗼𝗱𝗲 : {live_mode}\n"
    f"[ϟ] 𝗣𝗮𝘆𝗺𝗲𝗻𝘁𝘀 : {payments_enabled}\n"
    f"[ϟ] 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {available_balance}\n"
    f"[ϟ] 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {available_balance}\n"
    f"[ϟ] 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {pending_balance}\n"
    f"[ϟ] 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 : {currency}\n"
    f"[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country}\n"
    "－－－－－－－－－－－－－－－\n"
    "[✮] 𝐀𝐜𝐜𝐨𝐮𝐧𝐭 𝐈𝐧𝐟𝐨 ⬇️ [✮]\n"
    f"[ϟ] 𝗡𝗮𝗺𝗲 : {name}\n"
    f"[ϟ] 𝗣𝗵𝗼𝗻𝗲 : {phone}\n"
    f"[ϟ] 𝗘𝗺𝗮𝗶𝗹 : {email}\n"
    f'''[ϟ] 𝗨𝗿𝗹 : <code>{url}</code>\n'''
)

        bot.reply_to(message, response, parse_mode='HTML')
    else:
        bot.reply_to(message, f'Invalid or expired API key❌.\nKey: <code>{key}</code>', parse_mode='HTML')

# Function to check if the user can make another request
# Mapping of country codes to flag emojis
country_flags = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮",
    "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", "AR": "🇦🇷", "AS": "🇦🇸",
    "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿",
    "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫",
    "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱",
    "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BQ": "🇧🇶", "BR": "🇧🇷",
    "BS": "🇧🇸", "BT": "🇧🇹", "BV": "🇧🇻", "BW": "🇧🇼", "BY": "🇧🇾",
    "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫",
    "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱",
    "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺",
    "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇭🇨", "CY": "🇨🇾", "CZ": "🇨🇿",
    "DE": "🇩🇪", "DJ": "🇩🇯", "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴",
    "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭",
    "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯",
    "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧",
    "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭",
    "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵",
    "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼",
    "GY": "🇬🇾", "HK": "🇭🇰", "HM": "🇭🇲", "HN": "🇭🇳", "HR": "🇭🇷",
    "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱",
    "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷",
    "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴",
    "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", "KH": "🇰🇭", "KI": "🇰🇮",
    "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼",
    "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨",
    "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹",
    "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨",
    "MD": "🇲🇩", "ME": "🇲🇪", "MF": "🇲🇫", "MG": "🇲🇬", "MH": "🇲🇭",
    "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴",
    "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹",
    "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾",
    "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫",
    "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵",
    "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦",
    "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰",
    "PL": "🇵🇱", "PM": "🇵🇲", "PN": "🇵🇳", "PR": "🇵🇷", "PT": "🇵🇹",
    "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴",
    "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧",
    "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭",
    "SI": "🇸🇮", "SJ": "🇸🇯", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲",
    "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹",
    "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨",
    "TD": "🇹🇩", "TF": "🇹🇫", "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰",
    "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷",
    "TT": "🇹🇹", "TV": "🇹🇻", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬",
    "UM": "🇺🇲", "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦",
    "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳",
    "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹",
    "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼"
}

def is_request_allowed(user_id):
    return True

def get_card_info(bin_number):
    response = requests.get(f'https://lookup.binlist.net/{bin_number}')
    if response.status_code == 200:
        return response.json()
    return None

def generate_credit_card_numbers(bin_number):
    card_numbers = []
    for _ in range(10):  # Generate 10 card numbers
        card_number = f"{bin_number}{''.join(random.choices('0123456789', k=16 - len(bin_number)))}"
        month = random.randint(1, 12)
        year = random.randint(24, 30)  # Valid until 2024-2030
        cvv = ''.join(random.choices('0123456789', k=3))
        card_numbers.append(f"{card_number}|{month:02}|20{year}|{cvv}")
    return card_numbers

@bot.message_handler(commands=['gen'])
def generate_cards(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, 'Please provide a BIN after the /gen command.')
        return

    user_id = message.from_user.id
    if not is_request_allowed(user_id):
        bot.reply_to(message, 'Please wait a few seconds before making another request.')
        return

    bin_number = message.text.split()[1]
    card_numbers = generate_credit_card_numbers(bin_number)
    bin_info = get_card_info(bin_number)

    card_info = (
        f'𝗕𝗜𝗡 ⇾ {bin_number}\n'
        f'𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n'
        f'<code>\n' + '\n'.join(card_numbers) + '\n</code>\n'
    )

    # Append BIN info if available
    if bin_info:
        scheme = bin_info.get("scheme", "Unknown").upper()
        card_type = bin_info.get("type", "Unknown").upper()
        brand = bin_info.get("brand", "Unknown").upper()
        issuer = bin_info.get("bank", {}).get("name", "Unknown").upper()
        country = bin_info.get("country", {}).get("name", "Unknown").upper()
        country_code = bin_info.get("country", {}).get("alpha2", "Unknown").upper()
        flag = country_flags.get(country_code, "")

        card_info += (
            "𝗜𝗻𝗳𝗼: \n"
            f'{scheme} - {card_type} - {brand}\n'
            f'𝐈𝐬𝐬𝐮𝐞𝐫: {issuer}\n'
            f'𝗖𝗼𝘂𝗻𝘁𝗿𝗬: {country} {flag}\n'
        )
    else:
        card_info += "𝗜𝗻𝗳𝗼: No additional BIN info available.\n"

    bot.reply_to(message, card_info, parse_mode='HTML')

# Welcome message and commands
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        "Welcome to the Bot! Here are the commands you can use:\n"
        "/url <URL> - Check details about the specified URL\n"
        "/sk <sk_live key> - Check the sk_live key information\n"
        "/gen <BIN> - Generate credit card numbers based on the BIN\n"
    )
    bot.reply_to(message, welcome_text)

# Start the bot
bot.polling(none_stop=True)