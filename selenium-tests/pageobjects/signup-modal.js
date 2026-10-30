// signup-modal.js - Page object for registration modal interactions across main.html and index.html
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class SignupModal extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      authModalTrigger: By.css('[data-bs-target="#authModal"], a[data-bs-target="#signupModal"]'),
      signupTabBtn: By.id('signup-tab'),
      activeModal: By.css('#authModal, #signupModal'),
      nameInput: By.css('#signupName, #signup input[name="name"], form[action="/signup"] input[name="name"]'),
      emailInput: By.css('#signupEmail, #signup input[name="email"], form[action="/signup"] input[name="email"]'),
      passwordInput: By.css('#signupPassword, #signup input[name="password"], form[action="/signup"] input[name="password"]'),
      submitButton: By.css('#signup button[type="submit"], form[action="/signup"] button[type="submit"]'),
      closeButton: By.css('#authModal .btn-close, #signupModal .btn-close')
    };
  }

  async open() {
    const isShown = await this.driver.executeScript(`
      var m = document.querySelector('#authModal, #signupModal');
      return !!(m && m.classList.contains('show'));
    `);
    if (!isShown) {
      await WaitHelper.safeClick(this.driver, this.locators.authModalTrigger);
      await this.driver.sleep(400);
    }

    // Explicitly activate signup tab using Bootstrap 5 tab instance
    await this.driver.executeScript(`
      var tabBtn = document.getElementById('signup-tab');
      if (tabBtn && window.bootstrap) {
        var tab = bootstrap.Tab.getInstance(tabBtn) || new bootstrap.Tab(tabBtn);
        tab.show();
      } else if (tabBtn) {
        tabBtn.click();
      }
    `);
    await this.driver.sleep(400);
  }

  async register(name, email, password) {
    await this.open();
    await WaitHelper.safeType(this.driver, this.locators.nameInput, name);
    await WaitHelper.safeType(this.driver, this.locators.emailInput, email);
    await WaitHelper.safeType(this.driver, this.locators.passwordInput, password);
    await WaitHelper.safeClick(this.driver, this.locators.submitButton);
  }

  async close() {
    await WaitHelper.safeClick(this.driver, this.locators.closeButton);
  }

  async isModalVisible() {
    return await WaitHelper.isElementDisplayed(this.driver, this.locators.activeModal, 1500);
  }
}

module.exports = SignupModal;
