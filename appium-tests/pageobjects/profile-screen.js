// profile-screen.js - User Profile, Dietary Goals & Metabolic Baseline Screen
const BaseScreen = require('./base-screen');

class ProfileScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Dietary Profile'));
  }

  async updateMetrics(age, height, weight) {
    const inputs = await this.driver.findElements('class name', 'android.widget.EditText');
    if (inputs.length >= 3) {
      await inputs[0].clear();
      await inputs[0].sendKeys(String(age));
      await inputs[1].clear();
      await inputs[1].sendKeys(String(height));
      await inputs[2].clear();
      await inputs[2].sendKeys(String(weight));
    }
  }

  async selectGoal(goalName = 'Weight Loss') {
    await this.safeTap(() => this.driver.findByText(goalName));
  }

  async saveProfile() {
    await this.safeTap(() => this.driver.findByText('Save Profile'));
  }
}

module.exports = ProfileScreen;

