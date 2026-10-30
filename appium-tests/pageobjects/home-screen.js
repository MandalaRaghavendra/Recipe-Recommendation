// home-screen.js - Home Recipe Discovery Feed & Interactive Filter Pills
const BaseScreen = require('./base-screen');

class HomeScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('Tastio'));
  }

  async search(query) {
    const input = await this.waitForElement(() => this.driver.findByText('Search recipes'));
    await input.clear();
    await input.sendKeys(query);
  }

  async selectCuisine(cuisine) {
    await this.safeTap(() => this.driver.findByText(cuisine));
  }

  async selectMealType(mealType) {
    await this.safeTap(() => this.driver.findByText(mealType));
  }

  async selectDiet(diet) {
    await this.safeTap(() => this.driver.findByText(diet));
  }

  async openUserAuth() {
    await this.safeTap(() => this.driver.findByText('Demo Chef'));
  }

  async openRecipe(recipeName) {
    await this.safeTap(() => this.driver.findByText(recipeName));
  }
}

module.exports = HomeScreen;

