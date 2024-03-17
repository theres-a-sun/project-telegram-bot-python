# Create the email headers and body
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Purchasing Report"

    body = f"""
    Department: {user_data['department']}
    Item: {user_data['item']}
    Quantity: {user_data['quantity']}
    Price per Item: {user_data['price_per_item']}
    Total Price: {user_data['total_price']}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Attach the photo
    with open(photo_path, 'rb') as photo_file:
        msg.attach(MIMEImage(photo_file.read()))

    # Set up the SMTP server and send the email
    server = smtplib.SMTP('smtp.example.com', 587)  # Use the correct SMTP server and port for your email provider
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

# Call the function with the user_data dictionary and the path to the photo
send_email(user_data, 'path_to_photo.jpg')
