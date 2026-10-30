// auth-modal-screen.js - User Authentication & Registration Modal Screen Object
const BaseScreen = require('./base-screen');

class AuthModalScreen extends BaseScreen {
  constructor(driver) {
    super(driver);
  }

  async isModalOpen() {
    return await this.isElementVisible(() => this.driver.findByText('Welcome to Tastio'));
  }

  async switchMode(mode = 'signup') {
    if (mode === 'signup') {
      await this.safeTap(() => this.driver.findByText('Sign Up'));
    } else {
      await this.safeTap(() => this.driver.findByText('Login'));
    }
    await this.driver.sleep(300);
  }

  async enterFullName(name) {
    await this.safeType(() => this.driver.findByText('Full Name'), name);
  }

  async enterEmail(email) {
    await this.safeType(() => this.driver.findByText('Email Address'), email);
  }

  async enterPassword(password) {
    await this.safeType(() => this.driver.findByText('Password'), password);
  }

  async submitAuth() {
    try {
      await this.safeTap(() => this.driver.findByText('Sign In'));
    } catch (e) {
      await this.safeTap(() => this.driver.findByText('Create Account'));
    }
  }

  async signOut() {
    await this.safeTap(() => this.driver.findByText('Sign Out'));
  }

  async closeModal() {
    await this.safeTap(() => this.driver.findByText('✕'));
  }
}

module.exports = AuthModalScreen;

