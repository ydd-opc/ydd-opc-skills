# Feishu Bitable View Extension — Dev Notes

## Project Info

- App: `cli_aaa6a746f1b8dbe0` (袁兜兜的企业自建应用)
- BlockTypeID: `blk_6a2c1b5b50800beff548796d`
- Type: 数据表视图 (table view extension)
- Bitable: `https://scn06pieug78.feishu.cn/base/Q3Uqbucd9aawJosSSZocBKCpneh`
- Local path: `C:\Users\yuanjiafeng\my-app\table-view\`
- Stack: Vue 3 + Element Plus + Webpack 5

## Dev Workflow

```bash
cd C:\Users\yuanjiafeng\my-app\table-view

# 本地调试
npm run dev          # 启动 webpack-dev-server:8081
# 然后打开: https://...bitable_url...?debugPort=8081
# 在表格里点 "新建视图" → 底部 "本地开发组件" → 添加 blk_xxx

# 构建 + 上传
npm run build        # 输出到 dist/
npm run upload       # 输入版本号 (递增)，需要先 opdev login

# 发布
# 开发者后台 → 应用能力 → 数据表视图 → 选版本 → 保存
# 开发者后台 → 版本管理与发布 → 创建版本 → 发布
```

## Windows Issues & Fixes

### 1. WebpackBar breaks dev mode
`webpackbar` passes `name`, `color`, `reporters`, `reporter` options to webpack 5's ProgressPlugin, which doesn't support them. Error:
```
[webpack-cli] Invalid options object. Progress Plugin has been initialized...
```
**Fix:** Remove WebpackBar from dev plugins in `config/webpack.config.js`:
```js
// Before:
...(isDevelopment ? [new WebpackBar()] : [new MiniCssExtractPlugin()]),
// After:
...(isDevelopment ? [] : [new MiniCssExtractPlugin()]),
```

### 2. opdev CLI is a bash script
`node_modules/.bin/opdev` is a bash script (starts with `#!/bin/sh`). On Windows, use `opdev.cmd` instead.
```bash
# OK:
node_modules/.bin/opdev.cmd upload ./dist
# DON'T:
node node_modules/.bin/opdev  # fails - bash syntax
```

### 3. npm install corruption
The `@lark-opdev/cli` global install has package corruption issues on this machine (many "tarball seems to be corrupted" warnings). This is persistent across install attempts. The local project `npm install` works fine.

### 4. Interactive prompts don't work with pipe
`opdev upload` uses interactive `inquirer` prompts. Piping input (`echo "1.0.0" | opdev upload`) reads one char at a time and still hangs on second prompt. Workaround: run interactively in terminal.

## SDK API Reference

```javascript
import { bitable } from '@lark-opdev/block-bitable-api';

// Selection: which table/view the user is looking at
const sel = await bitable.base.getSelection();
// Returns: {tableId: "tbl_xxx", viewId: "vew_xxx", ...}

// Get table reference
const table = await bitable.base.getTableById(sel.tableId);

// Read field metadata
const fields = await table.getFieldMetaList();
// Returns: [{id: "fld_xxx", name: "任务名称", type: 1, property: {...}}, ...]
// Field types: 1=text, 3=number, 7=select, 15=checkbox, etc.

// Read records
const result = await table.getRecordList({pageSize: 200});
// Returns: {records: [{id: "rec_xxx", fields: {fld_xxx: "value"}}]}

// Select field values are objects: {text: "P0", id: "opt_xxx"}
// Checkbox values are boolean: true/false

// Write records
await table.addRecord({
    fields: {
        fld_xxx: "任务名称值",
        fld_yyy: true,  // checkbox
        fld_zzz: "P0",  // select - can use text directly
    }
});

await table.setRecord("rec_xxx", {
    fields: { fld_zzz: "已发布" }
});
```

## Key Differences from Feishu Open API

| | Bitable SDK (Plugin) | Feishu Open API |
|---|---|---|
| Auth | Inherits user's permission | Needs tenant_access_token |
| Blockable | Can be blocked by iframe CSP | No restrictions |
| Needs app scope | No (runs as user) | Yes (bitable:app) |
| Rate limits | Bound to user | Bound to app |
| Best for | Interactive UI, buttons | Automated cron jobs |

The plugin SDK is far easier to work with since it doesn't need API scopes. But it only works when the user has the bitable open in their browser. For automated/weekly tasks, prefer the Python webhook script (topic_picker.py).

## Plugin Structure

`App.vue` is a single-file component with:
- `<script setup>` — Composition API, all logic in one block
- `<template>` — Kanban board with columns, cards, buttons
- `<style scoped>` — Scoped CSS, Element Plus variable overrides

The webhook URL is hardcoded in the component (it's a webhook bot URL exposed to clients). This is acceptable because the webhook only allows POSTing to one specific group — it's a one-way firehose, not a secret key.

## Weekly Plan Generation Logic

```
generateWeeklyPlan():
  1. Calculate week label: "M/D-M/D" (Mon-Sun)
  2. Filter P0/P1 records → create copies with 周次=weekLabel, 是否完成=false
  3. Add placeholder: "小说：更新章节" (类别=小说章节)
  4. Add placeholder: "公众号：本周精选推送" (类别=公众号精选)
  5. Send card to Feishu webhook with:
     - Summary of generated tasks (count per category)
     - Button: "打开选题管线" (links to bitable)
```
