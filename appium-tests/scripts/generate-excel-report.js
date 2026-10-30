// generate-excel-report.js - Manual / CI trigger to build Excel report
const ExcelReporter = require('../utils/excel-reporter');

async function main() {
  const reporter = new ExcelReporter();
  const filePath = await reporter.generateReport();
  console.log(`[Excel] Report generated successfully at: ${filePath}`);
}

main().catch(err => {
  console.error('[Excel Fatal Error]', err);
  process.exit(1);
});

