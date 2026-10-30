// grocery-screen.js - 7-Category Smart Grocery Checklist Screen
const BaseScreen = require('./base-screen');

class GroceryScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Smart Grocery List'));
  }

  async tapCompileFromPlan() {
    await this.safeTap(() => this.driver.findByText('Compile from 7-Day Plan'));
  }

  async openAddItemModal() {
    await this.safeTap(() => this.driver.findByText('+ Add Item'));
  }

  async addCustomItem(name, category = 'Vegetables') {
    await this.openAddItemModal();
    const input = await this.waitForElement(() => this.driver.findByClass('android.widget.EditText'));
    await input.sendKeys(name);
    await this.safeTap(() => this.driver.findByText(category));
    await this.safeTap(() => this.driver.findByText('Save Item'));
  }

  async toggleItemCheckbox(itemName) {
    await this.safeTap(() => this.driver.findByText(itemName));
  }
}

module.exports = GroceryScreen;

