// driver-factory.js - WebDriver session initialization and lifecycle manager
const { Builder } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const edge = require('selenium-webdriver/edge');
const firefox = require('selenium-webdriver/firefox');
const fs = require('fs');
const path = require('path');
const config = require('../config/test-config');

class DriverFactory {
  static getCachedChromeDriver() {
    const defaultCached = 'C:\\Users\\Raghu\\.cache\\selenium\\chromedriver\\win64\\156.0.8078.80\\chromedriver.exe';
    if (process.env.CHROMEDRIVER_PATH && fs.existsSync(process.env.CHROMEDRIVER_PATH)) {
      return process.env.CHROMEDRIVER_PATH;
    }
    if (fs.existsSync(defaultCached)) {
      return defaultCached;
    }
    // Check general user cache dir
    const userProfile = process.env.USERPROFILE || process.env.HOME || '';
    if (userProfile) {
      const candidate = path.join(userProfile, '.cache', 'selenium', 'chromedriver', 'win64', '156.0.8078.80', 'chromedriver.exe');
      if (fs.existsSync(candidate)) {
        return candidate;
      }
    }
    return null;
  }

  static async createDriver() {
    let builder = new Builder().forBrowser(config.browser);

    if (config.browser === 'chrome') {
      const options = new chrome.Options();
      if (config.headless) {
        options.addArguments('--headless=new');
      }
      options.addArguments(
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        `--window-size=${config.windowSize.width},${config.windowSize.height}`,
        '--disable-extensions',
        '--ignore-certificate-errors'
      );
      builder = builder.setChromeOptions(options);

      const cachedDriver = this.getCachedChromeDriver();
      if (cachedDriver) {
        builder = builder.setChromeService(new chrome.ServiceBuilder(cachedDriver));
      }
    } else if (config.browser === 'edge') {
      const options = new edge.Options();
      if (config.headless) {
        options.addArguments('--headless=new');
      }
      options.addArguments(
        '--no-sandbox',
        '--disable-dev-shm-usage',
        `--window-size=${config.windowSize.width},${config.windowSize.height}`
      );
      builder = builder.setEdgeOptions(options);
    } else if (config.browser === 'firefox') {
      const options = new firefox.Options();
      if (config.headless) {
        options.addArguments('-headless');
      }
      builder = builder.setFirefoxOptions(options);
    }

    const driver = await builder.build();
    await driver.manage().setTimeouts({
      implicit: 0, // Prefer explicit waits everywhere
      pageLoad: 30000,
      script: 30000
    });

    return driver;
  }
}

module.exports = DriverFactory;
