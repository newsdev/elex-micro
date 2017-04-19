#ELEX-MICRO
Everything you like about Elex, only less.

## What?
Elex-micro is a Python library for returning results, and only results, from the AP Election v2.0 API. It is related to, but conceptually distinct from, [Elex](https://github.com/newsdev/elex), a more fully-featured wrapper.

## Why?
At The New York Times, we need our results just a little bit faster. And by "a little bit" I mean "about twice as fast."

```
time elex results 2012-11-02 -d '/Users/jbowers/Desktop/general/20121106-national.json' > /tmp/test.csv

2016-08-19 11:58:29,120 (INFO) elex (v2.0.9) : Getting results for election 2012-11-06

real    0m10.245s
user    0m9.457s
sys     0m0.592s
```

```
time results -d ~/Desktop/general/20121106-national.json --csv > /tmp/test.csv

real    0m5.834s
user    0m5.255s
sys     0m0.515s
```

## How?
Elex-micro passes all of the same tests that Elex does; the test suite is actually ported over from Elex. The output that Elex-micro generates is identical to Elex for results data. However, it is not a perfect drop-in replacement for Elex. 

### Things Elex-micro does not do that Elex does
* Hit the API directly (we use `curl --compressed` and point Elex-micro to a local file)
* Snapshot files to a local folder or to MongoDB (we do with with `curl`)
* Return any other Elections objects except `CandidateReportingUnit` (we use Elex for initialization)
* Have a pluggable CLI architecture (we only need JSON and CSV)
