# Brief: Delay tool ignores the wait time the LLM asks for

When the Delay block is wired to an LLM block as a tool, it does not wait for the time the model asks for. The model sends the wait time, for example `10000` for 10 seconds, but Delay always waits for its own `delay_ms` setting, which defaults to 1 second. The model's value is passed through untouched.

This is a working draft; the choice between the options is made at sign-off.

| | |
|---|---|
| **Owner** | Harigovindan M G |
| **Signed off** | Pending |
| **Target branch** | `develop` in smartspace-sdk (option B). Option A needs no code change. |
| **Scope** | Delay block in smartspace-sdk. Reaches dev through the ai-api SDK dependency. No admin UI or LLM block change. |

### Decisions governing this area

- **D1** - Delay 1.0.0 is not removed. Saved flows are pinned to it, and removing it would break them.
- **D2** - *Open.* How the wait time from the model reaches the block. See Options; the current leaning is option B, a new Delay version.
- **D3** - A negative wait time raises an error, instead of returning straight away and confirming a wait that never happened.
## What this is

The Delay block was built for pipelines: it waits for a set time, then passes its input on unchanged. Its wait time, `delay_ms`, is a design-time setting. Its only input, `data`, starts the step and is the value passed on.

Used as an LLM tool, the only thing the model sends is the wait time, and it lands on `data`. Delay never reads `data` as a wait time, so:

- **The model's wait time is ignored.** Delay waits for `delay_ms` (1 second unless set), whatever the model asks for.
- **A fixed `delay_ms` does not help.** Setting it to 10000 makes every call wait 10 seconds, but the model still cannot choose the time.
- **Making it work is unintuitive.** The model's value only takes effect if `delay_ms` is switched from fixed to dynamic and the same tool request is wired to both `data` and `delay_ms`.
- **There is no confirmation for the model.** Delay returns the model's own value, so a finished wait looks like a tool that did nothing. Without a confirmation, the model calls the tool over and over again, depending on the model. Today the flow designer has to add a String Template, such as "Waited {{output}}", to give the model that confirmation.

When this brief is done, a flow designer can give an LLM a delay tool with one wire and no String Template. The block waits for exactly the time the model asks for, and tells the model the wait is done.

### Terms used here

| Term | Meaning |
|---|---|
| **Tool** | A block wired to an LLM block so the model can call it. The model's request goes out on the tool's `request` pin and the block's result comes back on `return`. |
| **Tool request** | The value the model sends when it calls a tool. Here, the wait time in milliseconds. |
| **Fixed / dynamic** | A block setting is fixed when set at design time, and dynamic when it becomes an input pin that can be wired. |
| **Block version** | Each saved flow records the exact version of every block it uses, such as Delay 1.0.0. Several versions of a block can exist side by side, and a flow keeps running the version it recorded. |
| **`max_calls`** | How many times one tool can be called in one LLM block run. |

## Rules that are not choices

- **Existing Delay flows keep working.** Delay is used as a pass-through in pipelines, where returning the input unchanged is the point. Pipelines also pass numbers through Delay, so a number on `data` cannot simply be read as a wait time.
- **Delay 1.0.0 cannot be removed.** A saved flow only runs the exact version it recorded. Without 1.0.0, every flow that uses it would fail with "Could not find native block".
- **The model decides the wait time.** A fix that only lets the flow designer set one fixed time does not solve the tool case.

## Reproduction

A test workspace on dev. The LLM block has two tools: Get Current State, and Delay with the description "send the number of milliseconds to this tool to delay for that long". Prompt: "What is the current status. delay response by 10 seconds". In every run the model sent `10000`.

| Setup | Model | Wait asked for | Wait per call | Delay calls |
|---|---|---|---|---|
| `delay_ms` fixed, not set (dev) | GPT 6-astra | 10 s | 1 s | 8 |
| `delay_ms` fixed, not set (local) | gpt-5.6-sol | 10 s | 1 s | 1 |
| `delay_ms` dynamic, request wired to `data` and `delay_ms` (dev) | GPT 6-astra | 10 s | 10 s | 8 |

With the default setup, the block waited 1 second on every call, on both models. The asked-for 10 seconds only happened once the request was wired to both pins.

## Options

Option A can be used straight away while B is built.

| Option | Where | Model's wait time used | Wiring | String Template needed | Existing flows |
|---|---|---|---|---|---|
| **A.** Flow workaround with Delay 1.0.0 | Flow only | Yes | Two wires from one request | Yes | Unchanged |
| **B.** Delay 2.0.0 *(leaning)* | SDK | Yes | One wire | No | Unchanged |

### A. Flow workaround with Delay 1.0.0

Switch `delay_ms` to dynamic and wire the tool request to both `data` and `delay_ms`. Route the Delay output through a String Template, such as "Waited {{output}}", into the tool's `return`.

- Works today with no code change. On dev with GPT 6-astra, this setup waited the asked-for 10 seconds and the model called Delay once.
- Every flow designer has to know to wire the same value twice and add the String Template.

### B. New Delay version, 2.0.0

Release Delay 2.0.0 next to an unchanged Delay 1.0.0, the way String Template (1.0.0, 2.0.0) and HTTP Request (1.0.0, 2.0.0) already do.

