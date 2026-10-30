const DriverFactory = require('../utils/driver-factory');
const SignupModal = require('../pageobjects/signup-modal');
const { By } = require('selenium-webdriver');

async function test() {
  const driver = await DriverFactory.createDriver();
  try {
    await driver.get('http://127.0.0.1:5000/');
    const signupModal = new SignupModal(driver);
    await signupModal.open();
    await driver.sleep(600);

    const nameInput = await driver.findElement(signupModal.locators.nameInput);
    console.log('Name input displayed?:', await nameInput.isDisplayed());
    await nameInput.sendKeys('Test Chef');
    console.log('Typed Test Chef successfully!');
  } catch (e) {
    console.error('Test error:', e);
  } finally {
    await driver.quit();
  }
}

test();
