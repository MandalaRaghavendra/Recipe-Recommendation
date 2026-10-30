// screenshot-helper.js - Captures diagnostics and viewport screenshots on test failure
const fs = require('fs');
const path = require('path');
const config = require('../config/test-config');

class ScreenshotHelper {
  static async captureFailure(driver, testId, testTitle) {
    if (!config.screenshotOnFailure || !driver) return null;

    try {
      if (!fs.existsSync(config.screenshotDir)) {
        fs.mkdirSync(config.screenshotDir, { recursive: true });
      }

      const sanitizedTitle = (testTitle || 'test').replace(/[^a-zA-Z0-9_-]/g, '_').substring(0, 50);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${testId || 'FAIL'}_${sanitizedTitle}_${timestamp}.png`;
      const filepath = path.join(config.screenshotDir, filename);

      const image = await driver.takeScreenshot();
      fs.writeFileSync(filepath, image, 'base64');
      return filepath;
    } catch (err) {
      console.error(`Failed to capture screenshot for ${testId}:`, err.message);
      return null;
    }
  }
}

module.exports = ScreenshotHelper;

