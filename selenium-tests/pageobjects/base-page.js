// base-page.js - Foundation page object containing common browser interactions
const { By } = require('selenium-webdriver');
const WaitHelper = require('../utils/wait-helper');
const config = require('../config/test-config');

class BasePage {
  constructor(driver) {
    this.driver = driver;
    this.baseUrl = config.baseUrl;
  }

  async navigate(path = '/') {
    const fullUrl = path.startsWith('http') ? path : `${this.baseUrl}${path}`;
    await this.driver.get(fullUrl);
    await this.driver.manage().window().setRect({ width: config.windowSize.width, height: config.windowSize.height });
  }

  async getTitle() {
    return await this.driver.getTitle();
  }

  async getCurrentUrl() {
    return await this.driver.getCurrentUrl();
  }

  async refresh() {
    await this.driver.navigate().refresh();
  }

  async executeScript(script, ...args) {
    return await this.driver.executeScript(script, ...args);
  }

  async isElementVisible(locator, timeout = 3000) {
    return await WaitHelper.isElementDisplayed(this.driver, locator, timeout);
  }
}

module.exports = BasePage;

