from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

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
            print(f"Failed to click 'Add time item'")
            return False


    def list_all_iframes_on_the_page(self):
        frames = self.driver.find_elements(By.TAG_NAME, "iframe")
        frame_info = []
        for index, frame in enumerate(frames):
            frame_id = frame.get_attribute("id")
            frame_name = frame.get_attribute("name")
            frame_info.append({"index": index, "id": frame_id, "name": frame_name})
        return frame_info


    def find_element_in_frames(self, locator_type, locator_value, frame_list, timeout=5):
        """
        Search for an element across all frames and return which frame contains it.

        Args:
            locator_type: By.XPATH, By.ID, etc.
            locator_value: The actual locator string
            frame_list: Optional list of frame names/ids to check (if None, will check all frames)
            timeout: Seconds to wait for element in each frame

        Returns:
            dict: {'frame': frame_name/id or None if in main content, 'element': the element if found}
            None: If element not found in any frame
        """
        # First check in main content
        self.driver.switch_to.default_content()
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
            return {'frame': None, 'element': element}
        except (TimeoutException, NoSuchElementException):
            pass

        # Check each frame
        for frame_identifier in frame_list:
            try:
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame(frame_identifier)

                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((locator_type, locator_value))
                )
                return {'frame': frame_identifier, 'element': element}
            except (TimeoutException, NoSuchElementException):
                continue

        # Element not found in any frame
        self.driver.switch_to.default_content()
        return None


    def switch_to_frame(self, frame_identifier):
        """ Switch to frame by id, name or index """
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(frame_identifier)
            return True
        except Exception as e:
            print(f"Failed to switch to frame '{frame_identifier}': {e}")
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


    def search_and_interact_in_frames(self, selector_type, selector_value, interaction_type='find',
                                      interaction_value=None):
        """
        Systematically search for an element across frames with enhanced interaction capabilities.
        """
        # Reset to main document first
        self.driver.switch_to.default_content()

        # List of frames to check - starts with main content
        frames_to_check = [
            {'name': 'main_content', 'id': None},
            {'name': 'mainFrame', 'id': 'mainFrame'},
        ]

        # Add dynamic frame discovery - find all iframes in main content
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            frame_id = iframe.get_attribute('id')
            if frame_id and frame_id not in [frame['id'] for frame in frames_to_check if frame['id']]:
                frames_to_check.append({'name': frame_id, 'id': frame_id})

        # Check mainFrame and its nested frames
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")
            nested_frames = self.driver.find_elements(By.TAG_NAME, "iframe")
            for nested_frame in nested_frames:
                frame_id = nested_frame.get_attribute('id')
                if frame_id:
                    frames_to_check.append({'name': f'mainFrame > {frame_id}', 'id': frame_id, 'parent': 'mainFrame'})
        except:
            pass  # Continue if mainFrame doesn't exist

        # Return to default content
        self.driver.switch_to.default_content()

        # Now search through all discovered frames
        for frame in frames_to_check:
            try:
                # Switch to appropriate frame context
                self.driver.switch_to.default_content()
                if frame['id'] is None:
                    context = "main_content"
                elif 'parent' in frame and frame['parent'] == 'mainFrame':
                    self.driver.switch_to.frame('mainFrame')
                    self.driver.switch_to.frame(frame['id'])
                    context = f"mainFrame > {frame['id']}"
                else:
                    self.driver.switch_to.frame(frame['id'])
                    context = frame['id']

                print(f"🔍 Searching in frame: {context} for selector: {selector_type} = {selector_value}")

                # Try to find the element in this frame
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )

                print(f"✅ Element found in frame: {context}")

                # Perform requested interaction
                if interaction_type == 'click':
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        element.click()
                        print(f"🖱 Clicked element in {context}")
                    except Exception as click_error:
                        print(f"⚠️ Scroll/click failed: {click_error}")
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                        except:
                            pass
                elif interaction_type == 'send_keys' and interaction_value is not None:
                    try:
                        if element.tag_name in ['input', 'textarea']:
                            element.clear()
                        element.send_keys(interaction_value)
                        print(f"⌨️ Sent keys to element in {context}")
                    except Exception as send_error:
                        print(f"⚠️ send_keys failed: {send_error}")
                        try:
                            self.driver.execute_script(
                                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                                element, interaction_value
                            )
                        except:
                            pass

                self.driver.switch_to.default_content()
                return {'found': True, 'element': element, 'frame': context}

            except Exception as e:
                print(f"❌ No element in frame {frame['name']} | Reason: {str(e).splitlines()[0]}")
                continue

        # Element not found in any frame
        self.driver.switch_to.default_content()
        print(f"Element with {selector_type}: {selector_value} not found in any frame")
        return {'found': False}


    def find_element_in_current_frame(self, selector_type, selector_value):
        """
        Find an element in the currently active frame.

        Args:
            selector_type: Selenium By locator type
            selector_value: The locator string

        Returns:
            WebElement or None
        """
        try:
            element = self.driver.find_element(selector_type, selector_value)
            return element
        except Exception as e:
            print(f"Could not find element: {e}")
            return None


    def send_keys_to_element(self, selector_type, selector_value, keys_to_send):
        """
        Dedicated method to send keys to an element, with multiple fallback strategies.

        Args:
            selector_type: Selenium By locator type (e.g., By.ID, By.XPATH)
            selector_value: The locator string
            keys_to_send: The text/value to send to the element

        Returns:
            bool: True if successful, False otherwise
        """
        # List of frames to try
        frames_to_check = [
            None,  # Check main content first
            "mainFrame",  # Check mainFrame
            "iframedlgNewTime"  # Specific iframe you know contains the element
        ]

        for frame in frames_to_check:
            try:
                # Switch to the frame if specified
                if frame:
                    self.driver.switch_to.default_content()
                    self.driver.switch_to.frame(frame)
                else:
                    self.driver.switch_to.default_content()

                # Find the element
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )

                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

                # Multiple strategies to send keys
                try:
                    # Strategy 1: Standard clear and send_keys
                    element.clear()
                    element.send_keys(str(keys_to_send))
                    print(f"Successfully sent keys to element: {selector_value}")
                    return True
                except Exception as standard_error:
                    print(f"Standard send_keys failed: {standard_error}")

                    try:
                        # Strategy 2: JavaScript set value
                        self.driver.execute_script(
                            "arguments[0].value = arguments[1];",
                            element,
                            str(keys_to_send)
                        )
                        print(f"Successfully sent keys via JavaScript: {selector_value}")
                        return True
                    except Exception as js_error:
                        print(f"JavaScript send_keys failed: {js_error}")

            except Exception as frame_error:
                print(f"Error in frame {frame}: {frame_error}")
                continue
            finally:
                # Always return to default content
                self.driver.switch_to.default_content()

        print(f"Failed to send keys to element: {selector_value}")
        return False


    def add_comment(self, comment):
        """Enter user's comment"""
        print(f"Attempting to add comment: {comment}")

        # First try using name="COMMENT"
        result = self.search_and_interact_in_frames(By.NAME, "COMMENT", 'send_keys', comment)
        if result['found']:
            print(f"Comment added successfully using NAME attribute")
            return True

        # If that fails, try other common selectors for comment boxes
        selectors_to_try = [
            (By.ID, "COMMENT"),
            (By.XPATH, "//textarea[contains(@id, 'comment')]"),
            (By.XPATH, "//textarea[contains(@id, 'COMMENT')]"),
            (By.XPATH, "//textarea[contains(@name, 'comment')]"),
            (By.XPATH, "//textarea"),  # Last resort - look for any textarea
            (By.XPATH, "//div[contains(@id, 'commentBox')]//textarea"),
            (By.CSS_SELECTOR, ".comment-box textarea"),
            (By.CSS_SELECTOR, "textarea.commentField")
        ]

        for selector_type, selector_value in selectors_to_try:
            result = self.search_and_interact_in_frames(selector_type, selector_value, 'send_keys', comment)
            if result['found']:
                print(f"Comment added successfully using {selector_type}: {selector_value}")
                return True

        print("Failed to add comment - could not find any matching comment field")
        return False


    def enter_hours_for_week(self, hours_dict):
        """Enter user's hours per day of the week"""
        print("Attempting to enter hours for the week...")

        success = True
        for i, (day, hours_status) in enumerate(hours_dict.items(), start=1):
            print(f"Entering {hours_status} for {day} (day {i})...")

            # Define multiple selectors to try for each day
            selectors = [
                (By.ID, f"HOUR{i}"),
                (By.NAME, f"HOUR{i}"),
                (By.XPATH, f"//input[contains(@id, 'HOUR{i}')]"),
                (By.XPATH, f"//input[contains(@name, 'HOUR{i}')]"),
                (By.XPATH, f"//td[contains(text(), '{day}')]/following-sibling::td//input"),
                (By.CSS_SELECTOR, f"input[id*='HOUR{i}']"),
                (By.CSS_SELECTOR, f"input[name*='HOUR{i}']")
            ]

            found = False
            for selector_type, selector_value in selectors:
                result = self.search_and_interact_in_frames(selector_type, selector_value, 'send_keys', hours_status)
                if result['found']:
                    print(f"Successfully entered {hours_status} for {day} using {selector_type}: {selector_value}")
                    found = True
                    break

            if not found:
                print(f"Failed to enter hours for {day}")
                success = False

        return success


    def save_time_entry(self):
        """Click the save button to submit the time entry"""
        print("Attempting to click the save button...")

        # Multiple selectors to try for the save button based on the HTML you shared
        selectors = [
            (By.ID, "dlgNewTimebtnsave"),
            (By.XPATH, "//button[@id='dlgNewTimebtnsave']"),
            (By.XPATH, "//button[contains(@class, 'dialogApply')]"),
            (By.XPATH, "//span[contains(text(), 'Save')]/parent::button"),
            (By.XPATH, "//button[contains(@class, 'ui-button')]/span[text()='Save']/..")
        ]

        for selector_type, selector_value in selectors:
            result = self.search_and_interact_in_frames(selector_type, selector_value, 'click')
            if result['found']:
                print("Successfully clicked save button")
                return True

        # If direct click fails, try finding it with JavaScript
        try:
            self.driver.switch_to.default_content()
            self.driver.execute_script("""
                let frames = document.querySelectorAll('iframe');
                for (let i = 0; i < frames.length; i++) {
                    try {
                        let saveBtn = frames[i].contentDocument.querySelector('#dlgNewTimebtnsave');
                        if (saveBtn) {
                            saveBtn.click();
                            return true;
                        }
                    } catch (e) {}
                }

                // Try mainFrame and its nested frames
                try {
                    let mainFrame = document.querySelector('#mainFrame');
                    if (mainFrame) {
                        let nestedFrames = mainFrame.contentDocument.querySelectorAll('iframe');
                        for (let i = 0; i < nestedFrames.length; i++) {
                            try {
                                let saveBtn = nestedFrames[i].contentDocument.querySelector('#dlgNewTimebtnsave');
                                if (saveBtn) {
                                    saveBtn.click();
                                    return true;
                                }
                            } catch (e) {}
                        }
                    }
                } catch (e) {}

                return false;
            """)
            print("Attempted to click save button using JavaScript")
            return True
        except Exception as e:
            print(f"Failed to click save button: {e}")
            return False

    def enter_hours_for_vac_hol_week(self, hours_dict):
        """Enter user's hours per day of the week"""
        print("Attempting to enter non-working hours for the week...")

        success = True
        for i, (day, hours_status) in enumerate(hours_dict.items(), start=1):
            print(f"Day:{day}, hours: {hours_status}")
            if hours_status == '0H' or hours_status == '0V':
                print(f"Entering 8 for {day} (day {i})...")

                # Define multiple selectors to try for each day
                selectors = [
                    (By.ID, f"HOUR{i}"),
                    (By.NAME, f"HOUR{i}"),
                    (By.XPATH, f"//input[contains(@id, 'HOUR{i}')]"),
                    (By.XPATH, f"//input[contains(@name, 'HOUR{i}')]"),
                    (By.XPATH, f"//td[contains(text(), '{day}')]/following-sibling::td//input"),
                    (By.CSS_SELECTOR, f"input[id*='HOUR{i}']"),
                    (By.CSS_SELECTOR, f"input[name*='HOUR{i}']")
                ]

                found = False
                for selector_type, selector_value in selectors:
                    result = self.search_and_interact_in_frames(selector_type, selector_value, 'send_keys', '8')
                    if result['found']:
                        print(f"Successfully entered 8 for {day} using {selector_type}: {selector_value}")
                        found = True
                        break

                if not found:
                    print(f"Failed to enter non-working hours for {day}")
                    success = False

        return success


    def check_title_checkbox(self):
        """Click the title checkbox in the timesheet table"""
        print("Attempting to click the title checkbox...")

        # Multiple selectors to try for the checkbox
        selectors = [
            (By.ID, "chkTitle"),
            (By.NAME, "chkTitle"),
            (By.XPATH, "//input[@id='chkTitle']"),
            (By.XPATH, "//input[@name='chkTitle']"),
            (By.XPATH, "//input[@type='checkbox' and @id='chkTitle']"),
            (By.CSS_SELECTOR, "input#chkTitle")
        ]

        for selector_type, selector_value in selectors:
            result = self.search_and_interact_in_frames(selector_type, selector_value, 'click')
            if result['found']:
                print("Successfully clicked title checkbox")
                return True

        # If direct click fails, try JavaScript approach
        try:
            self.driver.switch_to.default_content()
            self.driver.execute_script("""
                let frames = document.querySelectorAll('iframe');
                for (let i = 0; i < frames.length; i++) {
                    try {
                        let checkbox = frames[i].contentDocument.querySelector('#chkTitle');
                        if (checkbox) {
                            checkbox.click();
                            return true;
                        }
                    } catch (e) {}
                }
    
                // Try mainFrame and its nested frames
                try {
                    let mainFrame = document.querySelector('#mainFrame');
                    if (mainFrame) {
                        let nestedFrames = mainFrame.contentDocument.querySelectorAll('iframe');
                        for (let i = 0; i < nestedFrames.length; i++) {
                            try {
                                let checkbox = nestedFrames[i].contentDocument.querySelector('#chkTitle');
                                if (checkbox) {
                                    checkbox.click();
                                    return true;
                                }
                            } catch (e) {}
                        }
                    }
                } catch (e) {}
    
                return false;
            """)
            print("Attempted to click title checkbox using JavaScript")
            return True
        except Exception as e:
            print(f"Failed to click title checkbox: {e}")
            return False

    def open_and_select_approver(self, approver_name="30_Ana_Perez"):
        print(f"Attempting to open dropdown and select: {approver_name}...")

        try:
            # Cambiar al frame principal (si no lo has hecho ya dentro de search_and_interact_in_frames)
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("mainFrame")

            # Hacer clic en el dropdown
            dropdown_clicked = False
            selectors = [
                (By.XPATH, "//span[@class='select2-selection select2-selection--single']"),
                (By.CSS_SELECTOR, "span.select2-selection--single"),
            ]

            for selector_type, selector_value in selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    element.click()
                    print("Dropdown clicked.")
                    dropdown_clicked = True
                    break
                except Exception as e:
                    print(f"Failed to click with {selector_value}: {e}")

            if not dropdown_clicked:
                print("Could not click dropdown.")
                return False

            # Esperar a que se abra el dropdown EN EL FRAME
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".select2-dropdown"))
            )
            print("Dropdown is open.")

            # Ahora seleccionar la opción deseada
            option_xpath = f"//li[contains(text(), '{approver_name}')]"
            approver_option = WebDriverWait(self.driver, 5).until(
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

        # Multiple selectors to try for the button
        selectors = [
            (By.XPATH, "//input[@value='Send Approval Request']"),
            (By.XPATH, "//input[@type='button' and @value='Send Approval Request']"),
            (By.CSS_SELECTOR, "input.btn[value='Send Approval Request']"),
            (By.CSS_SELECTOR, "input[type='button'][value='Send Approval Request']"),
            (By.XPATH, "//input[contains(@class, 'btn') and @value='Send Approval Request']"),
            (By.XPATH, "//div[contains(@class, 'approval')]//input[@type='button']")
        ]

        for selector_type, selector_value in selectors:
            result = self.search_and_interact_in_frames(selector_type, selector_value, 'click')
            if result['found']:
                print("Successfully clicked 'Send Approval Request' button")
                return True

        # If direct click fails, try JavaScript approach
        try:
            self.driver.switch_to.default_content()
            self.driver.execute_script("""
                // Function to find and click the button in a document
                function findAndClickButton(doc) {
                    // Try by value attribute
                    let button = doc.querySelector("input[value='Send Approval Request']");
                    if (button) {
                        button.click();
                        return true;
                    }

                    // Try by class and type
                    button = doc.querySelector("input.btn[type='button']");
                    if (button && button.value.includes('Send Approval Request')) {
                        button.click();
                        return true;
                    }

                    return false;
                }

                // Try in main document
                if (findAndClickButton(document)) return true;

                // Try in all frames
                let frames = document.querySelectorAll('iframe');
                for (let i = 0; i < frames.length; i++) {
                    try {
                        if (findAndClickButton(frames[i].contentDocument)) return true;
                    } catch (e) {}
                }

                // Try mainFrame and its nested frames
                try {
                    let mainFrame = document.querySelector('#mainFrame');
                    if (mainFrame) {
                        if (findAndClickButton(mainFrame.contentDocument)) return true;

                        let nestedFrames = mainFrame.contentDocument.querySelectorAll('iframe');
                        for (let i = 0; i < nestedFrames.length; i++) {
                            try {
                                if (findAndClickButton(nestedFrames[i].contentDocument)) return true;
                            } catch (e) {}
                        }
                    }
                } catch (e) {}

                return false;
            """)
            print("Attempted to click 'Send Approval Request' button using JavaScript")
            return True
        except Exception as e:
            print(f"Failed to click 'Send Approval Request' button: {e}")
            return False
