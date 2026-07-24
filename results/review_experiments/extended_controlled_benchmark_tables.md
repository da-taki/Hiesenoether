# Extended Controlled Benchmark Tables

## Metrics

| metric | value |
| --- | --- |
| cases | 64 |
| new_cases_added | 44 |
| TP | 40 |
| FP | 9 |
| TN | 15 |
| FN | 0 |
| precision | 0.8163 |
| recall | 1.0 |
| specificity | 0.625 |
| F1 | 0.8989 |
| exact_label_accuracy | 0.8594 |

## Confusion Matrix

| expected | SAFE | LOW | MEDIUM | HIGH | MISSING |
| --- | --- | --- | --- | --- | --- |
| SAFE | 15 | 0 | 9 | 0 | 0 |
| LOW | 0 | 10 | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 14 | 0 | 0 |
| HIGH | 0 | 0 | 0 | 16 | 0 |

## Label Mismatches

| file | class | expected | observed | evidence |
| --- | --- | --- | --- | --- |
| analysis/benchmark_examples.py | FalsePositivePureCache | SAFE | MEDIUM | P1: method get() (line 112): mutates self.{cached} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | CachedHash | SAFE | MEDIUM | P1: method __hash__() (line 255): mutates self.{_hash} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | ConstantAfterMutationNearMiss | SAFE | MEDIUM | P1: method get() (line 335): mutates self.{calls} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | ContextManagerBookkeeping | SAFE | MEDIUM | P1: method __enter__() (line 272): mutates self.{depth} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | FluentSetter | SAFE | MEDIUM | P1: method set_name() (line 315): mutates self.{name} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | HarmlessMemoizedProperty | SAFE | MEDIUM | P1: method value() (line 246): mutates self.{_cached} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | MetricsCounterIndependent | SAFE | MEDIUM | P1: method get() (line 290): mutates self.{metric} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | StabilizingDescriptor | SAFE | MEDIUM | P1: method __get__() (line 348): mutates self.{cached} and returns a value derived from self state |
| benchmarks/controlled_extended/extended_examples.py | StableDescriptorCacheOnce | SAFE | MEDIUM | P1: method __get__() (line 298): mutates self.{cached} and returns a value derived from self state |
