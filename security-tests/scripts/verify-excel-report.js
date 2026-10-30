// verify-excel-report.js - Enterprise Audit of Module D Security Excel Reports
const ExcelJS = require('exceljs');
const path = require('path');
const config = require('../config/security-config');

async function verify() {
  const filePath = config.paths.mainExcelReport;
  console.log('========================================================================');
  console.log('         SECURITY ASSESSMENT EXCEL REPORT ENTERPRISE AUDIT              ');
  console.log('========================================================================');
  console.log(`Auditing Main Report: ${filePath}\n`);

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  console.log('1. Worksheets Audit:');
  const expectedSheets = [
    'Test Summary',
    'Test Case Details',
    'Execution Results',
    'Failed Tests',
    'Security Findings'
  ];

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
    throw new Error('Worksheet validation failed: One or more required sheets missing.');
  }

  // 2. Summary Sheet Metrics Verification
  console.log('\n2. Test Summary Worksheet Metrics:');
  const summarySheet = workbook.getWorksheet('Test Summary');
  const summaryMetrics = {};
  for (let r = 5; r <= 19; r++) {
    const metric = summarySheet.getCell(`E${r}`).value;
    const val = summarySheet.getCell(`F${r}`).value;
    if (metric) {
      summaryMetrics[metric] = val;
      console.log(`  - ${metric}: ${val}`);
    }
  }

  // 3. Test Case Details 300 Scenarios Verification
  console.log('\n3. Test Case Details (300 Scenarios) Audit:');
  const detailsSheet = workbook.getWorksheet('Test Case Details');
  const expectedColumns = [
    'Test ID', 'Domain', 'Vulnerability Category', 'OWASP Ref',
    'Attack Vector / Test Procedure', 'Expected Defense & Assertion',
    'Actual Audit Result', 'Status', 'Severity', 'Priority',
    'Finding Reference', 'Audit Date', 'Remediation Summary'
  ];

  const actualHeaders = [];
  const headerRow = detailsSheet.getRow(1);
  headerRow.eachCell((cell) => actualHeaders.push(cell.value));

  const schemaMatch = expectedColumns.every((col, idx) => actualHeaders[idx] === col);
  console.log(`  - Header Schema Match: ${schemaMatch ? 'PASS ✅' : 'FAIL ❌'}`);

  const testIdsInSheet = new Set();
  const statusCounts = {};

  for (let r = 2; r <= detailsSheet.rowCount; r++) {
    const row = detailsSheet.getRow(r);
    const tid = row.getCell(1).value;
    const status = row.getCell(8).value;

    if (tid && typeof tid === 'string' && tid.startsWith('SEC-')) {
      testIdsInSheet.add(tid);
      statusCounts[status] = (statusCounts[status] || 0) + 1;
    }
  }

  console.log(`  - Total Unique SEC Cases: ${testIdsInSheet.size} / 300`);
  console.log(`  - Status Distribution:    ${JSON.stringify(statusCounts)}`);
  console.log(`  - Total Rows Cataloged:   ${testIdsInSheet.size}`);

  if (testIdsInSheet.size !== 300) {
    throw new Error(`Catalog mismatch: Expected 300 unique SEC test cases, found ${testIdsInSheet.size}`);
  }

  // Verify continuous sequence from SEC-001 to SEC-300
  let missingIds = [];
  for (let i = 1; i <= 300; i++) {
    const expectedId = `SEC-${String(i).padStart(3, '0')}`;
    if (!testIdsInSheet.has(expectedId)) {
      missingIds.push(expectedId);
    }
  }

  if (missingIds.length > 0) {
    throw new Error(`Missing expected test IDs: ${missingIds.join(', ')}`);
  }
  console.log('  - Sequence Check (SEC-001 to SEC-300): 100% COMPLETE & CONTINUOUS ✅');

  // 4. Failed Tests & Findings Sheets Check
  console.log('\n4. Failed Tests & Security Findings Audit:');
  const failedSheet = workbook.getWorksheet('Failed Tests');
  const findingsSheet = workbook.getWorksheet('Security Findings');
  console.log(`  - Failed Tests Cataloged:     ${failedSheet.rowCount - 1} test scenarios`);
  console.log(`  - Master Security Findings:    ${findingsSheet.rowCount - 1} vulnerability entries`);

  // 5. Check Additional Workbooks
  console.log('\n5. Additional Workbooks Verification:');
  const findingsWb = new ExcelJS.Workbook();
  await findingsWb.xlsx.readFile(config.paths.findingsExcel);
  console.log(`  - findings.xlsx:            ${findingsWb.worksheets[0].name} (${findingsWb.worksheets[0].rowCount} rows) [OK]`);

  const invWb = new ExcelJS.Workbook();
  await invWb.xlsx.readFile(config.paths.inventoryExcel);
  console.log(`  - endpoint-inventory.xlsx:  ${invWb.worksheets[0].name} (${invWb.worksheets[0].rowCount} rows) [OK]`);

  console.log('\n========================================================================');
  console.log('              ALL 300 TEST CASES & EXCEL WORKBOOKS VERIFIED ✅          ');
  console.log('========================================================================\n');
}

verify().catch(err => {
  console.error('[Audit Error]', err.message);
  process.exit(1);
});

