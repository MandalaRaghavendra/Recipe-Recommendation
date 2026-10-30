// base-screen.js - Base Screen Object for Android Appium Automation
class BaseScreen {
  constructor(driver) {
    this.driver = driver;
  }

  async waitForElement(findByFn, timeoutMs = 10000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      try {
        const el = await findByFn();
        if (el) return el;
      } catch (e) {}
      await this.driver.sleep(300);
    }
    throw new Error(`Element not found within ${timeoutMs}ms`);
  }

  async safeTap(findByFn, timeoutMs = 8000) {
    const el = await this.waitForElement(findByFn, timeoutMs);
    await el.click();
  }

  async safeType(findByFn, text, timeoutMs = 8000) {
    const el = await this.waitForElement(findByFn, timeoutMs);
    await el.clear();
    await el.sendKeys(text);
  }

  async isElementVisible(findByFn, timeoutMs = 3000) {
    try {
      const el = await this.waitForElement(findByFn, timeoutMs);
      return await el.isDisplayed();
    } catch (e) {
      return false;
    }
  }

  async getText(findByFn, timeoutMs = 5000) {
    const el = await this.waitForElement(findByFn, timeoutMs);
    return await el.getText();
  }
}

module.exports = BaseScreen;

