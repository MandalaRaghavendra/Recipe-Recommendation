// history-screen.js - Dietary Analytics & Daily Intake Log Screen
const BaseScreen = require('./base-screen');

class HistoryScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Intake History'));
  }

  async switchAnalyticsTab(tab = 'week') {
    await this.safeTap(() => this.driver.findByText(tab.toUpperCase()));
  }

  async switchMainTab(tab = 'log') {
    await this.safeTap(() => this.driver.findByText(tab === 'log' ? 'Meal Log' : 'Analytics'));
  }
}

module.exports = HistoryScreen;

