// run-all-tests.js - Enterprise Test Runner & Auto-Reporting Engine
const Mocha = require('mocha');
const path = require('path');
const fs = require('fs');
const testRegistry = require('../utils/test-registry');
const ExcelReporter = require('../utils/excel-reporter');
const config = require('../config/test-config');

async function run() {
  console.log('========================================================================');
  console.log('          TASTIO ENTERPRISE WEB E2E TEST RUNNER (SELENIUM)              ');
  console.log('========================================================================');
  console.log(`Target URL:      ${config.baseUrl}`);
  console.log(`Browser:         ${config.browser} (Headless: ${config.headless})`);
  console.log(`Test Cases:      300 Scenarios Registered (WEB-001 to WEB-300)`);
  console.log('========================================================================\n');

  const startTime = Date.now();

  const mocha = new Mocha({
    timeout: 45000,
    reporter: 'spec',
    slow: 5000,
    exit: true
  });

  const testsDir = path.resolve(__dirname, '../tests');
  const files = fs.readdirSync(testsDir).filter(f => f.endsWith('.js'));
  
  // Ensure login-tests.js is first
  files.sort((a, b) => {
    if (a === 'login-tests.js') return -1;
    if (b === 'login-tests.js') return 1;
    return a.localeCompare(b);
  });

  files.forEach(file => {
    mocha.addFile(path.join(testsDir, file));
  });

  console.log(`[Runner] Added ${files.length} test suite files to execution queue:`);
  files.forEach(f => console.log(`  - tests/${f}`));
  console.log('\n[Runner] Initiating WebDriver test execution...\n');

  return new Promise((resolve) => {
    mocha.run(async (failures) => {
      const durationMs = Date.now() - startTime;
      const durationSec = (durationMs / 1000).toFixed(1);
      const executionDuration = `${Math.floor(durationSec / 60)}m ${Math.floor(durationSec % 60)}s`;

      console.log('\n========================================================================');
      console.log('                      EXECUTION COMPLETED                               ');
      console.log('========================================================================');
      console.log(`Duration:        ${executionDuration}`);
      console.log(`Failures:        ${failures}`);

      // Generate the multi-worksheet Excel report
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

      resolve({ failures, summary, reportPath });
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

