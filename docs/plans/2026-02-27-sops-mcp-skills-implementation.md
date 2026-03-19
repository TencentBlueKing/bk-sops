# SOPS MCP Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create 4 AI Skills (SKILL.md) that guide AI assistants to correctly use SOPS MCP tools for operations users.

**Architecture:** Each Skill is a standalone SKILL.md file under `.cursor/skills/`. The base skill (`sops-mcp-basics`) provides foundational knowledge, and 3 scenario skills build on it. Each skill contains trigger conditions, MCP tool workflow, result presentation rules, and doc lookup guidance.

**Tech Stack:** Markdown (SKILL.md format), compatible with Cursor / CodeBuddy / Claude Code.

---

### Task 1: Create directory structure

**Files:**
- Create: `.cursor/skills/sops-mcp-basics/SKILL.md` (placeholder)
- Create: `.cursor/skills/sops-task-execution/SKILL.md` (placeholder)
- Create: `.cursor/skills/sops-task-monitoring/SKILL.md` (placeholder)
- Create: `.cursor/skills/sops-template-query/SKILL.md` (placeholder)

**Step 1: Create directories**

```bash
mkdir -p .cursor/skills/sops-mcp-basics
mkdir -p .cursor/skills/sops-task-execution
mkdir -p .cursor/skills/sops-task-monitoring
mkdir -p .cursor/skills/sops-template-query
```

**Step 2: Commit**

```bash
git add .cursor/skills/
git commit -m "chore: create SOPS MCP skills directory structure"
```

---

### Task 2: Write sops-mcp-basics SKILL.md

**Files:**
- Create: `.cursor/skills/sops-mcp-basics/SKILL.md`
- Reference: `docs/apidoc/zh_hans/*.md` (for API doc paths)

**Step 1: Write the SKILL.md**

The content should include:
- YAML front matter: name=sops-mcp-basics, description triggers on SOPS/标准运维 keywords
- MCP Server inventory:
  - 任务执行 MCP: create_task, get_task_detail, get_task_node_detail, get_task_status, start_task
  - 通用查询 MCP: get_task_detail, get_task_node_detail, get_task_status, get_template_info, get_template_list, get_task_list
- Common parameters: bk_biz_id (required), scope (cmdb_biz/project)
- Unified response format: result/data/message/trace_id
- MCP response filtering rules (per-API filtered fields, referencing docs)
- Error handling: check result → read message → use trace_id
- Doc lookup paths: `docs/apidoc/zh_hans/{api_name}.md`

**Step 2: Verify the SKILL.md**

- Validate YAML front matter syntax
- Confirm all MCP tool names match what user specified
- Confirm doc paths exist by checking `docs/apidoc/zh_hans/` directory

**Step 3: Commit**

```bash
git add .cursor/skills/sops-mcp-basics/SKILL.md
git commit -m "feat: add sops-mcp-basics skill with MCP server info and common patterns"
```

---

### Task 3: Write sops-task-execution SKILL.md

**Files:**
- Create: `.cursor/skills/sops-task-execution/SKILL.md`
- Reference: `docs/apidoc/zh_hans/create_task.md` (create_task params)
- Reference: `docs/apidoc/zh_hans/start_task.md` (start_task params)
- Reference: `docs/apidoc/zh_hans/get_template_info.md` (template constants structure)
- Reference: `docs/apidoc/zh_hans/get_task_status.md` (status check)

**Step 1: Write the SKILL.md**

The content should include:
- YAML front matter: triggers on "创建任务/执行任务/启动流程/跑模板"
- Prerequisites: user must provide or be asked for bk_biz_id
- 6-step workflow with MCP tool calls:
  1. get_template_list (name_keyword search)
  2. get_template_info (include_constants=true, note: MCP filters pipeline_tree)
  3. Present constants to user (show_type="show" variables, display name/desc/custom_type)
  4. create_task (template_id, name, constants with ${key} format)
  5. start_task (task_id from create_task response)
  6. get_task_status (confirm RUNNING)
- Key rules:
  - constants KEY must be ${key} format
  - constants VALUE type must match template definition
  - simplify_vars option for complex variable types
  - create_task only creates, does not execute
  - MCP create_task response excludes pipeline_tree
- Result presentation: show task_id, task_url, confirm started
- Error scenarios: template not found, parameter validation failure, permission denied

**Step 2: Validate against API docs**

Read `docs/apidoc/zh_hans/create_task.md` and `docs/apidoc/zh_hans/start_task.md` to confirm parameter names and workflow accuracy.

