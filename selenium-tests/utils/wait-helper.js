// wait-helper.js - Robust explicit wait utilities avoiding arbitrary sleeps
const { until, By } = require('selenium-webdriver');
const config = require('../config/test-config');

class WaitHelper {
  static async waitForElementVisible(driver, locator, timeout = config.explicitWaitTimeout) {
    const element = await driver.wait(until.elementLocated(locator), timeout, `Element not located: ${locator}`);
    await driver.wait(until.elementIsVisible(element), timeout, `Element not visible: ${locator}`);
    return element;
  }

  static async waitForElementClickable(driver, locator, timeout = config.explicitWaitTimeout) {
    const element = await this.waitForElementVisible(driver, locator, timeout);
    await driver.wait(until.elementIsEnabled(element), timeout, `Element not enabled: ${locator}`);
    return element;
  }

  static async waitForElementPresent(driver, locator, timeout = config.explicitWaitTimeout) {
    return await driver.wait(until.elementLocated(locator), timeout, `Element not present: ${locator}`);
  }

  static async waitForTextInElement(driver, locator, text, timeout = config.explicitWaitTimeout) {
    const element = await driver.wait(until.elementLocated(locator), timeout);
    await driver.wait(until.elementTextContains(element, text), timeout, `Text "${text}" not found in element: ${locator}`);
    return element;
  }

  static async waitForUrlContains(driver, text, timeout = config.explicitWaitTimeout) {
    await driver.wait(until.urlContains(text), timeout, `URL did not contain: "${text}"`);
  }

  static async safeClick(driver, locator, timeout = config.explicitWaitTimeout) {
    const element = await this.waitForElementPresent(driver, locator, timeout);
    try {
      await driver.executeScript('arguments[0].scrollIntoView({block: "center"});', element);
      await element.click();
    } catch (e) {
      // JS click fallback if intercepted by sticky element or animations
      await driver.executeScript('arguments[0].click();', element);
    }
  }

  static async safeType(driver, locator, text, clear = true, timeout = config.explicitWaitTimeout) {
    const element = await this.waitForElementVisible(driver, locator, timeout);
    if (clear) {
      await element.clear();
    }
    await element.sendKeys(text);
  }

  static async safeGetText(driver, locator, timeout = config.explicitWaitTimeout) {
    try {
      const element = await this.waitForElementPresent(driver, locator, timeout);
      return await element.getText();
    } catch {
      return '';
    }
  }

  static async isElementDisplayed(driver, locator, timeout = 2000) {
    try {
      const element = await driver.wait(until.elementLocated(locator), timeout);
      return await element.isDisplayed();
    } catch {
      return false;
    }
  }
}

module.exports = WaitHelper;
