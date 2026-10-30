// profile-page.js - Page object for user biometrics & analytics
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class ProfilePage extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      ageInput: By.id('age'),
      genderSelect: By.id('gender'),
      heightInput: By.id('height'),
      weightInput: By.id('weight'),
      goalSelect: By.id('diet_goal'),
      saveBtn: By.id('saveProfileBtn'),
      btnViewToday: By.id('btnViewToday'),
      btnViewWeek: By.id('btnViewWeek'),
      btnViewMonth: By.id('btnViewMonth'),
      editTab: By.id('v-pills-edit-tab'),
      profileTab: By.id('v-pills-profile-tab'),
      historyTab: By.id('v-pills-history-tab')
    };
  }

  async open() {
    await this.navigate('/profile');
  }

  async updateBiometrics(age, height, weight) {
    await WaitHelper.safeClick(this.driver, this.locators.editTab);
    await WaitHelper.safeType(this.driver, this.locators.ageInput, String(age));
    await WaitHelper.safeType(this.driver, this.locators.heightInput, String(height));
    await WaitHelper.safeType(this.driver, this.locators.weightInput, String(weight));
    await WaitHelper.safeClick(this.driver, this.locators.saveBtn);
  }
}

module.exports = ProfilePage;

