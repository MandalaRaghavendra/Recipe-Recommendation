// grocery-page.js - Page object for Smart Grocery Checklist
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class GroceryPage extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      pageTitle: By.id('listNameTitle'),
      btnGeneratePlan: By.id('btnGeneratePlan'),
      btnClearAll: By.id('btnClearAll'),
      progressBadge: By.id('progressBadge'),
      progressBar: By.id('progressBar'),
      groceryItems: By.css('.grocery-item-row, div[id^="row-"]'),
      itemCheckboxes: By.css('input[type="checkbox"].form-check-input'),
      checkedRows: By.css('.is-checked'),
      emptyStateBox: By.id('emptyGroceryBox'),
      categoriesContainer: By.id('groceryCategoriesWrap')
    };
  }

  async open() {
    await this.navigate('/grocery-list');
  }

  async compileFromPlan() {
    await WaitHelper.safeClick(this.driver, this.locators.btnGeneratePlan);
    await WaitHelper.waitForElementPresent(this.driver, this.locators.groceryItems, 10000);
  }

  async getItemsCount() {
    const items = await this.driver.findElements(this.locators.groceryItems);
    return items.length;
  }

  async toggleFirstItem() {
    await WaitHelper.safeClick(this.driver, this.locators.itemCheckboxes);
  }

  async getCheckedCount() {
    const checked = await this.driver.findElements(this.locators.checkedRows);
    return checked.length;
  }
}

module.exports = GroceryPage;

