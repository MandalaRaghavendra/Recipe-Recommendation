// scanner-page.js - Page object for food image recognition scanner
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class ScannerPage extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      dropzone: By.id('dropzone'),
      foodImageInput: By.id('foodImageInput'),
      dropzonePrompt: By.id('dropzonePrompt'),
      previewContainer: By.id('previewContainer'),
      previewImg: By.id('previewImg'),
      btnScanPhoto: By.id('btnScanPhoto'),
      btnLogMeal: By.id('btnLogMeal')
    };
  }

  async open() {
    await this.navigate('/scanner');
    await WaitHelper.waitForElementPresent(this.driver, this.locators.dropzone, 10000);
  }

  async isDropzoneVisible() {
    return await WaitHelper.isElementDisplayed(this.driver, this.locators.dropzone, 5000);
  }
}

module.exports = ScannerPage;

