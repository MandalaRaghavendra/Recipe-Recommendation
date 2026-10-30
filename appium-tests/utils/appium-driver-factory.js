// appium-driver-factory.js - W3C Appium Mobile Driver & Session Management
const http = require('http');
const config = require('../config/mobile-config');

class AppiumDriver {
  constructor(sessionId, baseUrl) {
    this.sessionId = sessionId;
    this.baseUrl = baseUrl;
  }

  async sendRequest(method, endpoint, body = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(`${this.baseUrl}/session/${this.sessionId}${endpoint}`);
      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: method,
        headers: {
          'Content-Type': 'application/json;charset=utf-8'
        },
        timeout: 20000
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const parsed = JSON.parse(data);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(parsed.value);
            } else {
              reject(new Error(parsed.value?.message || `Appium error HTTP ${res.statusCode}: ${data}`));
            }
          } catch (e) {
            resolve(data);
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error(`Appium request timed out on ${endpoint}`));
      });

      if (body) {
        req.write(JSON.stringify(body));
      }
      req.end();
    });
  }

  async findElement(strategy, selector) {
    const res = await this.sendRequest('POST', '/element', {
      using: strategy,
      value: selector
    });
    const elementId = res.ELEMENT || res['element-6066-11e4-a52e-4f735466cecf'];
    return new MobileElement(this, elementId);
  }

  async findElements(strategy, selector) {
    const list = await this.sendRequest('POST', '/elements', {
      using: strategy,
      value: selector
    });
    return (list || []).map(res => {
      const elementId = res.ELEMENT || res['element-6066-11e4-a52e-4f735466cecf'];
      return new MobileElement(this, elementId);
    });
  }

  async findByText(text) {
    return this.findElement('-android uiautomator', `new UiSelector().textContains("${text}")`);
  }

  async findByExactText(text) {
    return this.findElement('-android uiautomator', `new UiSelector().text("${text}")`);
  }

  async findByDescription(desc) {
    return this.findElement('-android uiautomator', `new UiSelector().descriptionContains("${desc}")`);
  }

  async findByResourceId(resId) {
    return this.findElement('-android uiautomator', `new UiSelector().resourceId("${resId}")`);
  }

  async findByClass(className) {
    return this.findElement('class name', className);
  }

  async getPageSource() {
    return await this.sendRequest('GET', '/source');
  }

  async takeScreenshot() {
    return await this.sendRequest('GET', '/screenshot');
  }

  async pressKeyCode(keyCode) {
    return await this.sendRequest('POST', '/appium/device/press_keycode', { keycode: keyCode });
  }

  async pressBack() {
    return await this.pressKeyCode(4);
  }

  async pressHome() {
    return await this.pressKeyCode(3);
  }

  async backgroundApp(seconds = 5) {
    return await this.sendRequest('POST', '/appium/app/background', { seconds });
  }

  async sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  async quit() {
    if (!this.sessionId) return;
    try {
      await new Promise((resolve) => {
        const url = new URL(`${this.baseUrl}/session/${this.sessionId}`);
        const req = http.request({
          hostname: url.hostname,
          port: url.port,
          path: url.pathname,
          method: 'DELETE'
        }, () => resolve());
        req.on('error', () => resolve());
        req.end();
      });
    } catch (e) {}
    this.sessionId = null;
  }
}

class MobileElement {
  constructor(driver, elementId) {
    this.driver = driver;
    this.elementId = elementId;
  }

  async click() {
    return await this.driver.sendRequest('POST', `/element/${this.elementId}/click`);
  }

  async clear() {
    return await this.driver.sendRequest('POST', `/element/${this.elementId}/clear`);
  }

  async sendKeys(text) {
    return await this.driver.sendRequest('POST', `/element/${this.elementId}/value`, {
      text: text,
      value: text.split('')
    });
  }

  async getText() {
    return await this.driver.sendRequest('GET', `/element/${this.elementId}/text`);
  }

  async getAttribute(name) {
    return await this.driver.sendRequest('GET', `/element/${this.elementId}/attribute/${name}`);
  }

  async isDisplayed() {
    try {
      return await this.driver.sendRequest('GET', `/element/${this.elementId}/displayed`);
    } catch (e) {
      return false;
    }
  }
}

class AppiumDriverFactory {
  static async createDriver(customCaps = {}) {
    const caps = {
      capabilities: {
        alwaysMatch: {
          ...config.capabilities,
          ...customCaps
        }
      }
    };

    return new Promise((resolve, reject) => {
      const url = new URL(`${config.appium.baseUrl}/session`);
      const postData = JSON.stringify(caps);

      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=utf-8',
          'Content-Length': Buffer.byteLength(postData)
        },
        timeout: 45000
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            if (res.statusCode >= 200 && res.statusCode < 300) {
              const sessionId = json.value?.sessionId || json.sessionId;
              resolve(new AppiumDriver(sessionId, config.appium.baseUrl));
            } else {
              reject(new Error(json.value?.message || `Failed to create Appium session: ${data}`));
            }
          } catch (e) {
            reject(new Error(`Failed to parse Appium session response: ${data}`));
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Appium session creation timed out. Ensure Appium server is running on port 4723.'));
      });

      req.write(postData);
      req.end();
    });
  }
}

module.exports = {
  AppiumDriver,
  MobileElement,
  AppiumDriverFactory
};

