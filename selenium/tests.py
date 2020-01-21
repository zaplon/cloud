import os
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


class TestGabinet:
    start_page = "http://localhost:8081/"
    username = 'jan'
    password = 'Sadyba88'

    def setup_class(self):
        if os.environ.get('ENV') == 'docker':
            self.driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", DesiredCapabilities.CHROME)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(3)
        self.driver.set_window_size(1366, 768)
        self.vars = {}

    # let's start each test from the homepage
    def setup_method(self):
        self._login()

    def teardown_method(self):
        self._logout()
        WebDriverWait(self.driver, 15).until(EC.url_changes(self.driver.current_url))

    def teardown_class(self):
        self.driver.quit()

    def _login(self):
        self.driver.get(self.start_page)
        self.driver.find_element(By.NAME, "username").click()
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)

    def _logout(self):
        self.driver.execute_script('window.scrollTo(0, 0);')
        WebDriverWait(self.driver, 15).until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, "vue-notification-template vue-notification")))
        self.driver.find_element(By.ID, "ddown-divider__BV_toggle_").click()
        self.driver.find_element(By.CSS_SELECTOR, "li:nth-child(5) > .dropdown-item").click()

    def _add_and_start_new_visit(self):
        self.driver.find_element(By.CSS_SELECTOR, ".FREE .fc-content").click()
        self.driver.find_element(By.CSS_SELECTOR, "#termPatient input:nth-child(1)").click()
        self.driver.find_element(By.CSS_SELECTOR, "#termPatient input:nth-child(1)").send_keys('a')
        self.driver.find_element(By.CSS_SELECTOR, ".autocomplete__results__item:nth-child(1)").click()
        self.driver.find_element(By.CSS_SELECTOR, "#termService input:nth-child(1)").click()
        self.driver.find_element(By.CSS_SELECTOR, "#termService input:nth-child(1)").send_keys("por")
        self.driver.find_element(By.CSS_SELECTOR, ".autocomplete__results__item:nth-child(1)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(5)").click()
        WebDriverWait(self.driver, 15).until(EC.url_changes(self.driver.current_url))
        assert 'visit' in self.driver.current_url

    def _cancel_visit(self):
        self.driver.get(self.start_page + '#/kalendarz/')
        self.driver.find_element(By.CSS_SELECTOR, ".PENDING .fc-content").click()
        self.driver.find_element(By.CSS_SELECTOR, ".modal-footer .btn-danger").click()

    def test_starting_new_visit(self):
        self._add_and_start_new_visit()
        self.driver.back()
        self._cancel_visit()

    def test_adding_and_removing_tabs(self):
        self.driver.find_element(By.LINK_TEXT, "Zakładki").click()
        self.driver.find_element(By.CSS_SELECTOR, ".bottom-right").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(1) > .col-sm-9 > .form-control").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(1) > .col-sm-9 > .form-control").send_keys(
            "test")
        self.driver.find_element(By.NAME, "order").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(4) > .col-sm-9 > .form-control").click()
        dropdown = self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(4) > .col-sm-9 > .form-control")
        dropdown.find_element(By.XPATH, "//option[. = 'Pole tekstowe']").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(4) > .col-sm-9 > .form-control").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn-default:nth-child(2)").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-danger").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "#confirmModal___BV_modal_footer_ > .btn-primary").click()

    def test_filling_visit(self):
        self._add_and_start_new_visit()
        self.driver.find_element(By.CSS_SELECTOR, ".input-group > .form-control").send_keys("zapale")
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(1) .btn-sm").click()
        self.driver.find_element(By.CSS_SELECTOR, "ul.nav-pills li:nth-child(3)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-control input:nth-child(1)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-control input:nth-child(1)").send_keys("aspirin")
        self.driver.find_element(By.CSS_SELECTOR, ".autocomplete__results__item:nth-child(1)").click()
        dropdown = self.driver.find_element(By.CSS_SELECTOR,
                                            ".table:nth-child(1) tr:nth-child(1) > td:nth-child(1) > .form-control")
        dropdown.find_element(By.XPATH, "//option[. = '100 tabl.']").click()
        element = self.driver.find_element(By.CSS_SELECTOR,
                                           ".table:nth-child(1) tr:nth-child(1) > td:nth-child(1) > .form-control")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.CSS_SELECTOR,
                                           ".table:nth-child(1) tr:nth-child(1) > td:nth-child(1) > .form-control")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.CSS_SELECTOR,
                                           ".table:nth-child(1) tr:nth-child(1) > td:nth-child(1) > .form-control")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.CSS_SELECTOR,
                                 ".table:nth-child(1) tr:nth-child(1) > td:nth-child(1) > .form-control").click()
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(4) > .form-control").click()
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(4) > .form-control").click()
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(4) > .form-control").send_keys("3")
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(5) > .form-control").click()
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(5) > .form-control").send_keys("2x2")
        self.driver.find_element(By.CSS_SELECTOR, ".btn > span").click()
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, "pdfDocumentModal")))
        assert EC.presence_of_element_located((By.ID, "s-external-code"))
        element = self.driver.find_element(By.ID, "pdfDocumentModal")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "pdfDocumentModal")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "pdfDocumentModal")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.CSS_SELECTOR, ".pull-right > .btn").click()
        self.driver.execute_script('window.scrollTo(0, 0);')
        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.ID, "s-save-visit")))
        self.driver.find_element(By.ID, "s-save-visit").click()
        self.driver.find_element(By.CSS_SELECTOR, "#saveVisitModal___BV_modal_footer_ .mr-2").click()
        WebDriverWait(self.driver, 15).until(EC.url_changes(self.driver.current_url))
        assert 'kalendarz' in self.driver.current_url
        self._cancel_visit()


