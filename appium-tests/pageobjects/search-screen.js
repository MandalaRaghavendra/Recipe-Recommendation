// search-screen.js - Dedicated AI Search & Pantry Intersection Screen
const BaseScreen = require('./base-screen');

class SearchScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Search'));
  }

  async enterPantryIngredients(ingredients) {
    const input = await this.waitForElement(() => this.driver.findByClass('android.widget.EditText'));
    await input.clear();
    await input.sendKeys(ingredients);
  }

  async tapSearch() {
    await this.safeTap(() => this.driver.findByText('Search'));
  }
}

module.exports = SearchScreen;

