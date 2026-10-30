// coach-screen.js - AI Nutrition Coach Streaming Assistant Screen
const BaseScreen = require('./base-screen');

class CoachScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Tastio AI Nutrition Coach'));
  }

  async tapQuickPrompt(promptText) {
    await this.safeTap(() => this.driver.findByText(promptText));
  }

  async sendMessage(message) {
    const input = await this.waitForElement(() => this.driver.findByClass('android.widget.EditText'));
    await input.clear();
    await input.sendKeys(message);
    await this.safeTap(() => this.driver.findByText('Send'));
  }
}

module.exports = CoachScreen;

