import { formatQDate, formatJobStatusString } from "./htcondor";

test("formatQDate converts seconds to ISO timestamp", () => {
  expect(formatQDate(1234)).toMatch(/1969-12-31T17:20:34.000-07:00 (.* ago)/);
});

describe("formatJobStatusString", () => {
  it.each([
    [1, "Idle"],
    [2, "Running"],
    [3, "Removed"],
    [4, "Completed"],
    [5, "Held"],
    [6, "Transferring Output"],
    [7, "Suspended"],
  ])("input is %d returns %s", (number, expected) => {
    expect(formatJobStatusString(number)).toBe(expected);
  });
});
