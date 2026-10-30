// test-config.js - Centralized configuration for Tastio Selenium E2E Framework
require('dotenv').config();
const path = require('path');

const config = {
  baseUrl: process.env.TEST_BASE_URL || 'http://127.0.0.1:5000',
  browser: (process.env.SELENIUM_BROWSER || 'chrome').toLowerCase(),
  headless: process.env.HEADLESS_MODE !== 'false', // Defaults to headless true
  explicitWaitTimeout: parseInt(process.env.EXPLICIT_WAIT_TIMEOUT, 10) || 10000,
  windowSize: {
    width: parseInt(process.env.BROWSER_WIDTH, 10) || 1920,
    height: parseInt(process.env.BROWSER_HEIGHT, 10) || 1080
  },
  testUser: {
    name: process.env.TEST_USER_NAME || 'Selenium Test Chef',
    email: process.env.TEST_USER_EMAIL || 'selenium_chef@test.local',
    password: process.env.TEST_USER_PASSWORD || 'TestPass123!'
  },
  reportsDir: path.resolve(__dirname, '../reports'),
  screenshotDir: path.resolve(__dirname, '../reports/screenshots'),
  screenshotOnFailure: process.env.SCREENSHOT_ON_FAILURE !== 'false'
};

module.exports = config;

