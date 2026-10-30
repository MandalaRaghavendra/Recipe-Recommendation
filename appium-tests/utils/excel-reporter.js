// excel-reporter.js - Enterprise multi-worksheet Excel report generator for Appium Android E2E
const ExcelJS = require('exceljs');
const path = require('path');
const fs = require('fs');
const testRegistry = require('./test-registry');
const config = require('../config/mobile-config');

class ExcelReporter {
  constructor(outputPath) {
    this.outputPath = outputPath || config.reportPath;
  }

  async generateReport(executionStats = {}) {
    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'Tastio Senior Mobile QA Automation Engineer';
    workbook.lastModifiedBy = 'Tastio Appium Android E2E Harness';
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
    console.log(`[ExcelReporter] Master Appium test report successfully written to: ${this.outputPath}`);
    return this.outputPath;
  }

  buildSummarySheet(workbook, summary, executionStats) {
    const sheet = workbook.addWorksheet('Test Summary', {
      views: [{ showGridLines: true }]
    });

    // Title Banner
    sheet.mergeCells('A1:G2');
    const titleCell = sheet.getCell('A1');
    titleCell.value = 'TASTIO ANDROID MOBILE APPLICATION - APPIUM E2E TEST REPORT';
    titleCell.font = { name: 'Calibri', size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
    titleCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF00A388' } }; // Tastio Teal Theme
    titleCell.alignment = { vertical: 'middle', horizontal: 'center' };

    // Metadata section
    sheet.getCell('A4').value = 'Target Package:';
    sheet.getCell('B4').value = 'com.mandalaraghavendra.tastio (MainActivity)';
    sheet.getCell('A5').value = 'Automation Framework:';
    sheet.getCell('B5').value = 'Appium 2.x + UiAutomator2 + Mocha BDD + Chai';
    sheet.getCell('A6').value = 'Target Environment:';
    sheet.getCell('B6').value = `${config.capabilities['appium:deviceName']} (Android ${config.capabilities['appium:platformVersion']})`;
    sheet.getCell('A7').value = 'Report Generation Date:';
    sheet.getCell('B7').value = new Date().toLocaleString();

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
      sheet.getCell(`E${row}`).value = m[1];
      sheet.getCell(`D${row}`).font = { bold: true };
      sheet.getCell(`E${row}`).font = { bold: true, color: { argb: m[2] } };
      sheet.getCell(`D${row}`).border = {
        top: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        bottom: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        left: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        right: { style: 'thin', color: { argb: 'FFE2E8F0' } }
      };
      sheet.getCell(`E${row}`).border = {
        top: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        bottom: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        left: { style: 'thin', color: { argb: 'FFE2E8F0' } },
        right: { style: 'thin', color: { argb: 'FFE2E8F0' } }
      };
    });

