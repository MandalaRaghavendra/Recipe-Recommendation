// home-search-page.js - Page object for main landing page and search flows
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class HomeSearchPage extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      brandLogo: By.css('.navbar-brand'),
      generalSearchTab: By.id('general-search-tab'),
      pantrySearchTab: By.id('pantry-search-tab'),
      searchInput: By.css('input[name="query"]'),
      searchSubmitBtn: By.css('form[action="/recommend"] button[type="submit"]'),
      pantryInput: By.id('pantryInput'),
      pantrySubmitBtn: By.css('#pantryForm button[type="submit"]'),
      recipeCards: By.css('.recipe-card'),
      firstRecipeCard: By.css('.recipe-card:first-of-type'),
      mealPlanNavLink: By.css('a[href="/meal-plan"], a[href="/mealplan"]'),
      groceryNavLink: By.css('a[href="/grocery-list"]'),
      coachNavLink: By.css('a[href="/coach"], a[href="/ai-coach"]'),
      scannerNavLink: By.css('a[href="/scanner"]'),
      profileNavLink: By.css('a[href="/profile"]'),
      noResultsAlert: By.css('.alert-warning, .no-recipes-box')
    };
  }

  async openHomePage() {
    await this.navigate('/');
  }

  async searchRecipes(query) {
    await WaitHelper.safeClick(this.driver, this.locators.generalSearchTab);
    await WaitHelper.safeType(this.driver, this.locators.searchInput, query);
    await WaitHelper.safeClick(this.driver, this.locators.searchSubmitBtn);
    await WaitHelper.waitForElementPresent(this.driver, this.locators.recipeCards, 10000);
  }

  async searchPantry(ingredients) {
    await WaitHelper.safeClick(this.driver, this.locators.pantrySearchTab);
    await WaitHelper.safeType(this.driver, this.locators.pantryInput, ingredients);
    await WaitHelper.safeClick(this.driver, this.locators.pantrySubmitBtn);
    await WaitHelper.waitForElementPresent(this.driver, this.locators.recipeCards, 10000);
  }

  async getRecipeCardsCount() {
    const cards = await this.driver.findElements(this.locators.recipeCards);
    return cards.length;
  }

  async clickFirstRecipeCard() {
    await WaitHelper.safeClick(this.driver, this.locators.firstRecipeCard);
  }
}

module.exports = HomeSearchPage;

