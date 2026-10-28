# Brief: Delay tool ignores the wait time the LLM asks for

When the Delay block is wired to an LLM block as a tool, it does not wait for the time the model asks for. The model sends the wait time, for example `10000` for 10 seconds, but Delay always waits for its own `delay_ms` setting, which defaults to 1 second. The model's value is passed through untouched.

| | |
|---|---|
| **Owner** | Harigovindan M G |
| **Signed off** | Pending |
| **Target branch** | `develop` in smartspace-sdk, on `fix/delay-ms-required` |
| **Scope** | Delay block in smartspace-sdk. Reaches dev through the ai-api SDK dependency. No admin UI or LLM block change. |

### Decisions governing this area

- **D1** - Delay 1.0.0 is not removed. Saved flows are pinned to it, and removing it would break them.
- **D2** - The fix is released as Delay 1.1.0. In 1.1.0, `delay_ms` is a required Config with no default, declared the same way other blocks declare their settings. The output pins do not change.

## What this is

The Delay block was built for pipelines: it waits for a set time, then passes its input on unchanged. Its wait time, `delay_ms`, is a design-time setting. Its only input, `data`, starts the step and is the value passed on.

Used as an LLM tool, the only thing the model sends is the wait time, and it lands on `data`. Delay never reads `data` as a wait time, so:

- **The model's wait time is ignored.** Delay waits for `delay_ms` (1 second unless set), whatever the model asks for.
- **A fixed `delay_ms` does not help.** Setting it to 10000 makes every call wait 10 seconds, but the model still cannot choose the time.
- **Making it work is unintuitive.** The model's value only takes effect if `delay_ms` is switched from fixed to dynamic and the same tool request is wired to both `data` and `delay_ms`.
- **There is no confirmation for the model.** Delay returns the model's own value, so a finished wait looks like a tool that did nothing. Without a confirmation, the model calls the tool over and over again, depending on the model. Today the flow designer has to add a String Template, such as "Waited {{output}}", to give the model that confirmation.

When this brief is done, Delay can no longer fall back to 1 second without anyone noticing. A flow designer has to set or wire `delay_ms`, and an LLM component has to send it.

### Terms used here

| Term | Meaning |
|---|---|
| **Tool** | A block wired to an LLM block so the model can call it. The model's request goes out on the tool's `request` pin and the block's result comes back on `return`. |
| **Component** | A block docked in the LLM block's Components slot. The model fills the block's inputs directly as named parameters, instead of sending one value on `request`. |
| **Tool request** | The value the model sends when it calls a tool. Here, the wait time in milliseconds. |
| **Fixed / dynamic** | A block setting is fixed when set at design time, and dynamic when it becomes an input pin that can be wired. |
| **Block version** | Each saved flow records the exact version of every block it uses, such as Delay 1.0.0, or a range such as `1.0.X`. Several versions of a block can exist side by side, and a flow keeps running the version it recorded. |

## Rules that are not choices

- **Existing Delay flows keep working.** Delay is used as a pass-through in pipelines, where returning the input unchanged is the point. Pipelines also pass numbers through Delay, so a number on `data` cannot simply be read as a wait time.
- **Delay 1.0.0 cannot be removed.** A saved flow only runs the exact version it recorded. Without 1.0.0, every flow that uses it would fail with "Could not find native block".
- **The new version is a minor bump, not a patch.** Flows saved with the range `1.0.X` pick up any new 1.0.x patch automatically. A 1.0.1 with a required `delay_ms` would break those flows, because they rely on the 1000 default.
- **The model decides the wait time.** A fix that only lets the flow designer set one fixed time does not solve the tool case.

## Reproduction

A test workspace on dev. The LLM block has two tools: Get Current State, and Delay with the description "send the number of milliseconds to this tool to delay for that long". Prompt: "What is the current status. delay response by 10 seconds". In every run the model sent `10000`.

| Setup | Model | Wait asked for | Wait per call | Delay calls |
|---|---|---|---|---|
| `delay_ms` fixed, not set (dev) | GPT 6-astra | 10 s | 1 s | 8 |
| `delay_ms` fixed, not set (local) | gpt-5.6-sol | 10 s | 1 s | 1 |
| `delay_ms` dynamic, request wired to `data` and `delay_ms` (dev) | GPT 6-astra | 10 s | 10 s | 8 |

With the default setup, the block waited 1 second on every call, on both models. The asked-for 10 seconds only happened once the request was wired to both pins.

Docking Delay 1.0.0 in the LLM block's Components slot does not help either. The component offers `delay_ms` to the model as an optional parameter, because it has a default of 1000. On dev the model left it unset, so Delay waited 1 second.

## The fix

Release Delay 1.1.0 next to an unchanged Delay 1.0.0, the way String Template (1.0.0, 2.0.0) and HTTP Request (1.0.0, 2.0.0) already keep older versions.

1. **`delay_ms` is required, with no default.** It can no longer fall back to 1 second. The designer flags it as missing until it is set or wired.
2. **`delay_ms` stays a Config.** Like other blocks' settings, it starts as fixed in the designer and can be switched to dynamic to wire it from a tool request. It keeps its value between messages.
3. **Output pins are unchanged.** Delay still forwards `data` unchanged after the wait.

As an LLM component, a required `delay_ms` becomes a required parameter, so the model has to send it. Checked against ai-api's `develop` code: Delay 1.0.0 requires only `data`, Delay 1.1.0 requires `data` and `delay_ms`.