- **One input.** `delay_ms` is the step's input. It starts the step and sets the wait time, so the tool needs one wire. Pipelines that need pass-through stay on 1.0.0.
- **What it returns.** Either the wait time it waited, such as `10000`, which is what led to repeat calls on GPT 6-astra; or a confirmation *(leaning)*, such as `{"waited_ms": 10000, "status": "complete"}`, which tells the model the wait finished. The String Template version of the confirmation stopped the repeat calls on dev.

**Sending other data with the wait time.** The tool's `schema` on the LLM block sets the shape of what the model sends. Today it is empty, so the model sends a bare value. An object schema lets the model send the wait time and other values in one call, for example:

```json
{
  "type": "object",
  "properties": {
    "delay_ms": { "type": "integer", "description": "How long to wait, in milliseconds" },
    "message": { "type": "string", "description": "Text to use after the wait" }
  },
  "required": ["delay_ms"]
}
```

The request then arrives as one object, so a Get block (path `$.delay_ms`) picks out the wait time for Delay 2.0.0, and other fields go wherever the flow needs them. When only the wait time is sent, a schema of `{"type": "integer"}` with a description is enough, and makes the model send a whole number of milliseconds.

A Delay dragged onto a new flow gets 2.0.0, because new blocks default to the latest version. Flows that already use Delay 1.0.0 as a tool are switched to 2.0.0 by hand in the version selector.

### Consequences of the leading option (B)

| | |
|---|---|
| **Changes** | Delay 2.0.0 appears in the block's version selector. Flow designers can give an LLM a delay tool with one wire and no String Template, and the block waits for the time the model asks for. A Delay dragged onto a new flow gets 2.0.0. |
| **Stays the same** | Delay 1.0.0 and every saved flow that uses it, including flows pinned to a `1.0.X` range. The LLM block, and the `max_calls` and global tool call limits. |
| **Could be affected** | A new pipeline flow that needs pass-through has to pick Delay 1.0.0 in the version selector, because new blocks default to 2.0.0. |

## Modification vs. extension

**Extension is enough.** The problem is how Delay behaves as a tool, not how it behaves in a pipeline. A new version lets the model's value set the wait time, without changing Delay 1.0.0, the LLM block or any saved flow.

Option A shows the block already waits correctly once the model's value reaches `delay_ms`. B makes that the default and removes the double wiring and the String Template.

## Known ambiguities / deliberately not in scope

Existing flows are not affected by Delay 2.0.0: they stay on Delay 1.0.0 and run as before. The points below concern Delay 2.0.0 only.

- **What the model sees when Delay 2.0.0 raises an error.** Under D3, a negative wait time raises an error. It is not yet confirmed whether that error reaches the model as a tool result it can act on, or fails the whole run. Checked before Task 1 is finished.
- **No automatic upgrade.** A flow that wants the new behaviour is switched from 1.0.0 to 2.0.0 by hand in the version selector. Flows are not moved automatically.

## Owner's restatement

The owner's own words. This is the sign-off, and it is not edited.

- **What done means:** Delay 2.0.0 is registered alongside Delay 1.0.0. Its single step input `delay_ms` triggers the step and sets the wait time, so an LLM tool's `request` pin wires to it directly. After the wait it returns a confirmation (`waited_ms`, `status: "complete"`) on `output`, which goes straight to the tool's `return` with no String Template. A negative `delay_ms` raises an error.
- **What will be built first:** a failing test on `develop` showing that a tool request on Delay 1.0.0's `data` does not set the wait time. Then `Delay_2_0_0` with its tests, a check of how an error raised inside a wired tool block reaches the LLM, and the SDK bump in ai-api.
- **What will NOT be built:** no change to Delay 1.0.0, no change to the LLM block or its `max_calls` and global tool call limits, and no pass-through `data` input on 2.0.0.
- **Edge cases that apply:** saved flows pinned to Delay 1.0.0 or `1.0.X` keep resolving to 1.0.0. New Delay blocks default to 2.0.0, so pipeline flows that need pass-through select 1.0.0 by hand. A negative wait time raises an error rather than returning straight away. An object tool schema needs a Get block (`$.delay_ms`) between the tool request and `delay_ms`.

## Tasks

Written for option B. Option A needs no tasks, only a flow change.

### 1. Release Delay 2.0.0

*smartspace-sdk*

Adds Delay 2.0.0 next to Delay 1.0.0. It has a single `delay_ms` input that starts the step and sets the wait time, and returns a confirmation after the wait. A negative `delay_ms` raises an error. Delay 1.0.0 is not changed.

**After this merges:**

- An LLM can be given a delay tool with one wire and no String Template.
- The block waits for the time the model asks for, and the model gets a clear confirmation.
- Saved flows on Delay 1.0.0 run exactly as before.

**Tests:**

- Delay 2.0.0 waits for the `delay_ms` it is given and returns a confirmation with the waited time.
- A negative `delay_ms` raises an error.
- Delay 2.0.0 wired as an LLM tool waits for the time in the tool request.
- Both versions are registered: a flow pinned to Delay 1.0.0 resolves to 1.0.0, and one pinned to 2.0.0 resolves to 2.0.0.
- Delay 1.0.0's existing behaviour is unchanged: it waits `delay_ms` and passes `data` on.

### 2. Bump the SDK in ai-api

*Smartspace-ai-api*

Updates the smartspace-sdk reference in ai-api so Delay 2.0.0 is available on dev.

**After this merges:**

- Delay 2.0.0 shows up in the Delay version selector on dev.
- Re-running the reproduction prompt with Delay 2.0.0 as the tool waits 10 seconds once, with one wire from the tool request and no String Template.
