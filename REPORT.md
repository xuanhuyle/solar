# t0-beta qualification: PASS

Model `theforecastingcompany/t0-beta` at revision `c8885416fab935d604749a90cdcbf9b54fffcaeb`; tfc-t0 0.5.0.

| file | sha256 |
|---|---|
| config.json | `bd0ef3c2b1c1a130e32a6ce6132d895297d3a42e1fa84ac2d516e794c5c881ff` |
| model.safetensors | `a0fd8abd51275dd30afd21f4892c763ebd45e2cb1811eff26eed43f89a543f7d` |

- **Q1** (a second load gives bit-identical forecasts on 16 requests) - pass
- **Q2** (1 and 2 covariate rows accepted, 24 values each) - pass
- **Q3** (finite, none sanitised, hourly sd > 0.05 for every forecast, {E} differs from {}): min hourly sd 0.1242, sanitised 0 - pass
- **Q4** (k = 7-13: pooled skill E vs none and E vs N each > 10%; E beats none in >= 6 of 8 worlds): E vs none +34.2%, E vs N +36.4%, E beats none in 8 of 8 worlds - pass

Reported only, k = 1-3: E vs none +15.7%, E vs N +15.1%, N vs none +0.7%; k = 7-13 N vs none -3.6%.

t0-beta forecasts: 274; elapsed 24.2 s.
