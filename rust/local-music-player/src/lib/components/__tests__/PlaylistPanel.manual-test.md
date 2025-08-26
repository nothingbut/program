# PlaylistPanel Component Manual Testing Guide

This document provides manual testing instructions for the PlaylistPanel component to verify all functionality works as expected.

## Test Setup

1. Ensure the application is running with `bun dev`
2. Have some MP3 files available in a test directory
3. Add the test directory using the DirectoryPanel component

## Test Cases

### 1. Component Rendering

#### 1.1 Empty State
- **Action**: Start the application without selecting any directory
- **Expected**: 
  - Playlist panel shows "No tracks found" message
  - Musical note icon (♪) is displayed
  - Helper text: "Select a directory with MP3 files to see your music here."
  - No track count is shown in the header

#### 1.2 Loading State
- **Action**: Select a directory with many MP3 files and observe during scanning
- **Expected**:
  - Loading spinner is displayed
  - "Loading tracks..." message appears
  - Playlist table is hidden during loading

#### 1.3 Populated State
- **Action**: Select a directory containing MP3 files
- **Expected**:
  - Header shows "Playlist" title
  - Track count displays correctly (e.g., "5 tracks" or "1 track")
  - Table headers are visible: #, Title, Artist, Album, Duration
  - All tracks are listed in the table

### 2. Track Display

#### 2.1 Complete Metadata
- **Action**: View tracks with complete ID3 tags
- **Expected**:
  - Track number displays correctly in # column
  - Title, Artist, Album show actual metadata values
  - Duration is formatted as MM:SS (e.g., "3:45")

#### 2.2 Missing Metadata
- **Action**: View tracks with incomplete or missing ID3 tags
- **Expected**:
  - Missing title shows as "Untitled"
  - Missing artist/album shows as "Unknown"
  - Missing track number shows as "-"
  - Duration still displays correctly

#### 2.3 Long Text Handling
- **Action**: View tracks with very long titles, artist names, or album names
- **Expected**:
  - Text is truncated with ellipsis (...)
  - Full text appears in tooltip on hover
  - Table layout remains intact

### 3. Track Selection

#### 3.1 Single Click Selection
- **Action**: Click once on any track row
- **Expected**:
  - Row becomes highlighted with blue background
  - Previously selected row (if any) is deselected
  - Only one row can be selected at a time

#### 3.2 Selection Persistence
- **Action**: Select a track, then scroll or interact with other UI elements
- **Expected**:
  - Selected track remains highlighted
  - Selection persists across UI interactions

#### 3.3 No Duplicate Selection
- **Action**: Click on an already selected track
- **Expected**:
  - Track remains selected (no visual change)
  - No additional events are triggered

### 4. Track Playback

#### 4.1 Double Click to Play
- **Action**: Double-click on any track row
- **Expected**:
  - Track selection changes to the double-clicked track
  - Play event is triggered (should integrate with player controls)
  - Visual feedback indicates the action was registered

#### 4.2 Play Different Track
- **Action**: Double-click on a different track while one is selected
- **Expected**:
  - Selection moves to the new track
  - Play event is triggered for the new track

### 5. Keyboard Navigation

#### 5.1 Tab Navigation
- **Action**: Use Tab key to navigate through track rows
- **Expected**:
  - Focus moves between track rows
  - Focused row has visible focus outline
  - Focus is contained within the playlist area

#### 5.2 Enter Key
- **Action**: Focus on a track row and press Enter
- **Expected**:
  - Track is selected and play event is triggered
  - Same behavior as double-click

#### 5.3 Space Key
- **Action**: Focus on a track row and press Space
- **Expected**:
  - Track is selected (but not played)
  - Same behavior as single click

#### 5.4 Arrow Keys (if implemented)
- **Action**: Use Up/Down arrow keys when focused on a track
- **Expected**:
  - Focus moves to previous/next track
  - Selection follows focus

### 6. Responsive Design

#### 6.1 Medium Screen (Tablet)
- **Action**: Resize window to ~1024px width
- **Expected**:
  - Album column is hidden
  - Artist column expands to fill space
  - All other columns remain visible

#### 6.2 Small Screen (Mobile)
- **Action**: Resize window to ~768px width
- **Expected**:
  - Header padding is reduced
  - Track row padding is reduced
  - Font sizes are slightly smaller
  - All essential columns still visible

#### 6.3 Very Small Screen
- **Action**: Resize window to ~480px width
- **Expected**:
  - Artist column is hidden
  - Title column expands significantly
  - Track number and duration columns are narrower
  - Layout remains functional

### 7. Accessibility

#### 7.1 Screen Reader Support
- **Action**: Use screen reader to navigate the component
- **Expected**:
  - Track rows are announced as buttons
  - Track information is read in logical order
  - Instructions are provided ("Click to select, double-click to play")

#### 7.2 High Contrast Mode
- **Action**: Enable high contrast mode in OS
- **Expected**:
  - All text remains readable
  - Selection highlighting is visible
  - Focus indicators are clear

#### 7.3 Keyboard-Only Navigation
- **Action**: Navigate using only keyboard (no mouse)
- **Expected**:
  - All interactive elements are reachable
  - Visual focus indicators are clear
  - All functionality is accessible

### 8. Error Handling

#### 8.1 Corrupted Files
- **Action**: Include corrupted or invalid MP3 files in directory
- **Expected**:
  - Valid files are displayed normally
  - Invalid files are either skipped or show with default metadata
  - No application crashes or errors

#### 8.2 Large Playlists
- **Action**: Load directory with 100+ MP3 files
- **Expected**:
  - All tracks load without performance issues
  - Scrolling is smooth
  - Selection and interaction remain responsive

#### 8.3 Special Characters
- **Action**: Test with files containing special characters in metadata
- **Expected**:
  - Special characters display correctly
  - Unicode characters are supported
  - No encoding issues

### 9. Performance

#### 9.1 Large Playlist Scrolling
- **Action**: Scroll through a playlist with 50+ tracks
- **Expected**:
  - Smooth scrolling performance
  - No lag or stuttering
  - Memory usage remains stable

#### 9.2 Rapid Interactions
- **Action**: Quickly click between different tracks
- **Expected**:
  - All clicks are registered
  - Selection updates smoothly
  - No visual glitches

## Integration Testing

### 10.1 Directory Change
- **Action**: Switch between different directories
- **Expected**:
  - Playlist updates to show new directory's tracks
  - Previous selection is cleared
  - Loading state is shown during transition

### 10.2 Player Integration
- **Action**: Double-click tracks and verify player controls update
- **Expected**:
  - Player controls show current track information
  - Play/pause state synchronizes
  - Progress updates reflect current track

## Bug Reporting

When reporting issues, please include:
- Browser/OS information
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Console errors (if any)

## Test Data Recommendations

For comprehensive testing, use a directory containing:
- Files with complete metadata
- Files with missing metadata
- Files with very long titles/artist names
- Files with special characters
- Mix of different durations (short and long tracks)
- At least 10-20 files for scrolling tests