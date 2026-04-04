# Attention List — Phase 1 Review Notes

> Generated during Phase 1 verification of Lentera MD.
> Each item below requires attention in a future phase.

---

## 1. Edit Menu: Undo / Redo
**Location:** `src/legal_md_converter/ui/main_window.py` — `_create_menu_bar()`  
**Status:** Edit menu exists with Select All and Clear, but **Undo/Redo is not implemented**.  
**Reason:** Requires document state management (command pattern or state stack).  
**Action Needed (Phase 2):**
- Implement a command stack or state snapshot system
- Add `QAction` for Undo (`Ctrl+Z`) and Redo (`Ctrl+Shift+Z` / `Ctrl+Y`)
- Connect to document content change signals
- Ensure undo history is bounded to prevent memory leaks

---

## 2. Spellcheck Error Highlighting in DocumentPreview
**Location:** `src/legal_md_converter/ui/widgets/document_preview.py`  
**Status:** The widget can display markdown, but **does not highlight spelling errors inline**.  
**Reason:** Error highlighting is implemented in the enhanced `PreviewWidget` instead.  
**Action Needed (Phase 3):**
- Decide whether `DocumentPreview` or `PreviewWidget` should be the primary preview component
- Integrate `SpellCheckEngine.get_error_positions()` into the chosen widget
- Use `QTextCharFormat` with red underline for typo positions
- Handle overlapping ranges correctly

---

## 3. Search Within Document (Ctrl+F)
**Location:** `src/legal_md_converter/ui/widgets/document_preview.py`  
**Status:** Search is **not implemented** in `DocumentPreview`. It exists in `PreviewWidget`.  
**Reason:** Two separate preview widgets were created; `PreviewWidget` has the enhanced features.  
**Action Needed (Phase 2):**
- Either migrate search functionality into `DocumentPreview`, or
- Replace `DocumentPreview` usage in `MainWindow` with `PreviewWidget`
- Ensure `Ctrl+F` toggle, find next/previous, and highlight-all work correctly

---

## 4. Thread Worker Cancel Support
**Location:** `src/legal_md_converter/utils/thread_worker.py`  
**Status:** Generic `Worker` and `BatchWorker` have **no built-in cancel mechanism**.  
**Reason:** Cancel logic is implemented in `DocumentParserWorker` but not in the base classes.  
**Action Needed (Phase 2):**
- Add `QMutex` or `QAtomicInt` based cancellation flag to `WorkerSignals`
- Implement `cancel()` method on base `Worker` class
- Ensure worker functions check cancellation periodically
- Test that cancellation cleans up resources properly

---

## 5. Error Messages — Indonesian Language Consistency
**Location:** Throughout the codebase  
**Status:** **Mixed language** — `SpellCheckPanel` and `ExportDialog` use Indonesian labels; other components use English.  
**Reason:** No centralized i18n/l10n strategy yet.  
**Action Needed (Phase 4):**
- Decide on primary UI language (recommend Indonesian with English fallback)
- Create a translation string table or use `QTranslator`
- Audit all user-facing strings: menus, dialogs, status bar, message boxes
- Ensure error messages are friendly and actionable in the chosen language

---

## 6. Missing Explicit Tests
**Location:** `tests/test_ui.py`  
**Status:** 9 tests exist covering widget creation, file operations, and theme. **Missing tests for:**
- Menu shortcut definitions
- High-DPI scaling verification
- Drag & drop event handling (actual Qt event testing)
- `ProgressDialog` behavior
- `SpellCheckPanel` interactions
- `ExportDialog` configuration output
- `DocumentParserWorker` thread behavior
- `DocumentService` orchestration

**Action Needed (Phase 2+):**
- Add `qtbot`-based tests for event handling
- Test signal/slot connections
- Mock parser responses for engine tests
- Add integration tests for full workflow (load → parse → convert → export)

---

## Summary Matrix

| # | Item | Priority | Target Phase | Effort |
|---|------|----------|--------------|--------|
| 1 | Undo/Redo | Medium | Phase 2 | Medium |
| 2 | Spellcheck highlighting | High | Phase 3 | Medium |
| 3 | Search (Ctrl+F) integration | High | Phase 2 | Low |
| 4 | Thread cancel support | Medium | Phase 2 | Low |
| 5 | Language consistency | Low | Phase 4 | Medium |
| 6 | Missing tests | High | Phase 2+ | High |

---

*This document should be reviewed at the start of each subsequent phase.*
