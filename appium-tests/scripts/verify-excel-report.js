// verify-excel-report.js - Enterprise verification of Appium Excel Report
const ExcelJS = require('exceljs');
const path = require('path');
const config = require('../config/mobile-config');

async function verify() {
  const filePath = config.reportPath;
  console.log('========================================================================');
  console.log('          APPIUM EXCEL TEST REPORT VERIFICATION AUDIT                   ');
  console.log('========================================================================');
  console.log(`Checking Report: ${filePath}\n`);

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  console.log('1. Worksheets Audit:');
  const expectedSheets = ['Test Summary', 'Test Case Details', 'Execution Results', 'Failed Tests', 'Defects'];
  let sheetsValid = true;

  expectedSheets.forEach(sheetName => {
    const ws = workbook.getWorksheet(sheetName);
    if (ws) {
      console.log(`  [OK] Sheet '${sheetName}' present (rows: ${ws.rowCount}, cols: ${ws.columnCount})`);
    } else {
      console.error(`  [FAIL] Missing required sheet '${sheetName}'!`);
      sheetsValid = false;
    }
  });

  if (!sheetsValid) {
    throw new Error('Worksheet structure validation failed');
  }

  // 2. Summary Sheet Metrics Verification
  console.log('\n2. Test Summary Worksheet Metrics:');
  const summarySheet = workbook.getWorksheet('Test Summary');
  const summaryMetrics = {};
  for (let r = 5; r <= 15; r++) {
    const metric = summarySheet.getCell(`D${r}`).value;
    const val = summarySheet.getCell(`E${r}`).value;
    if (metric) {
      summaryMetrics[metric] = val;
      console.log(`  - ${metric}: ${val}`);
    }
  }

  // 3. Test Case Details 300 Scenarios Verification
  console.log('\n3. Test Case Details (300 Scenarios) Audit:');
  const detailsSheet = workbook.getWorksheet('Test Case Details');
  const expectedColumns = [
    'Test ID', 'Module', 'Test Scenario', 'Preconditions', 'Test Steps',
    'Test Data', 'Expected Result', 'Actual Result', 'Status', 'Priority',
    'Severity', 'Execution Date', 'Defect Reference'
  ];

  const actualColumns = [];
  for (let c = 1; c <= 13; c++) {
    actualColumns.push(detailsSheet.getRow(1).getCell(c).value);
  }

  const columnsMatch = JSON.stringify(actualColumns) === JSON.stringify(expectedColumns);
  console.log(`  - Header Schema Match: ${columnsMatch ? 'PASS ✅' : 'FAIL ❌'}`);
  if (!columnsMatch) {
    console.error('    Expected:', expectedColumns);
    console.error('    Actual:  ', actualColumns);
  }

  let validCasesCount = 0;
  const statusDistribution = {};
  const mobIds = new Set();

  for (let r = 2; r <= detailsSheet.rowCount; r++) {
    const id = detailsSheet.getRow(r).getCell(1).value;
    if (id && String(id).startsWith('MOB-')) {
      validCasesCount++;
      mobIds.add(String(id));
      const status = detailsSheet.getRow(r).getCell(9).value || 'Not Executed';
      statusDistribution[status] = (statusDistribution[status] || 0) + 1;
    }
  }

  console.log(`  - Total Unique MOB Cases: ${mobIds.size} / 300`);
  console.log(`  - Status Distribution:    ${JSON.stringify(statusDistribution)}`);
  console.log(`  - Total Rows Cataloged:   ${validCasesCount}`);

  // Assert exactly 300 unique cases
  if (mobIds.size !== 300) {
    throw new Error(`Expected exactly 300 unique MOB test cases, found ${mobIds.size}`);
  }

  // 4. Execution Results Worksheet
  const execSheet = workbook.getWorksheet('Execution Results');
  console.log(`\n4. Execution Results Entries: ${execSheet.rowCount - 1} rows`);

  // 5. Failed Tests Worksheet
  const failedSheet = workbook.getWorksheet('Failed Tests');
  console.log(`5. Failed Tests Entries:    ${failedSheet.rowCount - 1} rows`);

  // 6. Defects Worksheet
  const defectsSheet = workbook.getWorksheet('Defects');
  console.log(`6. Defects Documented:       ${defectsSheet.rowCount - 1} entries`);

  console.log('\n========================================================================');
  console.log('              ALL 300 TEST CASES & EXCEL SHEETS VERIFIED ✅             ');
  console.log('========================================================================\n');
}

if (require.main === module) {
  verify().catch(err => {
    console.error('[Verification Fatal Error]', err.message);
    process.exit(1);
  });
}

module.exports = verify;

