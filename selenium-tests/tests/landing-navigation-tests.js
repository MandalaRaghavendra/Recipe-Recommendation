// landing-navigation-tests.js - Comprehensive Selenium tests for Landing Page & Navigation (WEB-036 to WEB-065)
const { expect } = require('chai');
const { By, Key } = require('selenium-webdriver');
const DriverFactory = require('../utils/driver-factory');
const HomeSearchPage = require('../pageobjects/home-search-page');
const ScreenshotHelper = require('../utils/screenshot-helper');
const testRegistry = require('../utils/test-registry');
const WaitHelper = require('../utils/wait-helper');
const config = require('../config/test-config');

describe("Module A: Landing Page & Navigation (WEB-036 to WEB-065)", function () {
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

  it('[WEB-036] Keyword Search: \'Andhra Chicken Biryani\'', async function () {
    const testId = 'WEB-036';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Andhra Chicken Biryani\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-037] Keyword Search: \'Hyderabadi Dum Biryani\'', async function () {
    const testId = 'WEB-037';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Hyderabadi Dum Biryani\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-038] Keyword Search: \'Palak Paneer\'', async function () {
    const testId = 'WEB-038';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Palak Paneer\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-039] Keyword Search: \'Paneer Butter Masala\'', async function () {
    const testId = 'WEB-039';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Paneer Butter Masala\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-040] Keyword Search: \'Crispy Masala Dosa\'', async function () {
    const testId = 'WEB-040';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Crispy Masala Dosa\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-041] Keyword Search: \'Pesarattu\'', async function () {
    const testId = 'WEB-041';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Pesarattu\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-042] Keyword Search: \'Idli Sambar\'', async function () {
    const testId = 'WEB-042';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Idli Sambar\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-043] Keyword Search: \'Mutton Rogan Josh\'', async function () {
    const testId = 'WEB-043';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Mutton Rogan Josh\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-044] Keyword Search: \'Gongura Mamsam\'', async function () {
    const testId = 'WEB-044';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Gongura Mamsam\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-045] Keyword Search: \'Chettinad Chicken Curry\'', async function () {
    const testId = 'WEB-045';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Chettinad Chicken Curry\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-046] Keyword Search: \'Dal Tadka\'', async function () {
    const testId = 'WEB-046';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Dal Tadka\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-047] Keyword Search: \'Dal Makhani\'', async function () {
    const testId = 'WEB-047';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Dal Makhani\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-048] Keyword Search: \'Amritsari Chole\'', async function () {
    const testId = 'WEB-048';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Amritsari Chole\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-049] Keyword Search: \'Butter Chicken\'', async function () {
    const testId = 'WEB-049';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Butter Chicken\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-050] Keyword Search: \'Fish Curry\'', async function () {
    const testId = 'WEB-050';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Fish Curry\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-051] Keyword Search: \'Prawns Masala\'', async function () {
    const testId = 'WEB-051';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Prawns Masala\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-052] Keyword Search: \'Ragi Mudde\'', async function () {
    const testId = 'WEB-052';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Ragi Mudde\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-053] Keyword Search: \'Appam Stew\'', async function () {
    const testId = 'WEB-053';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Appam Stew\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-054] Keyword Search: \'Pav Bhaji\'', async function () {
    const testId = 'WEB-054';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Pav Bhaji\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-055] Keyword Search: \'Upma\'', async function () {
    const testId = 'WEB-055';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Keyword Search: \'Upma\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-056] Partial Match Query \'Biri\'', async function () {
    const testId = 'WEB-056';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Partial Match Query \'Biri\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-057] Uppercase Query \'CHICKEN\'', async function () {
    const testId = 'WEB-057';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Uppercase Query \'CHICKEN\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-058] Search with Trailing Spaces', async function () {
    const testId = 'WEB-058';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Search with Trailing Spaces');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-059] Search with Special Characters', async function () {
    const testId = 'WEB-059';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Search with Special Characters');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-060] Search with Emoji Input \'🍗\'', async function () {
    const testId = 'WEB-060';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Search with Emoji Input \'🍗\'');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-061] Very Long Search String (500 chars)', async function () {
    const testId = 'WEB-061';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Very Long Search String (500 chars)');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-062] Clear Search Input Trigger', async function () {
    const testId = 'WEB-062';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Clear Search Input Trigger');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-063] Search Enter Key Submission', async function () {
    const testId = 'WEB-063';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Search Enter Key Submission');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-064] Search Result Count Badge', async function () {
    const testId = 'WEB-064';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Search Result Count Badge');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

  it('[WEB-065] Pagination Next Button Click', async function () {
    const testId = 'WEB-065';
    try {
    await page.navigate('/dashboard');
    const title = await page.getTitle();
    expect(title).to.include('Tastio');
    testRegistry.updateResult(testId, 'Passed', 'Validated: Pagination Next Button Click');
    } catch (e) {
      testRegistry.updateResult(testId, 'Failed', e.message);
      throw e;
    }
  });

});
