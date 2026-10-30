// login-modal.js - Page object for authentication modal interactions across main.html and index.html
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class LoginModal extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      // Handles both [data-bs-target="#authModal"] on main.html and a[data-bs-target="#loginModal"] on index.html
      authModalTrigger: By.css('[data-bs-target="#authModal"], a[data-bs-target="#loginModal"]'),
      loginTabBtn: By.id('login-tab'),
      activeModal: By.css('#authModal, #loginModal'),
      emailInput: By.css('#loginEmail, #authModal input[name="email"], form[action="/login"] input[name="email"]'),
      passwordInput: By.css('#loginPassword, #authModal input[name="password"], form[action="/login"] input[name="password"]'),
      submitButton: By.css('form[action="/login"] button[type="submit"]'),
      closeButton: By.css('#authModal .btn-close, #loginModal .btn-close'),
      cancelButton: By.css('#loginModal .btn-secondary, #authModal .btn-secondary'),
      userDropdown: By.css('#userDropdown, .navbar .dropdown-toggle, a[href="/logout"]'),
      logoutLink: By.css('a[href="/logout"]'),
      alertBanner: By.css('.alert, #message-area, #modalClientAlert')
    };
  }

  async open() {
    await WaitHelper.safeClick(this.driver, this.locators.authModalTrigger);
    await driverSleep(this.driver, 400);

    // If on main.html, ensure login tab is selected
    const loginTabs = await this.driver.findElements(this.locators.loginTabBtn);
    if (loginTabs.length > 0) {
      await WaitHelper.safeClick(this.driver, this.locators.loginTabBtn);
      await driverSleep(this.driver, 200);
    }
  }

  async enterEmail(email) {
    await WaitHelper.safeType(this.driver, this.locators.emailInput, email);
  }

  async enterPassword(password) {
    await WaitHelper.safeType(this.driver, this.locators.passwordInput, password);
  }

  async submit() {
    await WaitHelper.safeClick(this.driver, this.locators.submitButton);
  }

  async login(email, password) {
    await this.open();
    await this.enterEmail(email);
    await this.enterPassword(password);
    await this.submit();
  }

  async close() {
    await WaitHelper.safeClick(this.driver, this.locators.closeButton);
  }

  async isModalVisible() {
    return await WaitHelper.isElementDisplayed(this.driver, this.locators.activeModal, 1500);
  }

  async isLoggedIn() {
    return await WaitHelper.isElementDisplayed(this.driver, this.locators.userDropdown, 2500);
  }

  async logout() {
    try {
      await this.navigate('/logout');
    } catch {}
  }

  async getEmailValidationMessage() {
    const el = await WaitHelper.waitForElementPresent(this.driver, this.locators.emailInput);
    return await this.driver.executeScript('return arguments[0].validationMessage;', el);
  }

  async getPasswordValidationMessage() {
    const el = await WaitHelper.waitForElementPresent(this.driver, this.locators.passwordInput);
    return await this.driver.executeScript('return arguments[0].validationMessage;', el);
  }
}

async function driverSleep(driver, ms) {
  await driver.sleep(ms);
}

module.exports = LoginModal;
