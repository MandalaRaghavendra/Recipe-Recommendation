// excel-reporter.js - Enterprise multi-worksheet Excel report generator using ExcelJS
const ExcelJS = require('exceljs');
const path = require('path');
const fs = require('fs');
const testRegistry = require('./test-registry');
const config = require('../config/test-config');

class ExcelReporter {
  constructor(outputPath) {
    this.outputPath = outputPath || path.join(config.reportsDir, 'selenium-test-report.xlsx');
  }

  async generateReport(executionStats = {}) {
    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'Tastio Senior QA Automation Suite';
    workbook.lastModifiedBy = 'Tastio Selenium E2E Harness';
    workbook.created = new Date();
    workbook.modified = new Date();

    const summaryData = testRegistry.getSummary();
    if (executionStats.executionDuration) {
      summaryData.executionDuration = executionStats.executionDuration;
    }

    const testCases = testRegistry.getAll();
    const executedCases = testCases.filter(tc => tc.status !== 'Not Executed');
    const failedCases = testCases.filter(tc => tc.status === 'Failed');

    // 1. Worksheet: Test Summary
    this.buildSummarySheet(workbook, summaryData, executionStats);

    // 2. Worksheet: Test Case Details (300 cases)
    this.buildDetailsSheet(workbook, testCases);

    // 3. Worksheet: Execution Results
    this.buildExecutionResultsSheet(workbook, executedCases);

    // 4. Worksheet: Failed Tests
    this.buildFailedTestsSheet(workbook, failedCases);

    // 5. Worksheet: Defects
    this.buildDefectsSheet(workbook, failedCases);

    // Ensure directory exists
    const dir = path.dirname(this.outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    await workbook.xlsx.writeFile(this.outputPath);
    console.log(`[ExcelReporter] Master test report successfully written to: ${this.outputPath}`);
    return this.outputPath;
  }

  buildSummarySheet(workbook, summary, executionStats) {
    const sheet = workbook.addWorksheet('Test Summary', {
      views: [{ showGridLines: true }]
    });

    // Title Banner
    sheet.mergeCells('A1:G2');
    const titleCell = sheet.getCell('A1');
    titleCell.value = 'TASTIO RECIPE RECOMMENDATION SYSTEM - E2E AUTOMATION TEST REPORT';
    titleCell.font = { name: 'Calibri', size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
    titleCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF7B2C3F' } }; // Burgundy theme
    titleCell.alignment = { vertical: 'middle', horizontal: 'center' };

    // Metadata section
    sheet.getCell('A4').value = 'Target Environment:';
    sheet.getCell('B4').value = config.baseUrl;
    sheet.getCell('A5').value = 'Browser Engine:';
    sheet.getCell('B5').value = `${config.browser.toUpperCase()} (Headless: ${config.headless})`;
    sheet.getCell('A6').value = 'Test Execution Date:';
    sheet.getCell('B6').value = new Date().toLocaleString();
    sheet.getCell('A7').value = 'Test Runner & Framework:';
    sheet.getCell('B7').value = 'Selenium WebDriver 4.x + Mocha BDD + Chai';

    ['A4', 'A5', 'A6', 'A7'].forEach(cell => {
      sheet.getCell(cell).font = { bold: true, color: { argb: 'FF334155' } };
    });

    // KPI Summary Table
    sheet.getCell('D4').value = 'Execution Metric';
    sheet.getCell('E4').value = 'Value';
    sheet.getCell('D4').font = { bold: true, color: { argb: 'FFFFFFFF' } };
    sheet.getCell('D4').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1E293B' } };
    sheet.getCell('E4').font = { bold: true, color: { argb: 'FFFFFFFF' } };
    sheet.getCell('E4').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1E293B' } };

    const metrics = [
      ['Total Test Cases', summary.totalTestCases, 'FF0F172A'],
      ['Passed', summary.passed, 'FF16A34A'],
      ['Failed', summary.failed, 'FFDC2626'],
      ['Blocked', summary.blocked, 'FFD97706'],
      ['Not Executed', summary.notExecuted, 'FF64748B'],
      ['Pass Percentage', summary.passPercentage, 'FF2563EB'],
      ['Execution Duration', summary.executionDuration, 'FF475569']
    ];

    metrics.forEach((m, idx) => {
      const row = 5 + idx;
      sheet.getCell(`D${row}`).value = m[0];
      sheet.getCell(`D${row}`).font = { bold: true };
      sheet.getCell(`E${row}`).value = m[1];
      sheet.getCell(`E${row}`).font = { bold: true, color: { argb: m[2] } };
      sheet.getCell(`E${row}`).alignment = { horizontal: 'center' };
    });

    // Module breakdown table
    sheet.getCell('A13').value = 'Module Breakdown';
    sheet.getCell('A13').font = { size: 13, bold: true, color: { argb: 'FF1E293B' } };

    const headers = ['Module Name', 'Total', 'Passed', 'Failed', 'Blocked', 'Not Executed', 'Compliance'];
    headers.forEach((h, i) => {
      const colLetter = String.fromCharCode(65 + i);
      const cell = sheet.getCell(`${colLetter}14`);
      cell.value = h;
      cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
      cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF475569' } };
      cell.alignment = { horizontal: 'center' };
    });

    const modules = [
      'Authentication & Session Management',
      'Landing Page & Navigation',
      'Recipe Discovery & Multi-Param Filter Matrix',
      'AI Vector & Keyword Search',
      "Pantry Ingredient Intersection ('What Can I Cook')",
      'Recipe Detail Modal & Servings Scaler',
      '7-Day AI Meal Plan Grid & Slot Swapping',
      'Categorized Smart Grocery List & Compilation',
      'AI Nutrition Coach Web Chat Assistant',
      'Food Scanner Drag-and-Drop Vision Analysis',
      'User Profile Biometrics & Analytics',
      'Accessibility, Responsive Viewports & Layout'
    ];

    modules.forEach((mod, idx) => {
      const r = 15 + idx;
      const allModCases = testRegistry.getAll().filter(tc => tc.module === mod);
      const modPassed = allModCases.filter(tc => tc.status === 'Passed').length;
      const modFailed = allModCases.filter(tc => tc.status === 'Failed').length;
      const modBlocked = allModCases.filter(tc => tc.status === 'Blocked').length;
      const modNotExec = allModCases.filter(tc => tc.status === 'Not Executed').length;
      const modPct = allModCases.length > 0 ? `${((modPassed / allModCases.length) * 100).toFixed(1)}%` : '0%';

      sheet.getCell(`A${r}`).value = mod;
      sheet.getCell(`B${r}`).value = allModCases.length;
      sheet.getCell(`C${r}`).value = modPassed;
      sheet.getCell(`D${r}`).value = modFailed;
      sheet.getCell(`E${r}`).value = modBlocked;
      sheet.getCell(`F${r}`).value = modNotExec;
      sheet.getCell(`G${r}`).value = modPct;

      ['B', 'C', 'D', 'E', 'F', 'G'].forEach(col => {
        sheet.getCell(`${col}${r}`).alignment = { horizontal: 'center' };
      });
    });

    sheet.columns = [
      { width: 44 },
      { width: 12 },
      { width: 12 },
      { width: 12 },
      { width: 12 },
      { width: 16 },
      { width: 16 }
    ];
  }

  buildDetailsSheet(workbook, testCases) {
    const sheet = workbook.addWorksheet('Test Case Details', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const columns = [
      { header: 'Test ID', key: 'testId', width: 14 },
      { header: 'Module', key: 'module', width: 34 },
      { header: 'Test Scenario', key: 'testScenario', width: 38 },
      { header: 'Preconditions', key: 'preconditions', width: 32 },
      { header: 'Test Steps', key: 'testSteps', width: 45 },
      { header: 'Test Data', key: 'testData', width: 28 },
      { header: 'Expected Result', key: 'expectedResult', width: 45 },
      { header: 'Actual Result', key: 'actualResult', width: 45 },
      { header: 'Status', key: 'status', width: 16 },
      { header: 'Priority', key: 'priority', width: 14 },
      { header: 'Severity', key: 'severity', width: 14 },
      { header: 'Execution Date', key: 'executionDate', width: 22 },
      { header: 'Defect Reference', key: 'defectReference', width: 18 }
    ];

    sheet.columns = columns;

    // Header formatting
    const headerRow = sheet.getRow(1);
    headerRow.font = { name: 'Calibri', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF7B2C3F' } };
    headerRow.alignment = { vertical: 'middle', horizontal: 'center', wrapText: true };
    headerRow.height = 28;

    testCases.forEach((tc, index) => {
      const row = sheet.addRow({
        testId: tc.testId,
        module: tc.module,
        testScenario: tc.testScenario,
        preconditions: tc.preconditions,
        testSteps: tc.testSteps,
        testData: tc.testData,
        expectedResult: tc.expectedResult,
        actualResult: tc.actualResult || 'Not Executed',
        status: tc.status,
        priority: tc.priority,
        severity: tc.severity,
        executionDate: tc.executionDate ? new Date(tc.executionDate).toLocaleString() : 'Pending Execution',
        defectReference: tc.defectReference || 'N/A'
      });

      row.height = 24;
      row.alignment = { vertical: 'middle', wrapText: true };

      // Zebra striping
      if (index % 2 === 1) {
        row.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF8FAFC' } };
      }

      // Status pill coloring
      const statusCell = row.getCell('status');
      statusCell.font = { bold: true };
      statusCell.alignment = { horizontal: 'center', vertical: 'middle' };

      if (tc.status === 'Passed') {
        statusCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDCFCE7' } }; // Light green
        statusCell.font = { bold: true, color: { argb: 'FF166534' } };
      } else if (tc.status === 'Failed') {
        statusCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFEE2E2' } }; // Light red
        statusCell.font = { bold: true, color: { argb: 'FF991B1B' } };
      } else if (tc.status === 'Blocked') {
        statusCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFEF3C7' } }; // Light amber
        statusCell.font = { bold: true, color: { argb: 'FF92400E' } };
      } else {
        statusCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF1F5F9' } }; // Slate gray
        statusCell.font = { bold: true, color: { argb: 'FF475569' } };
      }

      row.getCell('testId').alignment = { horizontal: 'center', vertical: 'middle' };
      row.getCell('priority').alignment = { horizontal: 'center', vertical: 'middle' };
      row.getCell('severity').alignment = { horizontal: 'center', vertical: 'middle' };
      row.getCell('defectReference').alignment = { horizontal: 'center', vertical: 'middle' };
    });
  }

  buildExecutionResultsSheet(workbook, executedCases) {
    const sheet = workbook.addWorksheet('Execution Results', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const columns = [
      { header: 'Test ID', key: 'testId', width: 14 },
      { header: 'Test Scenario', key: 'testScenario', width: 38 },
      { header: 'Module', key: 'module', width: 32 },
      { header: 'Status', key: 'status', width: 16 },
      { header: 'Duration (ms)', key: 'duration', width: 16 },
      { header: 'Execution Timestamp', key: 'timestamp', width: 24 },
      { header: 'Actual Output & Diagnostics', key: 'actualResult', width: 50 }
    ];

    sheet.columns = columns;
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1E293B' } };
    headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
    headerRow.height = 26;

    if (executedCases.length === 0) {
      const row = sheet.addRow({
        testId: 'INFO',
        testScenario: 'No automated tests have been executed in this reporting run yet.',
        module: 'N/A',
        status: 'Not Executed',
        duration: 0,
        timestamp: new Date().toLocaleString(),
        actualResult: 'Execute `npm test` to populate live execution results.'
      });
      row.alignment = { vertical: 'middle' };
    } else {
      executedCases.forEach(tc => {
        const row = sheet.addRow({
          testId: tc.testId,
          testScenario: tc.testScenario,
          module: tc.module,
          status: tc.status,
          duration: tc.duration || 150,
          timestamp: tc.executionDate ? new Date(tc.executionDate).toLocaleString() : 'N/A',
          actualResult: tc.actualResult
        });
        row.alignment = { vertical: 'middle' };
        row.getCell('testId').alignment = { horizontal: 'center' };
        row.getCell('status').alignment = { horizontal: 'center' };
        row.getCell('duration').alignment = { horizontal: 'center' };
      });
    }
  }

  buildFailedTestsSheet(workbook, failedCases) {
    const sheet = workbook.addWorksheet('Failed Tests', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const columns = [
      { header: 'Test ID', key: 'testId', width: 14 },
      { header: 'Module', key: 'module', width: 32 },
      { header: 'Test Scenario', key: 'testScenario', width: 38 },
      { header: 'Expected Outcome', key: 'expectedResult', width: 40 },
      { header: 'Failure Reason & Exception Details', key: 'failureDetails', width: 55 },
      { header: 'Screenshot Artifact', key: 'screenshot', width: 35 },
      { header: 'Defect Reference', key: 'defectReference', width: 18 }
    ];

    sheet.columns = columns;
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDC2626' } }; // Danger red
    headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
    headerRow.height = 26;

    if (failedCases.length === 0) {
      const row = sheet.addRow({
        testId: 'NONE',
        module: 'All Modules',
        testScenario: 'Zero test failures recorded in the active execution batch.',
        expectedResult: 'N/A',
        failureDetails: 'All executed test assertions succeeded.',
        screenshot: 'N/A',
        defectReference: 'N/A'
      });
      row.alignment = { vertical: 'middle' };
    } else {
      failedCases.forEach(tc => {
        const row = sheet.addRow({
          testId: tc.testId,
          module: tc.module,
          testScenario: tc.testScenario,
          expectedResult: tc.expectedResult,
          failureDetails: tc.actualResult || 'Assertion Error or Element Timeout',
          screenshot: tc.screenshotPath || 'reports/screenshots/default.png',
          defectReference: tc.defectReference || 'DEF-TBD'
        });
        row.alignment = { vertical: 'middle', wrapText: true };
        row.getCell('testId').alignment = { horizontal: 'center' };
        row.getCell('defectReference').alignment = { horizontal: 'center' };
      });
    }
  }

  buildDefectsSheet(workbook, failedCases) {
    const sheet = workbook.addWorksheet('Defects', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const columns = [
      { header: 'Defect ID', key: 'defectId', width: 14 },
      { header: 'Defect Summary', key: 'summary', width: 40 },
      { header: 'Severity', key: 'severity', width: 14 },
      { header: 'Impacted Module', key: 'module', width: 30 },
      { header: 'Steps to Reproduce', key: 'steps', width: 45 },
      { header: 'Expected vs Actual', key: 'expectedVsActual', width: 45 },
      { header: 'Remediation Status', key: 'status', width: 20 }
    ];

    sheet.columns = columns;
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF92400E' } }; // Amber
    headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
    headerRow.height = 26;

    // Discovered baseline defects from TESTING-PLAN.md
    const baselineDefects = [
      {
        defectId: 'DEF-001',
        summary: 'Missing Anti-CSRF Tokens on Web Form Submissions',
        severity: 'Critical',
        module: 'Authentication & Search Forms',
        steps: 'Submit POST request to /login, /signup, or /recommend from third-party origin',
        expectedVsActual: 'Expected CSRF validation failure; Actual request accepted without CSRF token',
        status: 'Open (Tracked in Test Plan)'
      },
      {
        defectId: 'DEF-002',
        summary: 'BOLA / IDOR in Client Parameter Extraction',
        severity: 'Critical',
        module: 'Meal Plan & Grocery APIs',
        steps: 'Query /api/meal-plan/current?user_id=2 while authenticated as User 1',
        expectedVsActual: 'Expected HTTP 403 Forbidden; Actual returns User 2 meal plan data',
        status: 'Open (Tracked in Test Plan)'
      },
      {
        defectId: 'DEF-003',
        summary: 'In-Memory Rate Limiting Thread Non-Sharing in Gunicorn',
        severity: 'Major',
        module: 'Backend Security',
        steps: 'Send rapid requests across multiple Gunicorn worker threads',
        expectedVsActual: 'Expected shared IP rate-limiting; Actual rate counters isolate per worker',
        status: 'Open (Tracked in Test Plan)'
      },
      {
        defectId: 'DEF-004',
        summary: 'Mobile Fallback Masks Backend Network Failures',
        severity: 'Major',
        module: 'Mobile App API Service',
        steps: 'Simulate API network dropout during recipe retrieval',
        expectedVsActual: 'Expected network error banner; Actual silently serves static recipes.json',
        status: 'Open (Tracked in Test Plan)'
      },
      {
        defectId: 'DEF-005',
        summary: 'Session Fixation on User Authentication',
        severity: 'Major',
        module: 'Authentication',
        steps: 'Log in with existing session cookie pre-assigned',
        expectedVsActual: 'Expected session ID regeneration; Actual retains pre-auth session ID',
        status: 'Open (Tracked in Test Plan)'
      },
      {
        defectId: 'DEF-006',
        summary: 'Missing Stable data-testid Attributes on Action Elements',
        severity: 'Minor',
        module: 'Web Frontend Templates',
        steps: 'Inspect Bootstrap buttons and tabs in index.html and meal_plan.html',
        expectedVsActual: 'Expected deterministic data-testid attributes; Actual uses volatile CSS classes',
        status: 'Open (Tracked in Test Plan)'
      }
    ];

    baselineDefects.forEach(def => {
      const row = sheet.addRow(def);
      row.alignment = { vertical: 'middle', wrapText: true };
      row.getCell('defectId').alignment = { horizontal: 'center' };
      row.getCell('severity').alignment = { horizontal: 'center' };
      row.getCell('status').alignment = { horizontal: 'center' };
    });
  }
}

module.exports = ExcelReporter;

