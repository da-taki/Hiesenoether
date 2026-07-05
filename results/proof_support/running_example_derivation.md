# Running Example Exact Derivation

This derivation uses exact rational arithmetic only. Fractions are written as integers or `p/q` strings.

## Initial Value

- Base: 10
- Access count: 0
- Drift state: 1
- Access entropy increment: 1/10
- Observation entropy increment: 1

## Operation Orders

- Order A: OBS, READ, READ
- Order B: READ, READ, OBS

## Body and Cap Outputs

| Order | Body read values | Body accumulator | Cap factor | Final output |
| --- | --- | --- | --- | --- |
| A | 10, 121/10 | 221/10 | 72/5 | 7956/25 |
| B | 10, 111/10 | 211/10 | 72/5 | 7596/25 |

Final divergence: `72/5`.

## Step Trace

### Order A

- Step 0 `INITIAL`: accumulator `0`
  - state `{'base': '10', 'access_count': 0, 'drift_state': '1'}`
- Step 1 `OBS`: accumulator `0`
  - state before `{'base': '10', 'access_count': 0, 'drift_state': '1'}`, state after `{'base': '10', 'access_count': 0, 'drift_state': '2'}`
- Step 2 `READ`: accumulator `10`
  - exposed `10`, drift `0`, state after `{'base': '10', 'access_count': 1, 'drift_state': '21/10'}`
- Step 3 `READ`: accumulator `221/10`
  - exposed `121/10`, drift `21/10`, state after `{'base': '10', 'access_count': 2, 'drift_state': '11/5'}`

Cap output: `7956/25`.

### Order B

- Step 0 `INITIAL`: accumulator `0`
  - state `{'base': '10', 'access_count': 0, 'drift_state': '1'}`
- Step 1 `READ`: accumulator `10`
  - exposed `10`, drift `0`, state after `{'base': '10', 'access_count': 1, 'drift_state': '11/10'}`
- Step 2 `READ`: accumulator `211/10`
  - exposed `111/10`, drift `11/10`, state after `{'base': '10', 'access_count': 2, 'drift_state': '6/5'}`
- Step 3 `OBS`: accumulator `211/10`
  - state before `{'base': '10', 'access_count': 2, 'drift_state': '6/5'}`, state after `{'base': '10', 'access_count': 2, 'drift_state': '11/5'}`

Cap output: `7596/25`.

## Paper Explanation

Both executions use the same multiset of operations. Placing OBS before the reads raises latent drift before the second body read, so order A has body accumulator 221/10 while order B has body accumulator 211/10. The compositional cap uses the same next-read factor 72/5 in both orders, producing final outputs 7956/25 and 7596/25 and exact divergence 72/5.
