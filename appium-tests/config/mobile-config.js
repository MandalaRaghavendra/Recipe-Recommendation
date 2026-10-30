// mobile-config.js - Configuration for Appium Android E2E Automation
const path = require('path');
require('dotenv').config();

module.exports = {
  appium: {
    host: process.env.APPIUM_HOST || '127.0.0.1',
    port: parseInt(process.env.APPIUM_PORT || '4723', 10),
    baseUrl: process.env.APPIUM_BASE_URL || 'http://127.0.0.1:4723',
    timeoutMs: 30000
  },

  capabilities: {
    platformName: 'Android',
    'appium:automationName': 'UiAutomator2',
    'appium:appPackage': 'com.mandalaraghavendra.tastio',
    'appium:appActivity': 'com.mandalaraghavendra.tastio.MainActivity',
    'appium:deviceName': process.env.ANDROID_DEVICE_NAME || 'Android Emulator',
    'appium:platformVersion': process.env.ANDROID_PLATFORM_VERSION || '13.0',
    'appium:noReset': true,
    'appium:fullReset': false,
    'appium:autoGrantPermissions': true,
    'appium:newCommandTimeout': 180,
    'appium:uiautomator2ServerLaunchTimeout': 60000,
    'appium:adbExecTimeout': 30000
  },

  backend: {
    url: process.env.TASTIO_API_URL || 'http://127.0.0.1:5000/api',
    hostIp: process.env.DEV_HOST_IP || '10.231.101.150'
  },

  testUser: {
    email: 'demo@tastio.ai',
    name: 'Demo Chef',
    password: 'TestPassword123!'
  },

  reportsDir: path.resolve(__dirname, '../reports'),
  reportPath: path.resolve(__dirname, '../reports/appium-test-report.xlsx')
};

