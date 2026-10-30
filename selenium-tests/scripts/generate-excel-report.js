// generate-excel-report.js - CLI runner to generate selenium-test-report.xlsx
const ExcelReporter = require('../utils/excel-reporter');

async function main() {
  console.log('[Runner] Generating selenium-test-report.xlsx...');
  const reporter = new ExcelReporter();
  const filePath = await reporter.generateReport();
  console.log(`[Runner] Report generated at: ${filePath}`);
}

main().catch(err => {
  console.error('[Runner] Error generating Excel report:', err);
  process.exit(1);
});

