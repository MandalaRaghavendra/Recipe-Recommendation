// generate-excel-report.js - Standalone trigger for generating the performance Excel report
const PerfExcelReporter = require('../utils/excel-reporter');

async function main() {
  const reporter = new PerfExcelReporter();
  const filePath = await reporter.generateReport();
  console.log(`[Excel] Report generated successfully at: ${filePath}`);
}

main().catch(err => {
  console.error('[Excel Fatal Error]', err);
  process.exit(1);
});

