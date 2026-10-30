// recipe-detail-modal-screen.js - Recipe Details, Servings Multiplier, Nutrition & Reviews
const BaseScreen = require('./base-screen');

class RecipeDetailModalScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isModalOpen() {
    return await this.isElementVisible(() => this.driver.findByText('Serving Size:'));
  }

  async selectServingSize(scaler = '1x') {
    await this.safeTap(() => this.driver.findByText(scaler));
  }

  async tapAddToGrocery() {
    await this.safeTap(() => this.driver.findByText('Add to Grocery'));
  }

  async tapMarkAsCooked() {
    await this.safeTap(() => this.driver.findByText('Mark as Cooked'));
  }

  async toggleFavorite() {
    await this.safeTap(() => this.driver.findByText('Favorite'));
  }

  async submitReview(stars = 5, comment = 'Delicious!') {
    await this.safeTap(() => this.driver.findByText('Write Review'));
    const input = await this.waitForElement(() => this.driver.findByClass('android.widget.EditText'));
    await input.sendKeys(comment);
    await this.safeTap(() => this.driver.findByText('Submit'));
  }

  async closeModal() {
    await this.safeTap(() => this.driver.findByText('Close'));
  }
}

module.exports = RecipeDetailModalScreen;

