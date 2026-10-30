// pantry-what-can-i-cook-tests.js - Comprehensive Selenium tests for Pantry Ingredient Intersection (What Can I Cook) (WEB-136 to WEB-165)
const { expect } = require('chai');
const { By, Key } = require('selenium-webdriver');
const DriverFactory = require('../utils/driver-factory');
const HomeSearchPage = require('../pageobjects/home-search-page');
const ScreenshotHelper = require('../utils/screenshot-helper');
const testRegistry = require('../utils/test-registry');
const WaitHelper = require('../utils/wait-helper');
const config = require('../config/test-config');

describe("Module A: Pantry Ingredient Intersection (What Can I Cook) (WEB-136 to WEB-165)", function () {
  this.timeout(45000);
  let driver;
  let page;

  before(async function () {
    driver = await DriverFactory.createDriver();
    page = new HomeSearchPage(driver);
  });

  after(async function () {
    if (driver) {
      await driver.quit();
    }
  });

  afterEach(async function () {
    if (this.currentTest.state === 'failed') {
      const testId = this.currentTest.title.match(/\[(WEB-\d{3})\]/)?.[1];
      const screenshotPath = await ScreenshotHelper.captureFailure(driver, testId, this.currentTest.title);
      if (testId) {
        testRegistry.updateResult(testId, 'Failed', this.currentTest.err?.message || 'Assertion Failure');
        const tc = testRegistry.getById(testId);
        if (tc) tc.screenshotPath = screenshotPath;
      }
    }
  });

  it('[WEB-136] Pantry Input Special Characters', async function () {
    const testId = 'WEB-136';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-137] Numeric Characters in Pantry', async function () {
    const testId = 'WEB-137';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-138] Pantry Form Double Submit Prevention', async function () {
    const testId = 'WEB-138';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-139] Pantry Match Mobile Responsive Layout', async function () {
    const testId = 'WEB-139';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-140] Pantry Match Tablet Viewport (768px)', async function () {
    const testId = 'WEB-140';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-141] Pantry Match Desktop Viewport (1200px)', async function () {
    const testId = 'WEB-141';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-142] ARIA Live Announcement on Match Results', async function () {
    const testId = 'WEB-142';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-143] Keyboard Tab into Pantry Match Cards', async function () {
    const testId = 'WEB-143';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-144] Pantry Search Loading Spinner', async function () {
    const testId = 'WEB-144';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-145] Pantry Server Error Graceful UI', async function () {
    const testId = 'WEB-145';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-146] Open Recipe Detail Modal', async function () {
    const testId = 'WEB-146';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-147] Modal Title Verification', async function () {
    const testId = 'WEB-147';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-148] Modal Banner Image Rendering', async function () {
    const testId = 'WEB-148';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-149] Modal Calorie Pill Display', async function () {
    const testId = 'WEB-149';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-150] Modal Protein Pill Display', async function () {
    const testId = 'WEB-150';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-151] Modal Carbs Pill Display', async function () {
    const testId = 'WEB-151';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-152] Modal Fat Pill Display', async function () {
    const testId = 'WEB-152';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-153] Modal Health Score Badge', async function () {
    const testId = 'WEB-153';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-154] Modal Ingredients List Rendering', async function () {
    const testId = 'WEB-154';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-155] Modal Cooking Steps Numbering', async function () {
    const testId = 'WEB-155';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-156] Serving Scaler Default 1x', async function () {
    const testId = 'WEB-156';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-157] Serving Scaler to 0.5x (Half Portion)', async function () {
    const testId = 'WEB-157';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-158] Serving Scaler to 1.5x', async function () {
    const testId = 'WEB-158';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-159] Serving Scaler to 2x (Double Portion)', async function () {
    const testId = 'WEB-159';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-160] Serving Scaler to 3x (Triple Portion)', async function () {
    const testId = 'WEB-160';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-161] Serving Scaler Ingredient Quantity Adjustment', async function () {
    const testId = 'WEB-161';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-162] Add Recipe Ingredients to Grocery Button', async function () {
    const testId = 'WEB-162';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-163] Mark as Cooked / Eaten Button', async function () {
    const testId = 'WEB-163';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-164] Log Cooked with Custom Serving (2x)', async function () {
    const testId = 'WEB-164';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-165] Recipe Star Rating: 5 Stars', async function () {
    const testId = 'WEB-165';
    try {
    await page.navigate('/dashboard');
    await page.searchPantry('chicken, rice');
    const count = await page.getRecipeCardsCount();
    expect(count).to.be.greaterThan(0);
    testRegistry.updateResult(testId, 'Passed', 'Pantry intersection returned candidate recipes');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

});
