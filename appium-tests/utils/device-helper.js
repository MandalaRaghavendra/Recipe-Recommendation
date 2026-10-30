// device-helper.js - Probing ADB and Appium server readiness
const { execSync } = require('child_process');
const http = require('http');
const config = require('../config/mobile-config');

class DeviceHelper {
  static async checkAppiumServer() {
    return new Promise((resolve) => {
      const req = http.get(`${config.appium.baseUrl}/status`, { timeout: 2000 }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            resolve({ online: true, value: json.value || json });
          } catch (e) {
            resolve({ online: res.statusCode === 200 });
          }
        });
      });
      req.on('error', () => resolve({ online: false }));
      req.on('timeout', () => {
        req.destroy();
        resolve({ online: false });
      });
    });
  }

  static getAdbDevices() {
    try {
      const output = execSync('adb devices', { encoding: 'utf-8', timeout: 4000 });
      const lines = output.split('\n').map(l => l.trim()).filter(Boolean);
      const devices = [];
      for (let i = 1; i < lines.length; i++) {
        const parts = lines[i].split(/\s+/);
        if (parts.length >= 2 && parts[1] === 'device') {
          devices.push(parts[0]);
        }
      }
      return devices;
    } catch (e) {
      return [];
    }
  }

  static async getEnvironmentStatus() {
    const appiumStatus = await this.checkAppiumServer();
    const adbDevices = this.getAdbDevices();

    const isReady = appiumStatus.online && adbDevices.length > 0;
    let reason = 'Ready for execution';

    if (!appiumStatus.online && adbDevices.length === 0) {
      reason = 'Appium server (port 4723) not running AND no Android emulator/device connected via ADB.';
    } else if (!appiumStatus.online) {
      reason = 'Appium server not running on http://127.0.0.1:4723.';
    } else if (adbDevices.length === 0) {
      reason = 'No active Android emulator or physical device detected by ADB.';
    }

    return {
      isReady,
      appiumOnline: appiumStatus.online,
      deviceConnected: adbDevices.length > 0,
      devices: adbDevices,
      reason
    };
  }
}

module.exports = DeviceHelper;

