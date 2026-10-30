// scanner-screen.js - Food Vision AI Camera & Gallery Dish Recognition Screen
const BaseScreen = require('./base-screen');

class ScannerScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Take Photo'));
  }

  async tapTakePhoto() {
    await this.safeTap(() => this.driver.findByText('Take Photo'));
  }

  async tapChooseGallery() {
    await this.safeTap(() => this.driver.findByText('Choose from Gallery'));
  }

  async tapSampleDish(dishName = 'Biryani') {
    await this.safeTap(() => this.driver.findByText(dishName));
  }

  async isRecognitionCardVisible() {
    return await this.isElementVisible(() => this.driver.findByText('Match'));
  }
}

module.exports = ScannerScreen;

