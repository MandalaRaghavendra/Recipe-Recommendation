// run-all-mobile-tests.js - Master Appium Android Test Runner & Auto-Reporting Engine
const Mocha = require('mocha');
const path = require('path');
const fs = require('fs');
const testRegistry = require('../utils/test-registry');
const ExcelReporter = require('../utils/excel-reporter');
const DeviceHelper = require('../utils/device-helper');
const config = require('../config/mobile-config');

async function run() {
  console.log('========================================================================');
  console.log('          TASTIO ENTERPRISE MOBILE E2E TEST RUNNER (APPIUM)             ');
  console.log('========================================================================');
  console.log(`Target Package:  ${config.capabilities['appium:appPackage']}`);
  console.log(`Activity:        ${config.capabilities['appium:appActivity']}`);
  console.log(`Device Profile:  ${config.capabilities['appium:deviceName']} (Android ${config.capabilities['appium:platformVersion']})`);
  console.log(`Appium Server:   ${config.appium.baseUrl}`);
  console.log(`Test Cases:      300 Scenarios Registered (MOB-001 to MOB-300)`);
  console.log('========================================================================\n');

  const startTime = Date.now();

  // 1. Probe Environment Readiness
  console.log('[Runner] Probing Android Emulator / Physical Device & Appium Server...');
  const env = await DeviceHelper.getEnvironmentStatus();

  console.log(`  - Appium Server (port 4723): ${env.appiumOnline ? 'ONLINE ✅' : 'OFFLINE ❌'}`);
  console.log(`  - ADB Connected Devices:    ${env.deviceConnected ? `CONNECTED (${env.devices.join(', ')}) ✅` : 'NONE DETECTED ❌'}`);
  console.log(`  - Environment Assessment:   ${env.reason}\n`);

  if (!env.isReady) {
    console.log('------------------------------------------------------------------------');
    console.log('[Runner Notice] Live Android execution skipped in accordance with Requirement 10:');
    console.log('  "If an emulator is unavailable, complete the framework and provide exact');
    console.log('   setup instructions instead of repeatedly attempting to launch one."');
    console.log('------------------------------------------------------------------------\n');

    // Generate Master Excel Report with accurate Not Executed status
    console.log('[Runner] Compiling Master Appium Excel Test Report with all 300 test cases...');
    const reporter = new ExcelReporter();
    const reportPath = await reporter.generateReport({ executionDuration: '0s (Awaiting Device)' });

    const summary = testRegistry.getSummary();
    console.log('\n========================================================================');
    console.log('                 FINAL TEST EXECUTION METRICS                           ');
    console.log('========================================================================');
    console.log(`Total Scenarios: ${summary.totalTestCases}`);
    console.log(`Passed:          ${summary.passed}`);
    console.log(`Failed:          ${summary.failed}`);
    console.log(`Blocked:         ${summary.blocked}`);
    console.log(`Not Executed:    ${summary.notExecuted} (Awaiting Android Emulator / Device)`);
    console.log(`Pass Rate:       ${summary.passPercentage}`);
    console.log(`Master Report:   ${reportPath}`);
    console.log('========================================================================\n');

    return { failures: 0, summary, reportPath, isDeviceAvailable: false };
  }

  // 2. Execute via Mocha when device is present
  console.log('[Runner] Environment verified. Queueing 10 test suites for execution...');
  const mocha = new Mocha({
    timeout: 45000,
    reporter: 'spec',
    slow: 5000,
    exit: true
  });

  const testsDir = path.resolve(__dirname, '../tests');
  const files = fs.readdirSync(testsDir).filter(f => f.endsWith('.js')).sort();
  files.forEach(file => mocha.addFile(path.join(testsDir, file)));

  return new Promise((resolve) => {
    mocha.run(async (failures) => {
      const durationMs = Date.now() - startTime;
      const durationSec = (durationMs / 1000).toFixed(1);
      const executionDuration = `${Math.floor(durationSec / 60)}m ${Math.floor(durationSec % 60)}s`;

      console.log('\n[Runner] Generating Master Excel Test Report...');
      const reporter = new ExcelReporter();
      const reportPath = await reporter.generateReport({ executionDuration });

      const summary = testRegistry.getSummary();
      console.log('\n========================================================================');
      console.log('                 FINAL TEST EXECUTION METRICS                           ');
      console.log('========================================================================');
      console.log(`Total Scenarios: ${summary.totalTestCases}`);
      console.log(`Passed:          ${summary.passed}`);
      console.log(`Failed:          ${summary.failed}`);
      console.log(`Blocked:         ${summary.blocked}`);
      console.log(`Not Executed:    ${summary.notExecuted}`);
      console.log(`Pass Rate:       ${summary.passPercentage}`);
      console.log(`Master Report:   ${reportPath}`);
      console.log('========================================================================\n');

      resolve({ failures, summary, reportPath, isDeviceAvailable: true });
    });
  });
}

if (require.main === module) {
  run().catch(err => {
    console.error('[Runner Fatal Error]', err);
    process.exit(1);
  });
}

module.exports = run;