**Step 3: Commit**

```bash
git add .cursor/skills/sops-task-execution/SKILL.md
git commit -m "feat: add sops-task-execution skill for create-and-run workflow"
```

---

### Task 4: Write sops-task-monitoring SKILL.md

**Files:**
- Create: `.cursor/skills/sops-task-monitoring/SKILL.md`
- Reference: `docs/apidoc/zh_hans/get_task_status.md` (status and children structure)
- Reference: `docs/apidoc/zh_hans/get_task_detail.md` (task detail with outputs)
- Reference: `docs/apidoc/zh_hans/get_task_node_detail.md` (node inputs/outputs/ex_data)

**Step 1: Write the SKILL.md**

The content should include:
- YAML front matter: triggers on "查看任务状态/执行结果/排查失败/节点详情"
- Prerequisites: user must provide task_id and bk_biz_id
- 5-step workflow:
  1. get_task_status (with_ex_data=true)
  2. Interpret state: CREATED/RUNNING/FAILED/SUSPENDED/REVOKED/FINISHED
  3. If FAILED: recursively find FAILED nodes in children
  4. get_task_node_detail (task_id + node_id) for failed nodes
  5. Present analysis: node name, error reason (ex_data), inputs, suggested action
- Key rules:
  - children is nested dict-of-dict, must recurse to find all FAILED nodes
  - ex_data can be JSON string, HTML string, or plain string
  - MCP get_task_node_detail excludes histories
  - State flow: CREATED → RUNNING → FINISHED/FAILED, RUNNING ↔ SUSPENDED, any → REVOKED
- Result presentation format:
  - Success: task name, elapsed time, finish time
  - Running: current executing nodes
  - Failed: failed node name + error message + suggested action
- Common errors: timeout, permission denied, third-party API failure

**Step 2: Validate against API docs**

Read `docs/apidoc/zh_hans/get_task_status.md` and `docs/apidoc/zh_hans/get_task_node_detail.md` to confirm response structure accuracy.

**Step 3: Commit**

```bash
git add .cursor/skills/sops-task-monitoring/SKILL.md
git commit -m "feat: add sops-task-monitoring skill for status check and failure diagnosis"
```

---

### Task 5: Write sops-template-query SKILL.md

**Files:**
- Create: `.cursor/skills/sops-template-query/SKILL.md`
- Reference: `docs/apidoc/zh_hans/get_template_list.md` (list/search templates)
- Reference: `docs/apidoc/zh_hans/get_template_info.md` (template detail and constants)

**Step 1: Write the SKILL.md**

The content should include:
- YAML front matter: triggers on "查找模板/模板列表/模板参数/有哪些模板"
- Prerequisites: user must provide bk_biz_id
- 4-step workflow:
  1. get_template_list (name_keyword, template_source filter)
  2. Present template list as table: ID, name, category (Chinese), creator, edit_time
  3. get_template_info (on user request, include_constants=true)
  4. Present template detail: variables list with name/type/desc
- Key rules:
  - MCP get_template_list excludes auth_actions
  - MCP get_template_info excludes pipeline_tree
  - category mapping: OpsTools=运维工具, MonitorAlarm=监控告警, ConfManage=配置管理, DevTools=开发工具, EnterpriseIT=企业IT, OfficeApp=办公应用, Other=其它
  - template_source: business=业务流程, project=项目流程, common=公共流程
  - constants with show_type="show" are user-visible input parameters
- Result presentation:
  - Template list as markdown table
  - Template variables as structured list with name, type, description, default value

**Step 2: Validate against API docs**

Read `docs/apidoc/zh_hans/get_template_list.md` and `docs/apidoc/zh_hans/get_template_info.md` to confirm field mappings.

**Step 3: Commit**

```bash
git add .cursor/skills/sops-template-query/SKILL.md
git commit -m "feat: add sops-template-query skill for template search and inspection"
```

---

### Task 6: Final review and documentation

**Files:**
- Verify: `.cursor/skills/sops-*/SKILL.md` (all 4 files)
- Update: `docs/plans/2026-02-27-sops-mcp-skills-design.md` (mark as implemented)

**Step 1: Cross-skill consistency check**

- Verify MCP tool names are consistent across all skills
- Verify doc paths referenced in skills actually exist
- Verify no contradictions between skills

**Step 2: Final commit**

```bash
git add .
git commit -m "docs: finalize SOPS MCP skills implementation"
```
