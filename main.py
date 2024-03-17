import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Telegram Bot Token
TOKEN = 'ur bot token'

# Google Sheets Credentials
SERVICE_ACCOUNT_FILE = r'copy path json file'  # Replace with the path to your JSON credentials file! My path is D:/tugas_akhir/credentials.json
SPREADSHEET_ID = 'id from url sheet'

# Create bot instance
bot = telebot.TeleBot(TOKEN)

# Connect to Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('D:/tugas_akhir/credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Function to upload data to Google Sheets
def upload_to_sheet(user_id):
    # Check if all required data is present
    if all(key in user_data[user_id] for key in ['date', 'department', 'item', 'quantity', 'price_per_item', 'total_price']):
        # Connect to Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        
        # Prepare the data row
        data_row = [
            user_data[user_id].get('date', ''),
            user_data[user_id].get('department', ''),
            user_data[user_id].get('item', ''),
            user_data[user_id].get('quantity', ''),
            user_data[user_id].get('price_per_item', ''),
            user_data[user_id].get('total_price', '')
        ]
        
        # Upload the data row to the next available row in the sheet
        sheet.append_row(data_row)
    else:
        print("Not all data is available for user:", user_id)


# Define states for conversation
states = {}

# Dictionary to store user data temporarily
user_data = {}

def start(message):
    user_id = message.from_user.id  # Retrieve the unique user_id from the incoming message
    if user_id not in user_data:  # Check if this user_id already has data stored
        user_data[user_id] = {}  # Initialize an empty dictionary for this user_id

# Helper functions for managing conversation states
def get_state(user_id):
    return states.get(user_id, None)

def set_state(user_id, state):
    states[user_id] = state

def initialize_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {}

# Handle '/start' command
@bot.message_handler(commands=['start'])
def start(message):
    initialize_user_data(message.chat.id)
    bot.reply_to(message, "Welcome to the Purchasing Report Bot! Data you need to inpus is Department, Item, Quantity, Price per Item, total Price and Photo. First, please enter the date of your purchase in the format YYYY-MM-DD.")
    set_state(message.chat.id, 'date')
    # Register the next function to handle the date input
    bot.register_next_step_handler(message, save_date)

# Handle 'date'
def is_valid_date(date_str):
    try:
        # Assuming the date format is 'YYYY-MM-DD'
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
def save_date(message):
    user_id = message.chat.id
    date = message.text
    # Check if the date format is correct before saving
    # You can add your date validation logic here
    if is_valid_date(date):
        user_data[user_id]['date'] = date
        set_state(user_id, 'department')
        bot.reply_to(message, f"Date '{date}' saved successfully! Please enter your department.")
        upload_to_sheet(user_id)  # Save the date to Google Sheets
    else:
        bot.reply_to(message, "Invalid date format. Please enter the date in the format YYYY-MM-DD.")
        # Re-register the save_date function to handle the corrected input
        bot.register_next_step_handler(message, save_date)


# Function to save department
def save_department(message):
    user_id = message.chat.id
    department = message.text

    # Initialize user_data for the user if it doesn't exist
    if user_id not in user_data:
        initialize_user_data(user_id)

    # Save the department information
    user_data[user_id]['department'] = department

    # Update the state to the next expected input
    set_state(user_id, 'item')

    # Provide feedback to the user
    bot.reply_to(message, f"Department '{department}' saved successfully!")

    # Attempt to upload the data to Google Sheets
    try:
        upload_to_sheet(user_id)
    except Exception as e:
        print(f"An error occurred while uploading to Google Sheets: {e}")

    # Prompt the user for the next input
    bot.send_message(user_id, "Please enter the name of the item you want to purchase:")

# Function to save item input
def get_item(message):
    user_id = message.chat.id
    item = message.text
    user_data[user_id]['item'] = item
    set_state(user_id, 'quantity')
    bot.reply_to(message, f"Item '{item}' saved successfully!")
    upload_to_sheet(user_id)  # Save the item to Google Sheets
    bot.send_message(user_id, "Please enter the quantity of the item:")

# Function to handle quantity input
def get_quantity(message):
    user_id = message.chat.id
    quantity = message.text
    user_data[user_id]['quantity'] = quantity
    set_state(user_id, 'price_per_item')
    bot.reply_to(message, f"Quantity '{quantity}' saved successfully!")
    upload_to_sheet(user_id)  # Save the quantity to Google Sheets
    bot.send_message(user_id, "Please enter the price per item:")

# Function to handle price per item input
def get_price_per_item(message):
    user_id = message.chat.id
    price_per_item = message.text
    user_data[user_id]['price_per_item'] = price_per_item
    set_state(user_id, 'total_price')
    bot.reply_to(message, f"Price per item '{price_per_item}' saved successfully!")
    upload_to_sheet(user_id)  # Save the price per item to Google Sheets
    bot.send_message(user_id, "Please enter the total price:")

# Function to handle total price input
def get_total_price(message):
    user_id = message.chat.id
    total_price = message.text
    user_data[user_id]['total_price'] = total_price
    bot.reply_to(message, "Total price saved successfully!")
    upload_to_sheet(user_id)  # Save the total price to Google Sheets
    bot.send_message(user_id, "Please share a picture of the item:")

# Function to handle photo message
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    bot.reply_to(message, "Thank you for sharing the picture. Your purchase report will be generated and sent to your email.")
    upload_to_sheet(user_id)  # Save the picture to Google Sheets

# Function to send email
def send_email(user_id, photo_path):
    # Email credentials and recipient
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    recipient_email = "recipient@example.com"

     # Access user data using user_id
    department = user_data.get(user_id, {}).get('department', 'Not provided')
    item = user_data.get(user_id, {}).get('item', 'Not provided')

    
# Define a handler for messages that expects a continuous conversation
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    state = get_state(user_id)
    
    # Call the appropriate function based on the current state
    if state == 'department':
        save_department(message)
    elif state == 'item':
        get_item(message)
    elif state == 'quantity':
        get_quantity(message)
    elif state == 'price_per_item':
        get_price_per_item(message)
    elif state == 'total_price':
        get_total_price(message)
    else:
        start(message)  # Restart the conversation if the state is not recognized


# Polling to keep the bot running
bot.polling()