As a tool, the request is still wired to both `delay_ms` and `data`, and a String Template is still needed to give the model a confirmation.

### Other options considered

- **Flow workaround with Delay 1.0.0.** Switch `delay_ms` to dynamic, wire the tool request to both pins, and add a String Template. Works today with no code change, but nothing stops a flow from silently waiting the 1 second default.
- **Release as 1.0.1.** Flows saved with `1.0.X` would move to it automatically and fail, because they rely on the default.

### Consequences

| | |
|---|---|
| **Changes** | Delay 1.1.0 appears in the block's version selector, and a Delay dragged onto a new flow gets 1.1.0. Its `delay_ms` has no default and must be set or wired. As a component, the model must send `delay_ms`. |
| **Stays the same** | Delay 1.0.0 and every saved flow that uses it, including flows pinned to `1.0.X`. Delay's output. The LLM block, and its `max_calls` and global tool call limits. |
| **Could be affected** | A flow switched from 1.0.0 to 1.1.0 by hand loses the 1000 default and has to set `delay_ms`. |

## Modification vs. extension

**Extension is enough.** A new version changes how `delay_ms` is declared without changing Delay 1.0.0, the LLM block or any saved flow.

## Known ambiguities / deliberately not in scope

Existing flows are not affected by Delay 1.1.0: they stay on Delay 1.0.0 and run as before.

- **Negative wait times.** A negative `delay_ms` is not rejected. Delay returns straight away and forwards `data` as if it had waited. Confirmed locally: `-1000` ran for about 0.02 seconds.
- **The String Template is still needed for tools.** Delay 1.1.0 still returns `data`, so the model gets no confirmation without one.
- **Components on dev.** The component check was run against ai-api's `develop` code. The local ai-api build is older and offers no Delay component at all, so this is confirmed on dev after release.
- **No automatic upgrade.** A flow that wants the new behaviour is switched from 1.0.0 to 1.1.0 by hand in the version selector.

## Owner's restatement

The owner's own words. This is the sign-off, and it is not edited.

- **What done means:** `Delay_1_1_0` is registered alongside Delay 1.0.0. Its `delay_ms` is declared `Config()` with no default, so the interface marks it required, with `config` metadata (fixed in the designer by default), and sticky. The `delay` step and the `output` pin are the same as 1.0.0.
- **What will be built first:** tests for 1.1.0's `delay_ms` interface (required, no default, Config, sticky), version resolution of `1.0.0`, `1.0.X` and `1.1.0`, and Delay 1.0.0's unchanged behaviour. Then `Delay_1_1_0`, and the SDK bump in ai-api.
- **What will NOT be built:** no change to Delay 1.0.0, no change to Delay's output, no negative-value check, and no change to the LLM block.
- **Edge cases that apply:** saved flows pinned to Delay 1.0.0 or `1.0.X` keep resolving to 1.0.0. A Delay 1.1.0 run without `delay_ms` fails rather than waiting a default time. A negative `delay_ms` returns straight away.

## Tasks

### 1. Release Delay 1.1.0

*smartspace-sdk*

Adds Delay 1.1.0 next to Delay 1.0.0, with `delay_ms` a required Config with no default. Delay 1.0.0 is not changed.

**After this merges:**

- Delay 1.1.0 can be selected in the designer, with `delay_ms` flagged until it is set or wired.
- `delay_ms` must be set or wired; there is no 1 second fallback.
- Saved flows on Delay 1.0.0 or `1.0.X` run exactly as before.

**Tests:**

- Delay 1.1.0 registers as "Delay", version 1.1.0.
- Delay 1.1.0's `delay_ms` is required, with no default.
- Delay 1.1.0's `delay_ms` is a Config (fixed by default) and is sticky.
- Delay 1.0.0's `delay_ms` keeps its 1000 default and stays fixed.
- Delay 1.1.0's output pins match Delay 1.0.0's.
- `1.0.0` and `1.0.X` resolve to Delay 1.0.0, and `1.1.0` resolves to Delay 1.1.0.
- Delay 1.1.0 waits for `delay_ms` and forwards `data` unchanged.
- Delay 1.1.0 without `delay_ms` fails rather than waiting a default time.
- Delay 1.0.0 still waits 1 second when `delay_ms` is unset.

### 2. Bump the SDK in ai-api

*Smartspace-ai-api*

Updates the smartspace-sdk reference in ai-api so Delay 1.1.0 is available on dev.

**After this merges:**

- Delay 1.1.0 shows up in the Delay version selector on dev.
- Docked as a component, Delay 1.1.0 makes the model send `delay_ms`.

## Results

Fix on `fix/delay-ms-required`. Verified on 2026-10-21:

| Check | Result |
|---|---|
| Delay unit tests | 10 of 10 pass |
| SDK test suite | 149 of 149 pass. Lint clean. |
| Component projection (ai-api `develop` code) | Delay 1.0.0 requires `data`; Delay 1.1.0 requires `data` and `delay_ms` |
| New Delay in the designer (local) | Version 1.1.0, `delay_ms` flagged until set or wired. Checked while `delay_ms` was declared dynamic; it is now a Config, which starts as fixed (unit tested) |
| Fixed and wired `delay_ms` (local) | Waits the set time; output unchanged |
| LLM tool, request wired to `delay_ms` and `data` (local) | Waits the time the model asks for |
| Existing flows on 1.0.0 and `1.0.X` (local) | Unchanged, still wait 1 second by default |
| Negative `delay_ms` (local) | Returns straight away (about 0.02 seconds), as noted under known ambiguities |
