from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

USER = os.environ.get("ACE_user")
PWD = os.environ.get("ACE_password")


class ACEPageFunctions:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def login_to_ace(self):
        self.driver.find_element(By.ID, "Login").send_keys(f"{USER}")
        self.driver.find_element(By.ID, "Password").send_keys(f"{PWD}")
        self.driver.find_element(By.ID, "loginBtn").click()

    def go_to_add_time_item(self):
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-id='dlgEditTime']"))
            )
            element.click()
            return True
        except Exception as e:
            print(f"Failed to click 'Add time item': {e}")
            return False

    def click_time_menu(self):
        """ Click on the Time menu item """
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.ID, "div_img_mnu_3"))
            )
            element.click()
            return True
        except Exception as e:
            print(f"Failed to click Time menu: {e}")
            return False

    def switch_to_frame(self, frame_identifier):
        """ Switch to frame by id, name or index """
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(frame_identifier)
            return True
        except Exception as e:
            print(f"Failed to switch to frame '{frame_identifier}': {e}")
            return False

    def wait_for_and_switch_to_time_entry_iframe(self):
        """Wait for the time entry iframe to appear and switch to it"""
        try:
            # First switch to mainFrame
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")

            # Wait for the iframe to exist in the DOM
            self.wait.until(EC.presence_of_element_located((By.ID, "iframedlgNewTime")))

            # Now switch to it
            self.driver.switch_to.frame("iframedlgNewTime")
            print("Successfully switched to iframedlgNewTime")
            return True
        except Exception as e:
            print(f"Failed to switch to time entry iframe: {e}")
            return False

    def search_and_click(self, selector_type, selector_value):
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")
            self.driver.switch_to.frame("iframedlgNewTime")
            element = self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            try:
                element.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            print(f"Failed to click element {selector_value}: {e}")
            return False

    def select_project_and_task(self, project_value="77", task_value="194"):
        print(f"Selecting project {project_value} and task {task_value}...")

        # Open project dropdown
        if not self.search_and_click(By.XPATH, "//div[@id='PROJECT']//button"):
            print("Failed to click on project dropdown.")
            return False

        # Try multiple project selectors
        project_selectors = [
            (By.XPATH, f"//input[@value='{project_value}']"),
            (By.XPATH, f"//a[contains(text(), '{project_value}')]"),
            (By.XPATH, f"//span[contains(text(), '{project_value}')]/ancestor::a"),
        ]

        found_project = False
        for selector_type, selector_value in project_selectors:
            print(f"Trying project option selector: {selector_value}")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")
            self.driver.switch_to.frame("iframedlgNewTime")
            try:
                element = self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                try:
                    element.click()
                except:
                    self.driver.execute_script("arguments[0].click();", element)
                found_project = True
                print(f"✅ Selected project {project_value} using selector: {selector_value}")
                break
            except Exception as e:
                print(f"❌ Could not click project option with selector {selector_value}: {e}")

        if not found_project:
            print(f"❌ Failed to select project option {project_value}")
            return False

        time.sleep(0.5)

        # Open task dropdown
        if not self.search_and_click(By.XPATH, "//div[@id='TASK']//button"):
            print("Failed to click on task dropdown.")
            return False

        # Try multiple task selectors
        task_selectors = [
            (By.XPATH, f"//input[@value='{task_value}']"),
            (By.XPATH, f"//a[contains(text(), '{task_value}')]"),
            (By.XPATH, f"//span[contains(text(), '{task_value}')]/ancestor::a"),
        ]

        found_task = False
        for selector_type, selector_value in task_selectors:
            print(f"Trying task option selector: {selector_value}")
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")
            self.driver.switch_to.frame("iframedlgNewTime")
            try:
                element = self.wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                try:
                    element.click()
                except:
                    self.driver.execute_script("arguments[0].click();", element)
                found_task = True
                print(f"✅ Selected task {task_value} using selector: {selector_value}")
                break
            except Exception as e:
                print(f"❌ Could not click task option with selector {selector_value}: {e}")

        if not found_task:
            print(f"❌ Failed to select task option {task_value}")
            return False

        return True

    def enter_hours_for_week(self, hours_dict):
        """Enter user's hours per day of the week"""
        print("Attempting to enter hours for the week...")

        self.wait_for_and_switch_to_time_entry_iframe()
        success = True

        for i, (day, hours_status) in enumerate(hours_dict.items(), start=1):
            try:
                hour_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, f"HOUR{i}"))
                )
                hour_input.clear()
                hour_input.send_keys(hours_status)
                print(f"Successfully entered {hours_status} for {day} using id: HOUR{i}")
            except Exception as e:
                print(f"Failed to enter hours for {day}: {e}")
                success = False

        return success

    def add_comment(self, comment):
        """Enter user's comment"""
        print(f"Attempting to add comment: {comment}")

        self.wait_for_and_switch_to_time_entry_iframe()
        try:
            comment_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "COMMENT"))
            )
            comment_field.clear()
            comment_field.send_keys(comment)
            print("Comment added successfully using NAME attribute")
            return True
        except Exception as e:
            print(f"Failed to add comment: {e}")
            return False

    def save_time_entry(self):
        """Click the save button to submit the time entry"""
        print("Attempting to click the save button...")

        # First try in mainFrame
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ui-button')]/span[text()='Save']/.."))
            )
            save_button.click()
            print("Successfully clicked save button")
            return True
        except Exception as e:
            print(f"Failed to find save button in mainFrame: {e}")

            # As fallback, try with JavaScript
            try:
                self.driver.switch_to.default_content()
                self.driver.execute_script("""
                    let mainFrame = document.querySelector('#mainFrame');
                    if (mainFrame) {
                        let saveButtons = mainFrame.contentDocument.querySelectorAll('button');
                        for (let btn of saveButtons) {
                            if (btn.textContent.includes('Save')) {
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                """)
                print("Attempted to click save button using JavaScript")
                return True
            except Exception as js_error:
                print(f"Failed to click save button via JavaScript: {js_error}")
                return False

    def enter_hours_for_vac_hol_week(self, hours_dict):
        """Enter hours for vacation/holiday week"""
        print("Attempting to enter non-working hours for the week...")

        self.wait_for_and_switch_to_time_entry_iframe()
        success = True

        for i, (day, hours_status) in enumerate(hours_dict.items(), start=1):
            print(f"Day:{day}, hours: {hours_status}")
            if hours_status == '0H' or hours_status == '0V':
                print(f"Entering 8 for {day} (day {i})...")
                try:
                    hour_input = self.wait.until(
                        EC.presence_of_element_located((By.ID, f"HOUR{i}"))
                    )
                    hour_input.clear()
                    hour_input.send_keys('8')
                    print(f"Successfully entered 8 for {day} using id: HOUR{i}")
                except Exception as e:
                    print(f"Failed to enter non-working hours for {day}: {e}")
                    success = False

        return success

    def check_select_all_checkbox(self):
        """
           Directly click the title checkbox in the mainFrame using JavaScript.
        """
        print("Attempting to click the title checkbox...")
        try:
            # Switch to mainFrame where the checkbox exists
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")

            # Wait for the checkbox to be present
            checkbox = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "chkTitle"))
            )

            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)

            # Use JavaScript to click the checkbox directly
            self.driver.execute_script("arguments[0].click();", checkbox)

            print("Successfully clicked title checkbox using JavaScript")
            return True

        except Exception as e:
            print(f"Failed to click title checkbox: {e}")
            self.driver.switch_to.default_content()  # Return to default content on error
            return False
        finally:
            # Always return to default content
            self.driver.switch_to.default_content()

    def open_and_select_approver(self, approver_name="30_Ana_Perez"):
        print(f"Attempting to open dropdown and select: {approver_name}...")

        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")

            # Click on the dropdown
            dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.select2-selection--single"))
            )
            dropdown.click()
            print("Dropdown clicked.")

            # Wait for dropdown to open
            self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".select2-dropdown"))
            )
            print("Dropdown is open.")

            # Select the desired option
            option_xpath = f"//li[contains(text(), '{approver_name}')]"
            approver_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            approver_option.click()
            print(f"Approver '{approver_name}' selected.")
            return True

        except Exception as e:
            print(f"Error selecting approver: {e}")
            return False

    def click_send_approval_request(self):
        """Click the 'Send Approval Request' button"""
        print("Attempting to click the 'Send Approval Request' button...")

        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")
            button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Send Approval Request']"))
            )
            button.click()
            print("Successfully clicked 'Send Approval Request' button")
            return True
        except Exception as e:
            print(f"Failed to click 'Send Approval Request' button: {e}")
            return False
