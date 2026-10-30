const ExcelJS = require('exceljs');
const path = require('path');

async function verify() {
  const filePath = path.join(__dirname, '../reports/selenium-test-report.xlsx');
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  console.log('Worksheets in Excel:');
  workbook.worksheets.forEach(ws => {
    console.log(` - '${ws.name}' (rows: ${ws.rowCount}, cols: ${ws.columnCount})`);
  });

  const expectedSheets = ['Test Summary', 'Test Case Details', 'Execution Results', 'Failed Tests', 'Defects'];
  expectedSheets.forEach(s => {
    const ws = workbook.getWorksheet(s);
    if (ws) {
      console.log(`[OK] Sheet '${s}' verified.`);
    } else {
      console.log(`[FAIL] Sheet '${s}' missing!`);
    }
  });

  // 1. Verify Test Summary
  console.log('\n--- 1. Test Summary Worksheet ---');
  const summarySheet = workbook.getWorksheet('Test Summary');
  for (let r = 4; r <= 15; r++) {
    const metric = summarySheet.getCell(`D${r}`).value;
    const val = summarySheet.getCell(`E${r}`).value;
    if (metric) {
      console.log(`  ${metric}: ${val}`);
    }
  }

  // 2. Verify Test Case Details
  console.log('\n--- 2. Test Case Details Worksheet ---');
  const detailsSheet = workbook.getWorksheet('Test Case Details');
  const headers = [];
  for (let c = 1; c <= 13; c++) {
    headers.push(detailsSheet.getRow(1).getCell(c).value);
  }
  console.log('  Columns:', headers.join(' | '));

  let totalCases = 0;
  const statusCounts = {};
  for (let r = 2; r <= detailsSheet.rowCount; r++) {
    const id = detailsSheet.getRow(r).getCell(1).value;
    if (id && String(id).startsWith('WEB-')) {
      totalCases++;
      const status = detailsSheet.getRow(r).getCell(9).value;
      statusCounts[status] = (statusCounts[status] || 0) + 1;
    }
  }
  console.log(`  Total Valid Scenarios: ${totalCases}`);
  console.log('  Status Distribution:', JSON.stringify(statusCounts));

  // 3. Verify Execution Results
  console.log('\n--- 3. Execution Results Worksheet ---');
  const execSheet = workbook.getWorksheet('Execution Results');
  console.log(`  Execution Results Entry Count: ${execSheet.rowCount - 1}`);

  // 4. Verify Failed Tests
  console.log('\n--- 4. Failed Tests Worksheet ---');
  const failedSheet = workbook.getWorksheet('Failed Tests');
  console.log(`  Failed Tests Entry Count: ${failedSheet.rowCount - 1}`);

  // 5. Verify Defects
  console.log('\n--- 5. Defects Worksheet ---');
  const defectsSheet = workbook.getWorksheet('Defects');
  console.log(`  Defects Entry Count: ${defectsSheet.rowCount - 1}`);
}

verify().catch(console.error);