    sheet.columns = [
      { width: 25 },
      { width: 45 },
      { width: 5 },
      { width: 25 },
      { width: 25 },
      { width: 10 },
      { width: 10 }
    ];
  }

  buildDetailsSheet(workbook, testCases) {
    const sheet = workbook.addWorksheet('Test Case Details', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const headers = [
      'Test ID', 'Module', 'Test Scenario', 'Preconditions', 'Test Steps',
      'Test Data', 'Expected Result', 'Actual Result', 'Status', 'Priority',
      'Severity', 'Execution Date', 'Defect Reference'
    ];

    const headerRow = sheet.addRow(headers);
    headerRow.font = { name: 'Calibri', bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF00A388' } };
    headerRow.height = 26;
    headerRow.alignment = { vertical: 'middle', horizontal: 'center' };

    testCases.forEach((tc) => {
      const row = sheet.addRow([
        tc.testId,
        tc.module,
        tc.testScenario,
        tc.preconditions,
        tc.testSteps,
        tc.testData,
        tc.expectedResult,
        tc.actualResult || 'Not Executed',
        tc.status || 'Not Executed',
        tc.priority,
        tc.severity,
        tc.executionDate || '',
        tc.defectReference || ''
      ]);

      const statusCell = row.getCell(9);
      if (tc.status === 'Passed') {
        statusCell.font = { bold: true, color: { argb: 'FF16A34A' } };
      } else if (tc.status === 'Failed') {
        statusCell.font = { bold: true, color: { argb: 'FFDC2626' } };
      } else if (tc.status === 'Blocked') {
        statusCell.font = { bold: true, color: { argb: 'FFD97706' } };
      } else {
        statusCell.font = { bold: false, color: { argb: 'FF64748B' } };
      }

      row.alignment = { vertical: 'middle' };
    });

    sheet.columns = [
      { width: 12 }, { width: 35 }, { width: 40 }, { width: 40 },
      { width: 45 }, { width: 30 }, { width: 45 }, { width: 40 },
      { width: 14 }, { width: 12 }, { width: 12 }, { width: 22 }, { width: 18 }
    ];
  }

  buildExecutionResultsSheet(workbook, executedCases) {
    const sheet = workbook.addWorksheet('Execution Results', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const headers = ['Test ID', 'Module', 'Test Scenario', 'Status', 'Actual Result', 'Execution Date', 'Defect Reference'];
    const headerRow = sheet.addRow(headers);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1E293B' } };
    headerRow.height = 24;

    if (executedCases.length === 0) {
      sheet.addRow(['MOB-INFO', 'Execution Environment', 'Appium & Android Emulator Probe', 'Not Executed', 'Test harness initialized. Awaiting emulator/device attachment before executing live native gestures.', new Date().toISOString(), '']);
    } else {
      executedCases.forEach(tc => {
        sheet.addRow([
          tc.testId,
          tc.module,
          tc.testScenario,
          tc.status,
          tc.actualResult,
          tc.executionDate,
          tc.defectReference
        ]);
      });
    }

    sheet.columns = [
      { width: 14 }, { width: 35 }, { width: 45 }, { width: 15 },
      { width: 45 }, { width: 25 }, { width: 20 }
    ];
  }

  buildFailedTestsSheet(workbook, failedCases) {
    const sheet = workbook.addWorksheet('Failed Tests', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const headers = ['Test ID', 'Module', 'Test Scenario', 'Failure Reason', 'Severity', 'Execution Date', 'Defect Reference'];
    const headerRow = sheet.addRow(headers);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFB91C1C' } };
    headerRow.height = 24;

    if (failedCases.length === 0) {
      sheet.addRow(['NONE', 'N/A', 'No failures recorded in this test execution', 'N/A', 'N/A', new Date().toISOString(), '']);
    } else {
      failedCases.forEach(tc => {
        sheet.addRow([
          tc.testId,
          tc.module,
          tc.testScenario,
          tc.actualResult,
          tc.severity,
          tc.executionDate,
          tc.defectReference
        ]);
      });
    }

    sheet.columns = [
      { width: 14 }, { width: 35 }, { width: 45 }, { width: 45 },
      { width: 15 }, { width: 25 }, { width: 20 }
    ];
  }

  buildDefectsSheet(workbook, failedCases) {
    const sheet = workbook.addWorksheet('Defects', {
      views: [{ showGridLines: true, state: 'frozen', ySplit: 1 }]
    });

    const headers = ['Defect ID', 'Associated Test ID', 'Module', 'Summary', 'Severity', 'Root Cause / Status', 'Resolution Steps'];
    const headerRow = sheet.addRow(headers);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF991B1B' } };
    headerRow.height = 24;

    // Known defects cataloged in TESTING-PLAN.md
    const knownDefects = [
      ['DEF-MOB-001', 'MOB-009', 'Offline Caching', 'Offline Cache Warning Stutter', 'Medium', 'Resolved', 'Fallback cache mechanism provides instant recipesData fallback in api.js'],
      ['DEF-MOB-002', 'MOB-031', 'Server Config', 'Hardcoded IP in Default Fallback', 'High', 'Resolved', 'Added dynamic server config modal and setCustomHostIp API'],
      ['DEF-MOB-003', 'MOB-266', 'Camera Vision', 'Physical Camera Unavailable in Headless Emulator', 'Medium', 'Documented', 'Synthetic dish image injection fixture implemented in test harness'],
      ['DEF-MOB-004', 'MOB-221', 'Grocery Compilation', 'Meal Plan Required Toast before Compilation', 'Normal', 'Audited', 'Friendly navigation dialog guides user to planner if plan is missing']
    ];

    knownDefects.forEach(d => sheet.addRow(d));

    sheet.columns = [
      { width: 16 }, { width: 20 }, { width: 25 }, { width: 45 },
      { width: 15 }, { width: 20 }, { width: 50 }
    ];
  }
}

module.exports = ExcelReporter;

