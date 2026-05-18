# Simple Test Plan for TC06_Feeder_PlaceDoneSignal

## Goal
Run a minimal test of `TC06_Feeder_PlaceDoneSignal` without complex debug writes to verify that `q_bRunning` becomes TRUE.

## Steps

1. **Revert test file to minimal version**
   - Remove the added `WRITE` statement from `basic_test.scltest` (line ~47) so the file contains only the original test case code.
   - Keep only the `SET` statements and `ASSERT` for `q_bRunning`.

2. **Ensure FB_1004_GlueMachineFeeder_BufferFraming logic is correct**
   - Confirm that `bRunning := TRUE` is set when the start trigger occurs (already added).
   - Verify `T_MOVE_DEFAULT` timeout is set to a sufficient value (e.g., 20000 ms) to avoid premature timeout.

3. **Compile and download the PLC program**
   - Use the IDE’s **Rebuild** command to compile all `.scl` files.
   - Download the compiled program to the PLC or simulator.

4. **Execute the simplified test**
   - Run `basic_test.scltest` via the PLC test harness.
   - Observe whether the `ASSERT` passes (i.e., no runtime error reported).

5. **Validate result**
   - If the `ASSERT` passes, the test is successful.
   - If it fails, capture the error message and investigate which condition caused `q_bRunning` to remain FALSE.

6. **Document outcome**
   - Add a short entry to `PM_SESSION_DJ-2026-005.md` under `test_log` indicating success or the specific failure cause.
   - Update `fb_interfaces_and_documentation_improvement_plan.md` if any new insights about the trigger condition are discovered.

## Expected Result
After completing step 4, the test should complete without errors, confirming that `GlobalVars.stFeeder.q_bRunning` is correctly set to TRUE under the defined conditions.
