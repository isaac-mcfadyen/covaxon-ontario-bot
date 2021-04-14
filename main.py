# General.
import sys
import time
# For web scraper.
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
# For pushover notifications.
from notifiers.providers.pushover import Pushover
# For booking interrupt.
from select import select
# For input arguments.
import argparse

# Try to import packages for system notifications.
# This will depend on platform. For example, notify is not
# available on Mac (Darwin) so we use pync instead.
try:
    notification_platform = "other"
    from notify import notification
except RuntimeError:
    import pync
    notification_platform = "darwin"

# Load ignored locations from file.
with open("ignoreList.txt", "r") as file:\
    LOCATION_IGNORE = file.readlines()

# Parse input arguments.
parser = argparse.ArgumentParser()
parser.add_argument('--headless', required=False, help='Optional. Run in headless mode (no window).',
                    action='store_false')
parser.add_argument('--card-number', required=True, help='Your Ontario health card number.')
parser.add_argument('--invitation-code', required=True,
                    help='Your Ontario Covaxon invitation code number.')
parser.add_argument('--event-code', required=True,
                    help='Your Ontario Covaxon event ID number')
parser.add_argument('--location', required=True,
                    help='The nearest city to your location. Please verify that it is in an accepted format. Example: Ottawa, ON, Canada')
parser.add_argument('--pushover-user', required=False,
                    help='Optional. Your Pushover user token, if you want to use Pushover notifications.')
parser.add_argument('--pushover-token', required=False,
                    help='Optional. Your Pushover application token, if you want to use Pushover notifications.')
args = parser.parse_args()

# Generate and set Chrome driver options based on user's input.
driver_options = Options()
if args.headless:
    driver_options.add_argument("--headless")

# Create the webdriver.
driver = webdriver.Chrome(options=driver_options)

# Declare web driver wait defaults for later user.
wait = WebDriverWait(driver, 20)
waitShort = WebDriverWait(driver, 1.4)

# Create the pushover provider if the user wants to use it.
if args.pushover_token or args.pushover_user:
    pushover = Pushover()

# Load the Covaxon booking webpage for the first time.
driver.get("https://vaccine.covaxonbooking.ca/screening")

# Loop over the following.
while True:
    # Wait until the landing page button is clickable, then click it.
    x = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/main/div[1]/div/div[2]/div[3]/button'))).click()

    # Click yes to the consent button.
    wait.until(
        EC.element_to_be_clickable((By.ID, 'q-screening-in-order-to-book-an-appointment-you-wil-Yes'))).click()

    # Enter the provided health card number, invitation code and event code.
    x = wait.until(EC.element_to_be_clickable((By.ID, "q-patient-healthcare-id")))
    x.clear()
    x.send_keys(args.card_number)
    x = wait.until(EC.element_to_be_clickable((By.ID, "q-screening-secret-code")))
    x.clear()
    x.send_keys(args.invitation_code)
    x = wait.until(EC.element_to_be_clickable((By.ID, "q-screening-event-code")))
    x.clear()
    x.send_keys(args.event_code)

    # Click submit.
    wait.until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/main/div/form/div/button[1]'))).click()

    # Enter the user's city.
    wait.until(EC.visibility_of_element_located((By.ID, "location-search-input"))).send_keys(
        args.location)

    # Click submit.
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/main/div/div[5]/button[1]'))).send_keys(
        locationValue)

    # Wait until any location button is clickable.
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='location-select-location-continue']")))

    # Grab all of the location buttons.
    buttons = driver.find_elements(By.XPATH, "//button[@data-testid='location-select-location-continue']")

    # Loop through the location buttons.
    buttonCounter = 0
    for x in buttons:
        # Wait until the page reloads.
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='location-select-location-continue']")))

        # Get a new, refreshed version of the buttons.
        # We must do this in the loop because previous button arrays will be marked as 'stale'
        # and will throw an error.
        buttonsNew = driver.find_elements(By.XPATH, "//button[@data-testid='location-select-location-continue']")

        # Get the button we want to target and click on it.
        # This is wrapped in a try-catch because it occasionally throws errors.
        try:
            i = buttonsNew[buttonCounter]
            i.click()
        except:
            print("Error. List index out of range. Skipping...")
            continue

        # Check if we have a timeslot.
        try:
            # Check if there is a timeslot button available to click.
            # If there is not, this will throw a timeout exception, and the
            # except block will be run.
            waitShort.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='appointment-select-timeslot']")))

            # If there is a timeslot available, get the location
            # and the next available date.
            location = driver.find_element(By.CLASS_NAME, "tw-pb-6").text
            date = driver.find_element(By.CLASS_NAME, "tw-mb-5").text

            # Strip 'Change' from the location and date.
            location = location.replace(' Change\n', '')
            date = date.replace(' Change\n', '')

            # Check if we want to ignore this location.
            if location in LOCATION_IGNORE:
                pass
            else:
                # Print message to user.
                print("FOUND!")
                print("Location: {}".format(location))
                print("Date: {}".format(date))

                # Generate notification message.
                notification_message = "Found vaccine booking at {} {}".format(location, date)

                # Send pushover notification, if pushover token is provided.
                if args.pushover_token or args.pushover_user:
                    pushover.notify(user=args.pushover_user, message=notification_message, token=args.pushover_token)

                # Send system notification, depending on platform.
                if notification_platform == 'darwin':
                    pync.notify(notification_message)
                elif notification_platform == 'other':
                    notification(notification_message, title='Covaxon Ontario')
                else:
                    pass

                # Allow user to push enter to book.
                print("If you would like to book, push Enter/Return within 15 seconds.")
                timeout = 15
                rlist, wlist, xlist = select([sys.stdin], [], [], timeout)

                if rlist:
                    # Print message.
                    print("Allowing user to book!")

                    # Sleep to allow user to book.
                    time.sleep(120000)
                else:
                    # Print message.
                    print("User not booking. Continuing.")

        except TimeoutException:
            pass

        # Increment the button counter.
        buttonCounter += 1

        # Try to click the back button.
        # Sometimes it is obscured by a div, so we try until it is clicked.
        back = False
        while not back:
            try:
                x = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='back-button']"))).click()
                back = True
            except ElementClickInterceptedException:
                pass

    # Sleep for 30 seconds to prevent rate-limiting.
    time.sleep(30)

# Close the driver.
driver.close()
