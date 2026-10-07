# Brief : Step pin names colliding with BlockFunction's own attributes

A step whose input or output pin shares a name with one of the step object's own attributes overwrites that attribute. When the pin is `name` and the step returns a value, the step runs correctly and then fails to report its result, surfacing as an HTTP 500.


**Owner:** Harigovindan M G.
**Signed off:** pending.
**Target branch:** `develop` in `smartspace-sdk`, then a version bump in `Smartspace-ai-api`. `Smartspace-app` is not touched.

**Decisions governing this area:**
**D1** step and callback ports never have pin attributes set on them; their inputs travel only through `_pending_inputs`.
**D2** `Step` and `Callback` are treated the same, because they share the code path and the problem.
**D3** `Tool` ports and plain port classes keep their pin seeding exactly as it is.
**D4** rejecting reserved names at registration time is a separate, later safeguard, not part of this fix.
**D5** the fix is made once in the SDK.

> **One assumption still unconfirmed.** No custom block sends through a step's own output pin, for example `@step(output_name="result")` followed by `self.echo.result.send(x)`. That `Output` object exists only because of the seeding this fix removes, so after the fix it raises `AttributeError`. Block-level outputs such as `self.guid.send(...)` are not affected. Nothing in the SDK or `Smartspace-ai-api` uses the pattern. The published custom blocks need checking before the SDK version is bumped. If any does, stop and report.

## What this is

A block author writes a step, which is a method on the block marked `@step`. The SDK wraps that method in a `Step` object, and the object keeps a few facts about itself. The one that matters most is its `name`, for example `"echo"`, which is used at the very end to label the step's result so the engine knows which wire to send it down.

While a block is being built, the SDK prepares every pin on every port by writing a placeholder onto the port's object. For a step, that object is the `Step` itself. So a step input called `name` writes `None` over the step's own name. The step still receives its real input through a separate route and does its work correctly, but when it comes to labelling the result, the label is `None`, the label is rejected, and the result is discarded. This only happens when the step returns a value, because only then is the result labelled. Steps that emit through block-level outputs instead (`self.chunks.send(...)`) still have their name overwritten, but nothing reads it. The caller sees a 500 for work that actually succeeded. In the case where this was first found, a record had already been written to an external system by then, so the caller was told a write had failed when it had gone through.

When this brief is done, any step or callback can use any input or output name, steps with no inputs and no output name run normally, and nothing else about how blocks are built or run changes.

**Terms used here.**

| Term | Meaning |
|---|---|
| **Block** | One box in the Workflow Designer, for example the LLM block. |
| **Step** | The function inside a block that does the work, a method marked `@step`. |
| **Callback** | The other kind of block function, marked `@callback`. It shares the step's code path. |
| **Port** | A named connection point on a block. A step is one port and a config setting is another. |
| **Pin** | A single socket on a port that a wire attaches to. A step has one input pin per parameter and one output pin for its result. |
| **Wire address** | Where a wire starts or ends, written `block.port.pin`, for example `ReproPinNamed.echo.result`. |
| **Seeding** | `_create_port` writing a placeholder value onto a port object for each of its pins. |
| **Function port** | A port backed by a step or callback, marked `is_function` in the block interface. |


## Rules that are not choices

- **Seeding for `Tool` and plain ports does not change.** Those ports read their pins as attributes, and a pin that was never given a value has to read as `None` rather than raise `AttributeError`. `LLMTool.create_tool()` reading `self.schema` and `self.description` is the live example.
- **Argument delivery does not change.** `_set_inputs` fills `_pending_inputs` and `_run` reads from it. That is the only route a step's arguments take, and the fix does not touch it.
- **Output labelling and routing do not change** beyond no longer failing. The result is still labelled `BlockPinRef(port=self.name, pin=self._output_name)`.
- **The block interface does not change.** Ports and pins are built from the class definition before `_create_port` runs, so the Designer sees exactly the same blocks.
- **The object put back for a function port is the same instance that was already on the block.** Nothing is copied or replaced.
- **Steps and callbacks get the same treatment.** No branch that handles one and not the other.

## Source of the bug

`smartspace/core.py`, `Block._create_port`.

### How a step is built and run

1. **The block is created.** The flow engine (`run_step_inner` in `Smartspace-ai-api/app/flows/flow_run.py`) calls `injector.create_object(block_type)`, which runs `Block.__init__`.
2. **The step gets its own attributes.** `Block.__init__` copies each class level `Step` onto the instance with `attribute.create(self)`. The copy's constructor sets `name`, `_fn`, `_output_name`, `metadata`, `_block` and `_pending_inputs`.
3. **Ports are created.** `Block.__init__` calls `_create_all_ports`, which calls `_create_port` once per port and stores what it returns on the block.
4. **Pins are seeded.** For a port with named pins, `_create_port` fetches or builds the port object and runs `setattr(port, pin_name, value)` for every input (a default, usually `None`) and every output (an `Output` object). For a function port, the object is the `Step` itself.
5. **Inputs are delivered.** The engine calls `_load`, and `_set_inputs` stores each value for a function port in `step._pending_inputs[pin][index]`. Values for plain ports are set as attributes on the block.
6. **The step runs.** `_run_function` calls `_run`, which reads the function signature and takes each argument out of `_pending_inputs`. `_call_inner` wraps the call, and the engine's `async for m in block_run` runs it.
7. **The result is labelled.** After the user's function returns, `_inner` builds `OutputValue(source=BlockPinRef(port=self.name, pin=self._output_name), value=result)`.

