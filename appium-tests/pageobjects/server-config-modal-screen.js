// server-config-modal-screen.js - Dynamic Server IP & Connectivity Settings Modal
const BaseScreen = require('./base-screen');

class ServerConfigModalScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isModalOpen() {
    return await this.isElementVisible(() => this.driver.findByText('Server & API Settings'));
  }

  async setHostIp(ip) {
    const input = await this.waitForElement(() => this.driver.findByClass('android.widget.EditText'));
    await input.clear();
    await input.sendKeys(ip);
  }

  async tapPresetWifi() {
    await this.safeTap(() => this.driver.findByText('Wi-Fi IP'));
  }

  async tapPresetLocalhost() {
    await this.safeTap(() => this.driver.findByText('Localhost'));
  }

  async tapPresetUsb() {
    await this.safeTap(() => this.driver.findByText('USB'));
  }

  async tapTestConnection() {
    await this.safeTap(() => this.driver.findByText('Test Connection'));
  }

  async tapSaveAndApply() {
    await this.safeTap(() => this.driver.findByText('Save & Apply'));
  }

  async closeModal() {
    await this.safeTap(() => this.driver.findByText('✕'));
  }
}

module.exports = ServerConfigModalScreen;

