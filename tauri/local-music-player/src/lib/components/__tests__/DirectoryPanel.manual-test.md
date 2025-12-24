# DirectoryPanel Component Manual Test Checklist

This document provides a manual testing checklist for the DirectoryPanel component since automated tests are currently having configuration issues.

## Test Setup

1. Start the development server: `bun run dev`
2. Open the application in a browser
3. The DirectoryPanel component should be visible on the main page

## Test Cases

### ✅ Basic Rendering
- [ ] Component renders with "Music Directories" title
- [ ] "+" button is visible and clickable
- [ ] Directory list area is visible
- [ ] Empty state message appears when no directories are added

### ✅ Adding Directories
- [ ] Click the "+" button opens a folder selection dialog
- [ ] Selecting a folder adds it to the directory list
- [ ] Directory appears with correct name and path
- [ ] Canceling the dialog doesn't add anything
- [ ] Button shows loading spinner while processing
- [ ] Button is disabled during loading

### ✅ Directory Display
- [ ] Directory name is displayed correctly
- [ ] Directory path is shown below the name
- [ ] Path is shown in title attribute on hover
- [ ] Long paths are truncated with ellipsis
- [ ] Remove button (×) appears on hover

### ✅ Directory Selection
- [ ] Clicking a directory item selects it
- [ ] Selected directory is highlighted with different background
- [ ] Only one directory can be selected at a time
- [ ] Clicking the same directory again doesn't deselect it
- [ ] Keyboard navigation works (Tab to focus, Enter/Space to select)

### ✅ Directory Removal
- [ ] Clicking the remove button (×) removes the directory
- [ ] Remove button click doesn't trigger directory selection
- [ ] Removing selected directory clears the selection
- [ ] Confirmation is not required (as per design)

### ✅ Error Handling
- [ ] API errors show error message at top of component
- [ ] Error message can be dismissed with × button
- [ ] Error message has red background and appropriate styling
- [ ] Multiple errors replace previous ones

### ✅ Loading States
- [ ] Loading prop shows "Loading directories..." message
- [ ] Add button shows spinner when adding directory
- [ ] Add button is disabled during loading
- [ ] Loading state prevents user interaction

### ✅ Accessibility
- [ ] Directory items have role="button"
- [ ] Directory items are keyboard focusable (tabindex="0")
- [ ] Buttons have appropriate title attributes
- [ ] Focus indicators are visible
- [ ] Screen reader friendly structure

### ✅ Responsive Design
- [ ] Component works on different screen sizes
- [ ] Text truncation works properly on narrow screens
- [ ] Buttons remain accessible on mobile
- [ ] Touch interactions work on mobile devices

### ✅ Edge Cases
- [ ] Empty directory name falls back to path segment
- [ ] Root path ("/") displays correctly
- [ ] Very long directory names are handled
- [ ] Special characters in paths are displayed correctly
- [ ] Duplicate directory paths are handled (should not add duplicates)

## Integration Tests

### ✅ Store Integration
- [ ] Adding directory updates the directories store
- [ ] Selecting directory updates selectedDirectory store
- [ ] Removing directory updates both stores appropriately
- [ ] Store changes reflect in component immediately

### ✅ Event Handling
- [ ] directoryAdd event is dispatched with correct data
- [ ] directorySelect event is dispatched with correct data
- [ ] directoryRemove event is dispatched with correct data
- [ ] error event is dispatched with correct message

## Performance Tests

### ✅ Large Lists
- [ ] Component handles 50+ directories smoothly
- [ ] Scrolling is smooth with many directories
- [ ] Selection remains responsive with large lists
- [ ] Memory usage is reasonable

## Browser Compatibility

### ✅ Modern Browsers
- [ ] Chrome/Chromium based browsers
- [ ] Firefox
- [ ] Safari (if on macOS)
- [ ] Edge

## Notes

- Record any issues found during testing
- Note any deviations from expected behavior
- Document any browser-specific issues
- Include screenshots for visual issues

## Test Results

Date: ___________
Tester: ___________
Browser: ___________
OS: ___________

Overall Result: [ ] PASS [ ] FAIL

Issues Found:
1. ___________
2. ___________
3. ___________

Additional Notes:
___________