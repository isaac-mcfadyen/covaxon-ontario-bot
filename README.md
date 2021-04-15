# Covaxon Ontario Bot
A web bot to assist in Covaxon Ontario's COVID-19 vaccine booking.  
  
There currently seem to be challenges with the Ontario Covaxon booking system; it provides different booking slots and locations every time you re-enter your details, sometimes showing slots that were not there a minute before or making slots vanish after a few seconds. This poses a particular problem if you want/need a spot at your local vaccine distribution center.

This program helps solve this by constantly monitoring Covaxon Ontario's website (https://vaccine.covaxonbooking.ca), and alerting you via push notification to your smartphone (using Pushover, available with a 30 day free trial at https://pushover.net) when a spot opens up in your area. Push notifications are also generated on the device you are running on.

## Usage

There are two ways to run this program. Pre-built packages are a WIP; in the meantime, you can run with Python 3 directly.

To run with Python, you must first download and place a valid webdriver in your PATH, for use by Selenium. You can find instructions [here](https://selenium-python.readthedocs.io/installation.html#drivers). Make sure the version matches your web-browser's version.

Next, install the requirements in the requirements.txt file with:
```
pip install -r requirements.txt
```
or by using pip manually.

Finally, run the main Python file with:
```
python3 main.py [arguments]
```

Arguments can be listed with the --help flag. The following arguments are available:
```
--card - Required. Your Ontario health card number.
--invitation-code - Required. Your Covaxon Invitation Code number.
--event-code - Required. Your Covaxon Event ID number.
--location - Required. The nearest city to your location. Please verify that it is in an accepted format. Example: "Ottawa, ON, Canada" or "Toronto, ON, Canada"
--pushover-user - Optional. Provide your Pushover (https://pushover.net) user token here to allow Pushover notifications to your smartphone. If not provided, the default is notifications on the system the program is run on.
--pushover-tolken - Optional. Provide your Pushover (https://pushover.net) application token here to allow Pushover notifications to your smartphone. If not provided, the default is notifications on the system the program is run on.
--headless - Optional. Provide this flag to run in headless mode (no window).
```

Any locations you wish to ignore can be placed in ignoreList.txt (case-sensitive and must exactly match; it is recommended to Copy & Paste the location you wish to ignore from your results directly into the file).
## Contributing
All pull requests are welcome! Guidelines are provided [here](CONTRIBUTING).

## Donations

If you like this program, consider buying me a cup of coffee.  
  
[![Donate](https://github.com/Ximi1970/Donate/blob/master/paypal_btn_donateCC_LG_1.gif)](https://paypal.me/mcfadyeni)
