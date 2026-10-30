// recipe-detail-modal.js - Page object for recipe detail popups & interactions
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class RecipeDetailModal extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      modalDialog: By.css('.modal.show, div[id^="recipeModal"].show'),
      recipeTitle: By.css('.modal.show .modal-title, div[id^="recipeModal"].show h4'),
      heroImage: By.css('.modal.show img, div[id^="recipeModal"].show img'),
      addToGroceryBtn: By.css('.modal.show button[onclick*="addRecipeToGrocery"], div[id^="recipeModal"] button[data-recipe-id]'),
      markEatenBtn: By.css('.modal.show button[onclick*="markRecipeEaten"], div[id^="recipeModal"] .btn-eaten'),
      favoriteBtn: By.css('.modal.show button[onclick*="toggleFavorite"]'),
      closeBtn: By.css('.modal.show .btn-close, .modal.show button[data-bs-dismiss="modal"]')
    };
  }

  async isModalOpen() {
    return await WaitHelper.isElementDisplayed(this.driver, this.locators.modalDialog, 3000);
  }

  async getTitleText() {
    return await WaitHelper.safeGetText(this.driver, this.locators.recipeTitle);
  }

  async clickAddToGrocery() {
    await WaitHelper.safeClick(this.driver, this.locators.addToGroceryBtn);
  }

  async clickMarkEaten() {
    await WaitHelper.safeClick(this.driver, this.locators.markEatenBtn);
  }

  async clickFavorite() {
    await WaitHelper.safeClick(this.driver, this.locators.favoriteBtn);
  }

  async closeModal() {
    await WaitHelper.safeClick(this.driver, this.locators.closeBtn);
  }
}

module.exports = RecipeDetailModal;

