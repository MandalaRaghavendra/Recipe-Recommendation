// meal-plan-page.js - Page object for 7-Day AI Meal Plan section
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class MealPlanPage extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      pageHeading: By.css('h3, .navbar-brand'),
      btnRegenerate: By.id('btnRegenerate'),
      dayTabsContainer: By.id('dayTabsContainer'),
      dayPills: By.css('#dayTabsContainer button, .nav-pills button'),
      mealCards: By.css('.meal-card, div[data-meal-type]'),
      mealImages: By.css('.meal-img, .meal-card img'),
      activeDayCal: By.id('activeDayCal'),
      activeDayProt: By.id('activeDayProt'),
      swapButtons: By.css('button[onclick*="openSwapModal"], .btn-swap'),
      swapModal: By.id('swapModal'),
      alternativeCards: By.css('.alt-card, #swapCandidatesList .card'),
      altImages: By.css('.alt-img, .alt-card img')
    };
  }

  async open() {
    await this.navigate('/meal-plan');
    await WaitHelper.waitForElementPresent(this.driver, this.locators.dayTabsContainer, 10000);
  }

  async getMealImagesCount() {
    const images = await this.driver.findElements(this.locators.mealImages);
    return images.length;
  }

  async verifyMealImagesHaveSrc() {
    const images = await this.driver.findElements(this.locators.mealImages);
    const results = [];
    for (const img of images) {
      const src = await img.getAttribute('src');
      const isDisplayed = await img.isDisplayed();
      results.push({ src, isDisplayed, valid: !!(src && src.length > 5) });
    }
    return results;
  }

  async selectDay(dayIndex) {
    const dayPill = By.id(`tab-btn-${dayIndex}`);
    await WaitHelper.safeClick(this.driver, dayPill);
  }

  async openSwapModalFirstSlot() {
    await WaitHelper.safeClick(this.driver, this.locators.swapButtons);
    await WaitHelper.waitForElementVisible(this.driver, this.locators.swapModal, 5000);
  }
}

module.exports = MealPlanPage;

