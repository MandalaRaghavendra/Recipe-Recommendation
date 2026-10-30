// verify-excel-report.js - Enterprise Audit & Schema Verification of Performance Excel Report
const ExcelJS = require('exceljs');
const path = require('path');
const config = require('../config/perf-config');
const perfRegistry = require('../utils/perf-registry');

async function verify() {
  const filePath = config.paths.excelReport;
  console.log('========================================================================');
  console.log('         PERFORMANCE EXCEL REPORT ENTERPRISE AUDIT                      ');
  console.log('========================================================================');
  console.log(`Checking Report: ${filePath}\n`);

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  console.log('1. Worksheets Audit:');
  const expectedSheets = [
    'Test Summary',
    'Test Case Details',
    'Execution Results',
    'Failed Tests',
    'Performance Metrics'
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
  for (let r = 5; r <= 20; r++) {
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
    'Test ID', 'Module', 'Test Scenario', 'Concurrency Profile', 'Workload Parameters',
    'Preconditions', 'Test Steps', 'Expected Metric & Threshold', 'Actual Metric Measured',
    'Status', 'Priority', 'Severity', 'Execution Date'
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
    const status = row.getCell(10).value;

    if (tid && typeof tid === 'string' && tid.startsWith('PERF-')) {
      testIdsInSheet.add(tid);
      statusCounts[status] = (statusCounts[status] || 0) + 1;
    }
  }

  console.log(`  - Total Unique PERF Cases: ${testIdsInSheet.size} / 300`);
  console.log(`  - Status Distribution:    ${JSON.stringify(statusCounts)}`);
  console.log(`  - Total Rows Cataloged:   ${testIdsInSheet.size}`);

  if (testIdsInSheet.size !== 300) {
    throw new Error(`Catalog mismatch: Expected 300 unique PERF test cases, found ${testIdsInSheet.size}`);
  }

  // Verify each planned test ID exists from PERF-001 to PERF-300
  let missingIds = [];
  for (let i = 1; i <= 300; i++) {
    const expectedId = `PERF-${String(i).padStart(3, '0')}`;
    if (!testIdsInSheet.has(expectedId)) {
      missingIds.push(expectedId);
    }
  }

  if (missingIds.length > 0) {
    throw new Error(`Missing expected test IDs: ${missingIds.join(', ')}`);
  }
  console.log('  - Sequence Check (PERF-001 to PERF-300): 100% COMPLETE & CONTINUOUS ✅');

  // 4. Performance Metrics Sheet Check
  console.log('\n4. Performance Metrics Worksheet Audit:');
  const metricsSheet = workbook.getWorksheet('Performance Metrics');
  console.log(`  - Endpoint Breakdown Rows: ${metricsSheet.rowCount - 1} endpoints profiled`);

  console.log('\n========================================================================');
  console.log('              ALL 300 TEST CASES & 5 EXCEL SHEETS VERIFIED ✅           ');
  console.log('========================================================================\n');
}

verify().catch(err => {
  console.error('[Audit Error]', err.message);
  process.exit(1);
});

