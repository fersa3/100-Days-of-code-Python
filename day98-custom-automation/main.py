from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from ace_page_functions import ACEPageFunctions
import time

# Set up info for uploading weekly hours.
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
default_hours = ['8', '8', '8', '8', '8']
week_hours = dict(zip(days, default_hours))  # Initialize with 8 hours per day.
default_comment = "RU DCM releasing activities. Meetings with supplier and Stellantis team."

enter_hours = input("Were there any non-working days this week? y/N ").strip().lower()

if enter_hours == "y":
    for status, label in [("H", "Holiday"), ("V", "Vacation")]:
        days_with_0_hours = input(
            f"Which days were {label}s? If more than one, separate by commas (e.g., 1,2 for Mon & Tue), or press Enter to skip:\n"
            " 1 - Monday\n 2 - Tuesday\n 3 - Wednesday\n 4 - Thursday\n 5 - Friday\n"
            ).strip()
        if days_with_0_hours:
            indices = [int(i) - 1 for i in days_with_0_hours.split(",") if i.isdigit() and 1 <= int(i) <= 5]
            for i in indices:
                week_hours[days[i]] = f"0{status}"

# Message for comment showing non-working days and motive
days_with_0_hours_message = ",".join(f"{day} ({'Vacaciones' if 'V' in hours else 'Holiday'})"
                                     for day, hours in week_hours.items() if hours in ["0V", "0H"])

comment_with_days_off = f"\nNon-working days: {days_with_0_hours_message}" if days_with_0_hours_message else ""

# Set up Firefox options
options = Options()

# Create a new Firefox browser instance
print("Starting to upload your hours...")
driver = webdriver.Firefox(options=options)

# Open ACE Project in Firefox
driver.get("https://segulamexico.aceproject.com/")

page = ACEPageFunctions(driver)

# Log in
page.login_to_ace()

# Go to timesheet & enter hours
page.switch_to_frame("leftFrame")
page.click_time_menu()

# Sleep in case there's need to change week
time.sleep(10)

# Switch back to main document and add time item
driver.switch_to.default_content()
page.switch_to_frame("mainFrame")
page.go_to_add_time_item()

# Wait for the dialog to appear
time.sleep(2)

# Select project and task
page.select_project_and_task(project_value="77", task_value="194")

time.sleep(1)

# Enter hours
print("Entering hours for the week...")
page.enter_hours_for_week(week_hours)

time.sleep(1)

# Add comment
print("Adding comment...")
comment_text = default_comment
if days_with_0_hours_message:
    comment_text += comment_with_days_off
page.add_comment(comment_text)

# Click 'Save' button
page.save_time_entry()

time.sleep(2)

# If vacations or holiday, add them in a second time item
if days_with_0_hours_message:
    # Switch back to main document
    driver.switch_to.default_content()
    page.switch_to_frame("mainFrame")
    page.go_to_add_time_item()

    time.sleep(2)

    # Select project and task for time off
    page.select_project_and_task(project_value="77", task_value="453")

    time.sleep(1)

    # Enter hours
    print("Entering hours for non-working days of the week...")
    page.enter_hours_for_vac_hol_week(week_hours)

    time.sleep(1)

    # Add comment
    print("Adding comment...")
    page.add_comment(comment_with_days_off)

    # Click 'Save' button
    page.save_time_entry()

    time.sleep(2)

# Select the title checkbox and submit for approval
page.check_select_all_checkbox()
page.open_and_select_approver()
# Uncomment the next line when ready to actually send the approval request
page.click_send_approval_request()

time.sleep(2)

# Keep the browser open
input("Press Enter to close the browser...")

# Close the browser
driver.quit()
