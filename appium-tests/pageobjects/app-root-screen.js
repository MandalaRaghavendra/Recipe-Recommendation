// app-root-screen.js - Main App container, bottom navigation tabs and top server status bar
const BaseScreen = require('./base-screen');

class AppRootScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
    this.tabs = {
      home: 'Home',
      search: 'Search',
      scanner: 'Scan',
      planner: 'Plan',
      grocery: 'Grocery',
      coach: 'Coach',
      history: 'History',
      profile: 'Profile'
    };
  }

  async tapTab(tabName) {
    await this.safeTap(() => this.driver.findByText(tabName));
    await this.driver.sleep(400);
  }

  async isTabActive(tabName) {
    return await this.isElementVisible(() => this.driver.findByText(tabName));
  }

  async tapServerStatusPill() {
    await this.safeTap(() => this.driver.findByText('⚙️'));
  }

  async getServerStatusText() {
    return await this.getText(() => this.driver.findByText('API:'));
  }
}

module.exports = AppRootScreen;

