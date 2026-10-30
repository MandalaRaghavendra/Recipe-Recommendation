// meal-plan-screen.js - 7-Day AI Meal Plan Matrix & Meal Slot Swapper Screen
const BaseScreen = require('./base-screen');

class MealPlanScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isScreenLoaded() {
    return await this.isElementVisible(() => this.driver.findByText('7-Day AI'));
  }

  async selectDay(dayNumber = 1) {
    await this.safeTap(() => this.driver.findByText(`Day ${dayNumber}`));
  }

  async tapRegeneratePlan() {
    await this.safeTap(() => this.driver.findByText('New Plan'));
  }

  async tapSwapSlot(slot = 'Lunch') {
    await this.safeTap(() => this.driver.findByText('Swap'));
  }

  async selectAlternativeRecipe(recipeName) {
    await this.safeTap(() => this.driver.findByText(recipeName));
  }

  async logMealSlot(slot = 'Breakfast') {
    await this.safeTap(() => this.driver.findByText('Log'));
  }
}

module.exports = MealPlanScreen;