The bug is step 4 writing onto the `Step`. The SDK never reads a step's pins back as attributes, because inputs come from `_pending_inputs` (step 6) and the output is labelled from `name` and `_output_name` (step 7). So seeding a function port does nothing useful, and any pin whose name matches one of the attributes from step 2 overwrites it. The one seeded value block code could use is the `Output` set on a step's own output pin, covered under consequences.

### What each colliding name does

| Pin name | Effect | Breaks when |
|---|---|---|
| `name` | step 7 builds `BlockPinRef(port=None, ...)`, which Pydantic rejects | the step also returns a value |
| `_output_name` | step 7 builds `BlockPinRef(..., pin=None)`, rejected the same way | the step also returns a value |
| `_pending_inputs` | the input store becomes `None`, so step 5 raises `TypeError` | always |
| `_fn` | the user's function becomes `None`, so step 6 raises `TypeError` | always |
| `_block` | the step loses its block, so `_call_inner` raises `AttributeError` before running | always |
| `metadata` | becomes `None`. Nothing reads it at run time today, but it is still wrong | never at run time today |

This is not limited to custom blocks. Two native blocks already have a `name` input: `sentence_chunk` (`sentence_chunk_1_0_0.py:47`) and `generate` (`guid_generator_v5.py:38`). Their `step.name` is overwritten today, to `""` and `None` respectively. They work only because neither step has a return annotation, so nothing is labelled at the end. The real trigger is a colliding pin name plus a step that returns a value.

Output pins collide the same way. `@step(output_name="name")` replaces `step.name` with an `Output` object, and step 7 fails.

Callbacks go through the same branch of `_create_port`. A callback input named `name` replaces `callback.name`, which is used when a `CallbackCall` is built, and one named `_pending_inputs` breaks input delivery for the callback.

The error a caller sees for `name`:

```
1 validation error for BlockPinRef
port
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

`run_step_inner` catches it. A `ValidationError` has no status code of its own, so the engine gives it the default code 500 and sends it out of the block's `error` port.

### A related case: steps with no inputs

Near the top of `_create_port` there is a shortcut for ports that have exactly one pin, where that pin is unnamed (`""`). It returns the value itself instead of an object, which is right for a plain config value such as `prefix` or a plain output such as `error`.

A step with no parameters and no `output_name` also has exactly one unnamed pin, its output, so the shortcut catches it. `_create_port` returns a bare `Output`, `_create_all_ports` stores that on the block in place of the step, and `_run_function` later fails with `'run' is not a BlockFunction`. Native blocks have not hit this because every native step without inputs sets an `output_name`. A custom block written the obvious way would.

### How it was reproduced

A flow in the local workspace wires three blocks in a line:

| From | To |
|---|---|
| `StringConst.build.output` (`"Hi"`) | `LLM.chat.message` |
| `LLM.response` | `ReproPinNamed.echo.name` |
| `ReproPinNamed.echo.result` | `Response` |

`ReproPinNamed` is a custom block with a `prefix` config (default `"echoed"`) and one step, `echo(self, name: str)`, with `output_name="result"`. `ReproPinLabelled` is identical except that its input is called `label`. `ReproPinLabelled` always returns. `ReproPinNamed` always fails with the error above.


## The fix

Return early from `_create_port` for function ports, before the single pin shortcut and before any seeding:

```python
port_interface = self.interface().ports[port_name]

# Step and Callback receive inputs via _pending_inputs and emit their return
# value directly, so no pin attributes are set on them
if port_interface.is_function:
    return getattr(self, port_name)
