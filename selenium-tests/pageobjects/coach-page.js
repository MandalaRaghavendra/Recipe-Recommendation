// coach-page.js - Page object for AI Nutrition Coach Chat
const { By } = require('selenium-webdriver');
const BasePage = require('./base-page');
const WaitHelper = require('../utils/wait-helper');

class CoachPage extends BasePage {
  constructor(driver) {
    super(driver);
    this.locators = {
      chatStream: By.id('chatStream'),
      userInput: By.id('userInput'),
      sendBtn: By.id('sendBtn'),
      messageBubbles: By.css('.chat-bubble, #chatStream .card, #chatStream > div'),
      goalBadge: By.id('goalBadge')
    };
  }

  async open() {
    await this.navigate('/coach');
    await WaitHelper.waitForElementPresent(this.driver, this.locators.chatStream, 10000);
  }

  async sendMessage(message) {
    await WaitHelper.safeType(this.driver, this.locators.userInput, message);
    await WaitHelper.safeClick(this.driver, this.locators.sendBtn);
  }

  async getMessagesCount() {
    const bubbles = await this.driver.findElements(this.locators.messageBubbles);
    return bubbles.length;
  }
}

module.exports = CoachPage;