```

The branch further down that fetches the function port (`if port_interface.is_function: port = getattr(self, port_name)`) can no longer be reached and is removed, leaving only the code that builds `Tool` and plain port objects.

**Why not something narrower.**

- **Skipping only the input loop** fixes input pins, but not output pins named after an attribute, and not the no-input step caught by the shortcut. All three have the same cause, and one early return covers them.
- **Renaming `BlockFunction`'s attributes**, for example `name` to `_function_name`, only moves the collision to the new names, and all six would need renaming together.

**Consequences.**

|                       |                                                                                                                                                                                                                     |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Changes**           | Step and callback objects never get pin attributes, so their own attributes always hold the values set in their constructors. Steps with no inputs and no `output_name` stay steps and can be run.                  |
| **Stays the same**    | Argument delivery through `_pending_inputs`. Output labelling and routing. Seeding for `Tool` ports and plain port classes. The block interface the Designer reads.                                                 |
| **Could be affected** | Custom blocks that send through a step's own output pin (`self.<step>.<output_name>.send(...)`). The seeded `Output` that made this work is no longer created, so it raises `AttributeError`. Not used in the SDK or `Smartspace-ai-api`. Block-level outputs are unaffected. |

## Modification vs. extension

**Modification is required.** `_create_port` is a private method on `Block` that runs inside `__init__`, before any subclass code. There is no hook for a block author or a consuming service to skip it for function ports.

Working around it outside the SDK was considered and rejected (D5). Subclassing `Block` or patching `BlockFunction` would depend on private internals, would have to be repeated in every codebase that uses the SDK, and would not help authors who install the published SDK directly.

## Known ambiguities / deliberately not in scope

- **Does any custom block send through a step's own output pin?** Not found in the SDK or `Smartspace-ai-api`. The published custom blocks are searched for `self.<step>.<output_name>.send(` before the SDK version is bumped (task 2). **If any is found, stop and report.**
- **Authors can still choose these names.** With the fix the names are harmless, so this is no longer a correctness problem. A registration time check that rejects pin names matching `BlockFunction` attributes, with a clear message to the author, is still worth having as a guard against those attributes being read in a new way later (D4).
- **Future attributes.** If `BlockFunction` gains new attributes, the fix already protects them, because function ports have no pin attributes set at all. This is one reason it is preferred over renaming.
- **Designer validation is unrelated.** The Workflow Designer's pre-run checks (`node-readiness.ts` in `Smartspace-app`) work on the flow definition, not the running block object. They are a separate safety net and need no change.

## Owner's restatement

The owner's own words. This is the sign-off, and it is not edited.

- **What done means:** a custom block can name its step inputs or outputs anything, including `name`, and the step runs and its result reaches the next block instead of failing with the BlockPinRef error and a 500. The same goes for callbacks, and for a step that has no inputs and no output name. The fix is in the SDK and ai-api is running that SDK version, so it actually works on dev and not just in the SDK tests.
- **What I will build first:** the fix in `_create_port` in the SDK so it returns straight away for steps and callbacks, with a test for each case: an input named `name`, `output_name="name"`, a callback input named `name`, and a step with no inputs. Each one fails on develop and passes with the fix. Plus a test showing the native blocks that already have a `name` input behave the same. After that is merged, the one line version bump in ai-api.
- **What I will NOT build:** the check that stops block authors using these names when a block is registered. That is a separate PR. No changes to the Designer, and no changes to how the engine reports errors from blocks.
- **Edge cases that apply:** custom blocks that send through their step's own output pin, like `self.echo.result.send(x)`. That stops working after the fix, so the published custom blocks have to be checked before the bump. The two native blocks with a `name` input, `sentence_chunk` and `guid_generator_v5`, have to keep producing exactly the same output. And blocks that were already failing with this error will start succeeding, but anything they wrote before failing, and any duplicates from callers retrying, stays as it is.

## Tasks (each is one PR)

**In execution order.** The SDK ships before the ai-api bump. Hours are build time, AI assisted.

1. **Function ports skip pin handling in `_create_port`** *(smartspace-sdk · ~2 h)*. Returns early from `Block._create_port` for step and callback ports, before the single pin shortcut and before any seeding, and removes the function port branch that can no longer be reached.
   **After this merges:** a step or callback with any input or output name keeps its own attributes and labels its result with its own name; a step with no inputs and no `output_name` runs; `Tool` and plain port pins are seeded exactly as before.
   **Tests:** one per collision case, each failing on `develop` and passing with the fix: a step input named `name` on a step that returns a value; `@step(output_name="name")`; a callback input named `name`; a step with no inputs and no `output_name`. One confirming the native `name` input steps behave the same: a block shaped like `sentence_chunk` and `guid_generator_v5` (a `name` input, no return annotation, emitting through a block-level `Output`) sends the same output as before. A `Tool` config pin and a plain port config pin with no default still read `None`. The existing suite passes unchanged.

2. **Bump the SDK in `Smartspace-ai-api`** *(Smartspace-ai-api · ~1 h)*. Points `poetry.lock` at the SDK commit from task 1. Before that, the published custom blocks are checked for the one pattern the fix breaks: a step's own output pin used directly, for example `self.echo.result.send(x)`.
   **After this merges:** `ReproPinNamed` runs on dev and its result reaches `Response`; `sentence_chunk` and `guid_generator_v5` produce the same output as before.
   **Tests:** the native block suite, including `sentence_chunk` and `guid_generator_v5`, and the `LLM` block's `tools` port.






